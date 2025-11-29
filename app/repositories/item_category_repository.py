from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.item_category_model import ItemCategory

class ItemCategoryRepository:
    def __init__ (self, db: AsyncSession):
        self.db = db
        
    async def create_item_category(self, item_category: ItemCategory):
        self.db.add(item_category)
        await self.db.commit()
        await self.db.refresh(item_category)
        return item_category
    
    async def get_item_categories(self, restaurant_id: int):
        result = await self.db.execute(select(ItemCategory).where(ItemCategory.restaurant_id == restaurant_id))
        return result.scalars().all()
    
    async def get_item_category_by_id(self, item_category_id: int):
        result = await self.db.execute(select(ItemCategory).where(ItemCategory.id == item_category_id))
        return result.scalars().first()
    
    async def update_item_category(self, item_category: ItemCategory):
        await self.db.commit()
        await self.db.refresh(item_category)
        return item_category
    
    async def delete_item_category(self, item_category: ItemCategory):
        await self.db.delete(item_category)
        await self.db.commit()
        return item_category
    
    
        