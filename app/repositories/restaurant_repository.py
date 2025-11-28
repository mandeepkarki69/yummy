from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.restaurant_model import Restaurant

class RestaurantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, restaurant: Restaurant):
        self.db.add(restaurant)
        await self.db.commit()
        await self.db.refresh(restaurant)
        return restaurant

    async def get_by_id(self, restaurant_id: int):
        result = await self.db.execute(
            select(Restaurant).where(Restaurant.id == restaurant_id)
        )
        return result.scalars().first()

    async def update(self, restaurant: Restaurant):
        await self.db.commit()
        await self.db.refresh(restaurant)
        return restaurant

    async def delete(self, restaurant: Restaurant):
        await self.db.delete(restaurant)
        await self.db.commit()
        return True
