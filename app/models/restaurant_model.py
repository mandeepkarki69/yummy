from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class Restaurant(Base):
    __tablename__ = "restaurant_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    description = Column(String, nullable=True)
    registered_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)
    service_charge_rate = Column(Numeric(5, 2), nullable=False, default=0)

    user = relationship("User", back_populates="restaurants", passive_deletes=True)
    tables = relationship("RestaurantTable", back_populates="restaurant", cascade="all, delete")
    table_types = relationship("TableType", back_populates="restaurant", cascade="all, delete")
    categories = relationship("ItemCategory", back_populates="restaurant", cascade="all, delete")
    menu_items = relationship("Menu", back_populates="restaurant", cascade="all, delete")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
