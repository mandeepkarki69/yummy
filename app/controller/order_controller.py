from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.order_service import OrderService
from app.schema.order_schema import (
    OrderCreate,
    OrderRead,
    OrderListRead,
    OrderStatusEnum,
    OrderUpdate,
    OrderStatusUpdate,
    OrderAddItems,
    OrderAddPayment,
    OrderCancel,
    OrderEventRead,
    OrderPaymentRead,
)
from app.schema.base_response import BaseResponse
from app.utils.oauth2 import get_current_user
from app.utils.role_checker import RoleChecker


router = APIRouter(prefix="/orders", tags=["Orders"], dependencies=[Depends(RoleChecker(["admin", "staff"]))])


def _actor(current_user):
    return current_user["user_id"] if current_user else None


@router.post("/", response_model=BaseResponse[OrderRead], status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    order = await service.create_order(payload, _actor(current_user))
    return BaseResponse(status="success", message="Order created", data=order)


@router.get("/{order_id}", response_model=BaseResponse[OrderRead])
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    order = await service.get_order(order_id)
    return BaseResponse(status="success", message="Order fetched", data=order)


@router.get("/table/{table_id}", response_model=BaseResponse[OrderListRead])
async def get_orders_by_table(
    table_id: int,
    status: Optional[List[OrderStatusEnum]] = Query(None),
    channel: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    orders, total = await service.get_orders_by_table(table_id, status, channel, search, skip, limit)
    return BaseResponse(status="success", message="Orders fetched", data={"orders": orders, "total": total})


@router.get("/", response_model=BaseResponse[OrderListRead])
async def list_orders(
    restaurant_id: int,
    status: Optional[List[OrderStatusEnum]] = Query(None),
    channel: Optional[str] = Query(None),
    table_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    orders, total = await service.list_orders(restaurant_id, status, channel, table_id, search, skip, limit)
    return BaseResponse(status="success", message="Orders fetched", data={"orders": orders, "total": total})


@router.patch("/{order_id}/status", response_model=BaseResponse[OrderRead])
async def update_status(order_id: int, payload: OrderStatusUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    order = await service.update_status(order_id, payload.status, _actor(current_user))
    return BaseResponse(status="success", message="Status updated", data=order)


@router.patch("/{order_id}", response_model=BaseResponse[OrderRead])
async def update_order(order_id: int, payload: OrderUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    order = await service.update_order(order_id, payload, _actor(current_user))
    return BaseResponse(status="success", message="Order updated", data=order)


@router.post("/{order_id}/items", response_model=BaseResponse[OrderRead])
async def add_items(order_id: int, payload: OrderAddItems, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    order = await service.add_items(order_id, payload, _actor(current_user))
    return BaseResponse(status="success", message="Items updated", data=order)


@router.post("/{order_id}/payments", response_model=BaseResponse[OrderPaymentRead])
async def add_payment(order_id: int, payload: OrderAddPayment, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    payment = await service.add_payment(order_id, payload, _actor(current_user))
    return BaseResponse(status="success", message="Payment added", data=payment)


@router.post("/{order_id}/cancel", response_model=BaseResponse[OrderRead])
async def cancel_order(order_id: int, payload: OrderCancel, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    order = await service.cancel_order(order_id, payload, _actor(current_user))
    return BaseResponse(status="success", message="Order canceled", data=order)


@router.get("/{order_id}/events", response_model=BaseResponse[List[OrderEventRead]])
async def get_events(order_id: int, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    events = await service.get_events(order_id)
    return BaseResponse(status="success", message="Events fetched", data=events)


@router.delete("/{order_id}", response_model=BaseResponse[dict])
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    service = OrderService(db)
    result = await service.delete_order(order_id)
    return BaseResponse(status="success", message="Order deleted", data=result)
