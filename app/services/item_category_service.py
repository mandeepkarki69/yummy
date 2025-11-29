from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item_category_model import ItemCategory
from app.repositories.item_category_repository import ItemCategoryRepository


class ItemCategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ItemCategoryRepository(self.db)
        
    async def get_item_categories(self, restaurant_id: int):
        categories = await self.repository.get_item_categories(restaurant_id)
        if not categories:
            raise HTTPException(status_code=404, detail="Item categories not found")
        return categories
    
    async def get_item_category_by_id(self, item_category_id: int):
        category = await self.repository.get_item_category_by_id(item_category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Item category not found")
        return category
    
    async def create_item_category(self, item_category: ItemCategory, restaurant_id: int):
        category = ItemCategory(name=item_category.name, restaurant_id=restaurant_id)
        return await self.repository.create_item_category(category)
    
    async def  update_item_category(self, item_category: ItemCategory, item_category_id: int):
        category = await self.repository.get_item_category_by_id(item_category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Item category not found")
        category.name = item_category.name
        return await self.repository.update_item_category(category)
    
    async def delete_item_category(self, item_category_id: int):
        category = await self.repository.get_item_category_by_id(item_category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Item category not found")
        return await self.repository.delete_item_category(category)
        
        
    
        
    