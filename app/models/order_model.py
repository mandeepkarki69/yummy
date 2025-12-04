import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Numeric, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    preparing = "preparing"
    ready = "ready"
    served = "served"
    completed = "completed"
    canceled = "canceled"


class OrderChannel(enum.Enum):
    table = "table"
    group = "group"
    pickup = "pickup"
    quick_billing = "quick_billing"
    delivery = "delivery"
    online = "online"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant_info.id", ondelete="CASCADE"), nullable=False)
    channel = Column(Enum(OrderChannel), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id", ondelete="SET NULL"), nullable=True)
    group_id = Column(Integer, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    tax_total = Column(Numeric(12, 2), nullable=False, default=0)
    service_charge = Column(Numeric(12, 2), nullable=False, default=0)
    discount_total = Column(Numeric(12, 2), nullable=False, default=0)
    grand_total = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_staff_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    cancel_reason = Column(String, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    payments = relationship("OrderPayment", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    events = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    table = relationship("RestaurantTable", back_populates="orders", lazy="selectin")

    __table_args__ = (
        Index("ix_orders_restaurant_status_created", "restaurant_id", "status", "created_at"),
        Index("ix_orders_restaurant_channel", "restaurant_id", "channel"),
        Index("ix_orders_table", "table_id"),
        Index("ix_orders_group", "group_id"),
    )

    @property
    def table_name(self):
        return self.table.table_name if self.table else None


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True)
    name_snapshot = Column(String, nullable=False)
    category_name_snapshot = Column(String, nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    qty = Column(Integer, nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    notes = Column(String, nullable=True)

    order = relationship("Order", back_populates="items")


class PaymentStatus(enum.Enum):
    success = "success"
    pending = "pending"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(enum.Enum):
    cash = "cash"
    card = "card"
    upi = "upi"
    other = "other"


class OrderPayment(Base):
    __tablename__ = "order_payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reference = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.success)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    order = relationship("Order", back_populates="payments")


class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    event = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    order = relationship("Order", back_populates="events")
