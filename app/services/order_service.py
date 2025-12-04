from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.models.order_model import (
    Order,
    OrderItem,
    OrderPayment,
    OrderEvent,
    OrderStatus,
    OrderChannel,
    PaymentStatus,
)
from app.schema.order_schema import (
    OrderCreate,
    OrderStatusEnum,
    OrderChannelEnum,
    PaymentStatusEnum,
    PaymentMethodEnum,
    OrderUpdate,
    OrderAddItems,
    OrderItemsChannelUpdate,
    OrderAddSingleItem,
    OrderItemQuantityUpdate,
    OrderBulkAddItems,
    OrderBulkUpdateItems,
    OrderItemUpsert,
    OrderAddPayment,
    OrderCancel,
    OrderItemCreate,
)


STATUS_FLOW = {
    OrderStatus.pending: [OrderStatus.accepted, OrderStatus.canceled],
    OrderStatus.accepted: [OrderStatus.preparing, OrderStatus.canceled],
    OrderStatus.preparing: [OrderStatus.ready, OrderStatus.canceled],
    OrderStatus.ready: [OrderStatus.completed, OrderStatus.canceled],
    OrderStatus.completed: [],
    OrderStatus.canceled: [],
}


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrderRepository(db)
        self.restaurant_repo = RestaurantRepository(db)

    def _dec(self, value) -> Decimal:
        return Decimal(str(value or 0))

    def _money(self, value) -> Decimal:
        return self._dec(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def _get_restaurant(self, restaurant_id: int):
        restaurant = await self.restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        return restaurant

    def _ensure_items_mutable(self, order: Order):
        if order.status not in (OrderStatus.pending, OrderStatus.accepted):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify items in current status")

    def _find_item(self, order: Order, item_id: int) -> OrderItem | None:
        return next((i for i in order.items if i.id == item_id), None)

    async def _get_order_for_update(self, order_id: int):
        order = await self.repo.get_order_for_update(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    async def _get_menu_lookup(self, restaurant_id: int, menu_ids: List[int]):
        if not menu_ids:
            return {}
        menu_models = await self.repo.get_menu_items(menu_ids)
        menu_map = {m.id: m for m in menu_models}
        if len(menu_map) != len(set(menu_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid menu item")
        category_cache: dict[int | None, Optional[str]] = {}
        lookup = {}
        for menu_id, menu in menu_map.items():
            if menu.restaurant_id != restaurant_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu item not found for restaurant")
            if menu.item_category_id not in category_cache:
                category_cache[menu.item_category_id] = await self.repo.get_category_name(menu.item_category_id)
            lookup[menu_id] = {
                "menu": menu,
                "category_name": category_cache[menu.item_category_id],
            }
        return lookup

    def _merge_items_payload(self, items_payload: List[OrderItemUpsert] | List[OrderItemCreate]):
        merged: dict[int, dict[str, Optional[str] | int]] = {}
        for itm in items_payload:
            if itm.menu_item_id not in merged:
                merged[itm.menu_item_id] = {"qty": itm.qty, "notes": itm.notes}
            else:
                merged[itm.menu_item_id]["qty"] += itm.qty  # type: ignore
                if itm.notes is not None:
                    merged[itm.menu_item_id]["notes"] = itm.notes
        return merged

    async def _validate_menu_items(self, restaurant_id: int, items_payload) -> List[OrderItem]:
        menu_ids = [i.menu_item_id for i in items_payload]
        menu_models = await self.repo.get_menu_items(menu_ids)
        menu_map = {m.id: m for m in menu_models}
        if len(menu_map) != len(menu_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid menu item")

        order_items: List[OrderItem] = []
        for itm in items_payload:
            menu = menu_map.get(itm.menu_item_id)
            if not menu or menu.restaurant_id != restaurant_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu item not found for restaurant")
            line_total = float(menu.price) * itm.qty
            category_name = await self.repo.get_category_name(menu.item_category_id)
            order_items.append(OrderItem(
                menu_item_id=menu.id,
                name_snapshot=menu.name,
                category_name_snapshot=category_name,
                unit_price=menu.price,
                qty=itm.qty,
                line_total=line_total,
                notes=itm.notes,
            ))
        return order_items

    def _calc_totals(self, items: List[OrderItem]):
        subtotal = sum(float(i.line_total) for i in items)
        tax_total = 0.0
        service_charge = 0.0
        discount_total = 0.0
        grand_total = subtotal + tax_total + service_charge - discount_total
        return subtotal, tax_total, service_charge, discount_total, grand_total

    async def _recalculate_order_totals(self, order: Order):
        subtotal = sum(self._dec(i.line_total) for i in order.items)
        tax_total = self._dec(order.tax_total)
        service_charge = self._dec(order.service_charge)
        discount_total = self._dec(order.discount_total)

        order.subtotal = self._money(subtotal)
        order.tax_total = self._money(tax_total)
        order.service_charge = self._money(service_charge)
        order.discount_total = self._money(discount_total)
        order.grand_total = self._money(order.subtotal + order.tax_total + order.service_charge - order.discount_total)

    async def _add_items_to_order(self, order: Order, items: List[OrderItem], actor_id: Optional[int], metadata: Optional[dict] = None):
        if not items:
            return order

        order.items.extend(items)
        await self._recalculate_order_totals(order)
        await self.repo.update_order(order)

        meta = {k: v for k, v in (metadata or {}).items() if v is not None}
        for itm in items:
            payload = {"item_id": itm.id, "menu_item_id": itm.menu_item_id, "qty": itm.qty, "notes": itm.notes}
            payload.update(meta)
            await self.repo.add_event(order.id, "item_added", payload, actor_id)

        if meta:
            await self.repo.add_event(order.id, "items_updated_by_channel", meta, actor_id)

        return order

    async def create_order(self, payload: OrderCreate, actor_id: Optional[int]):
        await self.restaurant_repo.get_by_id(payload.restaurant_id)
        order_items = await self._validate_menu_items(payload.restaurant_id, payload.items)
        subtotal, tax_total, service_charge, discount_total, grand_total = self._calc_totals(order_items)

        table_id = payload.table_id if payload.table_id not in (None, 0) else None
        group_id = payload.group_id if payload.group_id not in (None, 0) else None

        order = Order(
            restaurant_id=payload.restaurant_id,
            channel=payload.channel.value,
            table_id=table_id,
            group_id=group_id,
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
            status=OrderStatus.pending,
            subtotal=subtotal,
            tax_total=tax_total,
            service_charge=service_charge,
            discount_total=discount_total,
            grand_total=grand_total,
            notes=payload.notes,
            created_by_staff_id=actor_id,
        )
        order.items = order_items

        payments = []
        if payload.payments:
            for p in payload.payments:
                payments.append(OrderPayment(
                    method=p.method.value,
                    amount=p.amount,
                    reference=p.reference,
                    status=p.status.value,
                ))
        order.payments = payments

        created = await self.repo.create_order(order)
        await self.repo.add_event(created.id, "order_created", {"status": order.status.value}, actor_id)
        return await self.get_order(created.id)

    async def get_order(self, order_id: int):
        order = await self.repo.get_order(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    async def get_orders_by_table(self, table_id: int, status_filter: Optional[List[OrderStatusEnum]], channel: Optional[str], search: Optional[str], skip: int, limit: int):
        table = await self.repo.get_table_by_id(table_id)
        if not table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
        return await self.list_orders(table.restaurant_id, status_filter, channel, table_id, search, skip, limit)

    async def list_orders(self, restaurant_id: int, status_filter: Optional[List[OrderStatusEnum]], channel: Optional[str], table_id: Optional[int], search: Optional[str], skip: int, limit: int):
        status_values = [OrderStatus(s.value) for s in status_filter] if status_filter else None
        channel_value = None
        if channel:
            try:
                channel_value = OrderChannel(channel)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid channel")
        orders, total = await self.repo.list_orders(restaurant_id, status_values, channel_value, table_id, search, skip, limit)
        return orders, total

    async def update_status(self, order_id: int, new_status: OrderStatusEnum, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        allowed = STATUS_FLOW.get(order.status, [])
        if OrderStatus(new_status.value) not in allowed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status transition")
        order.status = OrderStatus(new_status.value)
        now = datetime.utcnow()
        if new_status == OrderStatusEnum.completed:
            order.completed_at = now
        if new_status == OrderStatusEnum.canceled:
            order.canceled_at = now
        await self.repo.update_order(order)
        await self.repo.add_event(order.id, "status_changed", {"status": new_status.value}, actor_id)
        return order

    async def update_order(self, order_id: int, data: OrderUpdate, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        if data.notes is not None:
            order.notes = data.notes
        if data.customer_name is not None:
            order.customer_name = data.customer_name
        if data.customer_phone is not None:
            order.customer_phone = data.customer_phone
        if data.table_id is not None:
            order.table_id = data.table_id if data.table_id not in (0,) else None
        if data.group_id is not None:
            order.group_id = data.group_id if data.group_id not in (0,) else None
        await self.repo.update_order(order)
        await self.repo.add_event(order.id, "order_updated", data.dict(exclude_none=True), actor_id)
        return order

    async def add_items(self, order_id: int, payload: OrderAddItems, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        if order.status not in [OrderStatus.pending, OrderStatus.accepted]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify items in current status")
        new_items = await self._validate_menu_items(order.restaurant_id, payload.items)
        return await self._add_items_to_order(order, new_items, actor_id)

    async def bulk_add_items(self, order_id: int, payload: OrderBulkAddItems, actor_id: Optional[int]):
        order = await self._get_order_for_update(order_id)
        self._ensure_items_mutable(order)
        merged_payload = self._merge_items_payload(payload.items)
        if not merged_payload:
            return order

        menu_lookup = await self._get_menu_lookup(order.restaurant_id, list(merged_payload.keys()))
        added_existing: List[tuple[OrderItem, int]] = []
        added_new: List[OrderItem] = []
        for menu_id, incoming in merged_payload.items():
            qty = int(incoming["qty"] or 0)
            notes = incoming.get("notes")
            if qty <= 0:
                continue
            existing = next((i for i in order.items if i.menu_item_id == menu_id), None)
            if existing:
                added_existing.append((existing, qty))
                existing.qty += qty
                if notes is not None:
                    existing.notes = notes
                existing.unit_price = self._money(self._dec(existing.unit_price))
                existing.line_total = self._money(self._dec(existing.unit_price) * existing.qty)
                continue
            menu = menu_lookup[menu_id]["menu"]
            unit_price = self._money(menu.price)
            line_total = self._money(unit_price * qty)
            order_item = OrderItem(
                menu_item_id=menu_id,
                name_snapshot=menu.name,
                category_name_snapshot=menu_lookup[menu_id]["category_name"],
                unit_price=unit_price,
                qty=qty,
                line_total=line_total,
                notes=notes,
            )
            order.items.append(order_item)
            added_new.append(order_item)

        await self._recalculate_order_totals(order)
        await self.repo.update_order(order)

        for itm, delta in added_existing:
            await self.repo.add_event(
                order.id,
                "item_added",
                {"item_id": itm.id, "menu_item_id": itm.menu_item_id, "qty": itm.qty, "delta_qty": delta},
                actor_id,
            )
        for itm in added_new:
            await self.repo.add_event(
                order.id,
                "item_added",
                {"item_id": itm.id, "menu_item_id": itm.menu_item_id, "qty": itm.qty},
                actor_id,
            )
        return order

    async def update_items_by_channel(self, order_id: int, payload: OrderItemsChannelUpdate, actor_id: Optional[int]):
        if payload.table_id is None and payload.group_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="table_id or group_id is required")
        order = await self.get_order(order_id)
        if order.status not in [OrderStatus.pending, OrderStatus.accepted]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify items in current status")

        if payload.table_id is not None:
            if order.table_id != payload.table_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order does not belong to table")
        if payload.group_id is not None:
            if order.group_id != payload.group_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order does not belong to group")

        new_items = await self._validate_menu_items(order.restaurant_id, payload.items)
        return await self._add_items_to_order(
            order,
            new_items,
            actor_id,
            {"table_id": payload.table_id, "group_id": payload.group_id},
        )

    async def add_item(self, order_id: int, payload: OrderAddSingleItem, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        self._ensure_items_mutable(order)
        items = await self._validate_menu_items(order.restaurant_id, [payload.item])
        return await self._add_items_to_order(order, items, actor_id)

    async def bulk_update_items(self, order_id: int, payload: OrderBulkUpdateItems, actor_id: Optional[int]):
        order = await self._get_order_for_update(order_id)
        self._ensure_items_mutable(order)
        merged_payload = self._merge_items_payload(payload.items)
        payload_menu_ids = set(merged_payload.keys())
        menu_lookup = await self._get_menu_lookup(order.restaurant_id, list(payload_menu_ids))

        added_items: List[OrderItem] = []
        updated_items: List[OrderItem] = []
        removed_items: List[dict] = []

        existing_map = {itm.menu_item_id: itm for itm in order.items if itm.menu_item_id is not None}

        for menu_id, incoming in merged_payload.items():
            qty = int(incoming["qty"] or 0)
            notes = incoming.get("notes")
            menu_info = menu_lookup.get(menu_id)
            if menu_info is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid menu item")

            if qty <= 0:
                item_to_remove = existing_map.get(menu_id)
                if item_to_remove and item_to_remove in order.items:
                    removed_items.append({"item_id": item_to_remove.id, "menu_item_id": item_to_remove.menu_item_id})
                    order.items.remove(item_to_remove)
                continue

            if menu_id in existing_map:
                item = existing_map[menu_id]
                item.qty = qty
                if notes is not None:
                    item.notes = notes
                item.unit_price = self._money(self._dec(item.unit_price))
                item.line_total = self._money(self._dec(item.unit_price) * item.qty)
                updated_items.append(item)
            else:
                unit_price = self._money(menu_info["menu"].price)
                line_total = self._money(unit_price * qty)
                new_item = OrderItem(
                    menu_item_id=menu_id,
                    name_snapshot=menu_info["menu"].name,
                    category_name_snapshot=menu_info["category_name"],
                    unit_price=unit_price,
                    qty=qty,
                    line_total=line_total,
                    notes=notes,
                )
                order.items.append(new_item)
                added_items.append(new_item)

        for item in list(order.items):
            if item.menu_item_id in payload_menu_ids:
                continue
            removed_items.append({"item_id": item.id, "menu_item_id": item.menu_item_id})
            order.items.remove(item)

        await self._recalculate_order_totals(order)
        await self.repo.update_order(order)

        for itm in added_items:
            await self.repo.add_event(
                order.id,
                "item_added",
                {"item_id": itm.id, "menu_item_id": itm.menu_item_id, "qty": itm.qty},
                actor_id,
            )
        for itm in updated_items:
            await self.repo.add_event(
                order.id,
                "item_updated",
                {"item_id": itm.id, "menu_item_id": itm.menu_item_id, "qty": itm.qty, "notes": itm.notes},
                actor_id,
            )
        for itm in removed_items:
            await self.repo.add_event(order.id, "item_removed", itm, actor_id)

        return order

    async def update_item_quantity(self, order_id: int, item_id: int, payload: OrderItemQuantityUpdate, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        self._ensure_items_mutable(order)
        item = self._find_item(order, item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        item.qty = payload.qty
        item.line_total = self._money(self._dec(item.unit_price) * payload.qty)
        await self._recalculate_order_totals(order)
        await self.repo.update_order(order)
        await self.repo.add_event(
            order.id,
            "item_quantity_updated",
            {"item_id": item.id, "menu_item_id": item.menu_item_id, "qty": item.qty},
            actor_id,
        )
        return order

    async def add_payment(self, order_id: int, payload: OrderAddPayment, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        p = payload.payment
        payment = OrderPayment(
            order_id=order.id,
            method=p.method.value,
            amount=p.amount,
            reference=p.reference,
            status=p.status.value,
        )
        await self.repo.add_payment(payment)
        await self.repo.add_event(order.id, "payment_added", {"amount": p.amount, "method": p.method.value}, actor_id)
        return payment

    async def cancel_order(self, order_id: int, payload: OrderCancel, actor_id: Optional[int]):
        order = await self.get_order(order_id)
        if order.status == OrderStatus.canceled:
            return order
        order.status = OrderStatus.canceled
        order.canceled_at = datetime.utcnow()
        order.cancel_reason = payload.reason
        await self.repo.update_order(order)
        await self.repo.add_event(order.id, "order_canceled", {"reason": payload.reason}, actor_id)
        return order

    async def delete_order(self, order_id: int):
        order = await self.get_order(order_id)
        await self.repo.delete_order(order)
        return {"message": "Order deleted"}

    async def get_events(self, order_id: int):
        await self.get_order(order_id)
        return await self.repo.get_events(order_id)
