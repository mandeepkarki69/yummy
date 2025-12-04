from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.order_model import Order, OrderItem, OrderPayment, OrderEvent, OrderStatus
from app.models.menu_model import Menu
from app.models.item_category_model import ItemCategory
from app.models.table_model import RestaurantTable


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order: Order):
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_order(self, order_id: int):
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.events),
                selectinload(Order.table),
            )
            .where(Order.id == order_id)
        )
        return result.scalars().first()

    async def get_order_for_update(self, order_id: int):
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.events),
                selectinload(Order.table),
            )
            .where(Order.id == order_id)
            .with_for_update()
        )
        return result.scalars().first()

    async def list_orders(self, restaurant_id: int, status_filter: Optional[List[OrderStatus]] = None, channel: Optional[str] = None, table_id: Optional[int] = None, search: Optional[str] = None, skip: int = 0, limit: int = 50):
        query = select(Order).options(
            selectinload(Order.items),
            selectinload(Order.payments),
            selectinload(Order.table),
        ).where(Order.restaurant_id == restaurant_id)
        if status_filter:
            query = query.where(Order.status.in_(status_filter))
        if channel:
            query = query.where(Order.channel == channel)
        if table_id:
            query = query.where(Order.table_id == table_id)
        if search:
            like = f"%{search}%"
            query = query.where((Order.customer_name.ilike(like)) | (Order.customer_phone.ilike(like)))
        total_result = await self.db.execute(query.with_only_columns(func.count()))
        total = total_result.scalar_one()
        result = await self.db.execute(query.order_by(Order.created_at.desc()).offset(skip).limit(limit))
        return result.scalars().all(), total

    async def add_event(self, order_id: int, event: str, payload: dict | None, actor_id: int | None):
        ev = OrderEvent(order_id=order_id, event=event, payload=payload, actor_id=actor_id)
        self.db.add(ev)
        await self.db.commit()
        await self.db.refresh(ev)
        return ev

    async def get_events(self, order_id: int):
        result = await self.db.execute(select(OrderEvent).where(OrderEvent.order_id == order_id).order_by(OrderEvent.created_at.desc()))
        return result.scalars().all()

    async def add_payment(self, payment: OrderPayment):
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def update_order(self, order: Order):
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def delete_order(self, order: Order):
        await self.db.delete(order)
        await self.db.commit()

    async def get_menu_items(self, ids: List[int]):
        result = await self.db.execute(select(Menu).where(Menu.id.in_(ids)))
        return result.scalars().all()

    async def get_category_name(self, category_id: Optional[int]):
        if category_id is None:
            return None
        category = await self.db.get(ItemCategory, category_id)
        return category.name if category else None

    async def get_table_by_id(self, table_id: int):
        return await self.db.get(RestaurantTable, table_id)
