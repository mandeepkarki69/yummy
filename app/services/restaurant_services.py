from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurant_model import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.schema.restaurant_schema import RestaurantCreate, RestaurantUpdate

class RestaurantService:
    def __init__(self, db: AsyncSession):
        self.repo = RestaurantRepository(db)

    async def create_restaurant(self, data: RestaurantCreate, user_id: int):
        restaurant = Restaurant(
            name=data.name,
            address=data.address,
            phone=data.phone,
            description=data.description,
            registered_by=user_id
        )
        return await self.repo.create(restaurant)

    async def get_restaurant(self, restaurant_id: int):
        restaurant = await self.repo.get_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant

    async def update_restaurant(self, restaurant_id: int, data: RestaurantUpdate):
        restaurant = await self.repo.get_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        if data.name is not None:
            restaurant.name = data.name
        if data.address is not None:
            restaurant.address = data.address
        if data.phone is not None:
            restaurant.phone = data.phone
        if data.description is not None:
            restaurant.description = data.description

        return await self.repo.update(restaurant)

    async def delete_restaurant(self, restaurant_id: int):
        restaurant = await self.repo.get_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        await self.repo.delete(restaurant)
        return {"message": "Restaurant deleted successfully"}
