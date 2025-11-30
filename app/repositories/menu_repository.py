from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.menu_model import Menu
from app.models.restaurant_model import Restaurant
from app.models.item_category_model import ItemCategory


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = await self.db.get(Restaurant, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        return restaurant

    async def ensure_category(self, category_id: int, restaurant_id: int) -> ItemCategory:
        category = await self.db.get(ItemCategory, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item category not found")
        if category.restaurant_id != restaurant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not belong to this restaurant")
        return category

    async def create_menu(self, menu: Menu):
        self.db.add(menu)
        await self.db.commit()
        await self.db.refresh(menu)
        return menu

    async def get_menu_by_id(self, menu_id: int):
        result = await self.db.execute(select(Menu).where(Menu.id == menu_id))
        return result.scalars().first()

    async def get_menus_by_restaurant(self, restaurant_id: int, category_id: int | None = None):
        query = select(Menu).where(Menu.restaurant_id == restaurant_id)
        if category_id is not None:
            query = query.where(Menu.item_category_id == category_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_menu(self, menu: Menu):
        await self.db.commit()
        await self.db.refresh(menu)
        return menu

    async def delete_menu(self, menu: Menu):
        await self.db.delete(menu)
        await self.db.commit()
        return True
