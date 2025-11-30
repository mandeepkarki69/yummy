from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class RestaurantTable(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant_info.id", ondelete="CASCADE"))
    table_type_id = Column(Integer, ForeignKey("table_types.id", ondelete="CASCADE"))
    status = Column(String, nullable=True, server_default="free")
    
    restaurant = relationship("Restaurant", back_populates="tables", passive_deletes=True)
