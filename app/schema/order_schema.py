from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class OrderStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    preparing = "preparing"
    ready = "ready"
    completed = "completed"
    canceled = "canceled"


class OrderChannelEnum(str, Enum):
    table = "table"
    group = "group"
    pickup = "pickup"
    quick_billing = "quick_billing"
    delivery = "delivery"
    online = "online"


class PaymentStatusEnum(str, Enum):
    success = "success"
    pending = "pending"
    failed = "failed"
    refunded = "refunded"


class PaymentMethodEnum(str, Enum):
    cash = "cash"
    card = "card"
    upi = "upi"
    other = "other"


class OrderItemCreate(BaseModel):
    menu_item_id: int
    qty: int = Field(gt=0)
    notes: Optional[str] = None


class OrderPaymentCreate(BaseModel):
    method: PaymentMethodEnum
    amount: float
    reference: Optional[str] = None
    status: PaymentStatusEnum = PaymentStatusEnum.success


class OrderCreate(BaseModel):
    restaurant_id: int
    channel: OrderChannelEnum
    table_id: Optional[int] = None
    group_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]
    payments: Optional[List[OrderPaymentCreate]] = None


class OrderItemRead(BaseModel):
    id: int
    menu_item_id: Optional[int]
    name_snapshot: str
    category_name_snapshot: Optional[str]
    unit_price: float
    qty: int
    line_total: float
    notes: Optional[str]

    class Config:
        from_attributes = True


class OrderPaymentRead(BaseModel):
    id: int
    method: PaymentMethodEnum
    amount: float
    reference: Optional[str]
    status: PaymentStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: int
    restaurant_id: int
    channel: OrderChannelEnum
    table_id: Optional[int]
    table_name: Optional[str] = None
    group_id: Optional[int]
    customer_name: Optional[str]
    customer_phone: Optional[str]
    status: OrderStatusEnum
    subtotal: float
    tax_total: float
    service_charge: float
    discount_total: float
    grand_total: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    canceled_at: Optional[datetime]
    cancel_reason: Optional[str]
    items: List[OrderItemRead]
    payments: List[OrderPaymentRead]

    class Config:
        from_attributes = True


class OrderListRead(BaseModel):
    orders: List[OrderRead]
    total: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum


class OrderUpdate(BaseModel):
    notes: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    table_id: Optional[int] = None
    group_id: Optional[int] = None


class OrderAddItems(BaseModel):
    items: List[OrderItemCreate]


class OrderAddPayment(BaseModel):
    payment: OrderPaymentCreate


class OrderCancel(BaseModel):
    reason: str


class OrderEventRead(BaseModel):
    id: int
    event: str
    payload: Optional[dict]
    created_at: datetime
    actor_id: Optional[int]

    class Config:
        from_attributes = True
