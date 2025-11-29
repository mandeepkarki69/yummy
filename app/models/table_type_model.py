from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class TableType(Base):
    __tablename__ = "table_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant_info.id", ondelete="CASCADE"))

    restaurant = relationship("Restaurant", back_populates="table_types")
    tables = relationship(
        "RestaurantTable",
        back_populates="table_type_rel",
        cascade="all, delete-orphan",  # <- important for cascading deletes
        passive_deletes=True            # <- tells SQLAlchemy to rely on DB cascade
    )
