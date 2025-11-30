from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Menu(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant_info.id", ondelete="CASCADE"))
    item_category_id = Column(Integer, ForeignKey("item_categories.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    restaurant = relationship("Restaurant", back_populates="menu_items", passive_deletes=True)
    category = relationship("ItemCategory", back_populates="menu_items")
