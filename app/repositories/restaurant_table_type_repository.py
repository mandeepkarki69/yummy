from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.table_type_model import TableType
from app.models.restaurant_model import Restaurant


class RestaurantTableTypeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_restaurant_table_types_by_id(self, restaurant_id: int):
        restaurant = await self.db.get(Restaurant, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        result = await self.db.execute(
            select(TableType).where(TableType.restaurant_id == restaurant_id)
        )
        return result.scalars().all()

    async def get_restaurant_table_type_by_id(self, table_type_id: int):
        result = await self.db.execute(
            select(TableType).where(TableType.id == table_type_id)
        )
        return result.scalars().first()

    async def create_restaurant_table_type(self, table_type: TableType):
        self.db.add(table_type)
        await self.db.commit()
        await self.db.refresh(table_type)
        return table_type

    async def delete_restaurant_table_type(self, table_type: TableType):
        await self.db.delete(table_type)
        await self.db.commit()
        return table_type

    async def update_restaurant_table_type(self, table_type: TableType):
        # At this point, the object is already attached to the session
        await self.db.commit()
        await self.db.refresh(table_type)
        return table_type
