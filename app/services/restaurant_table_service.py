
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.table_model import RestaurantTable
from app.repositories.restaurant_tables_repository import RestaurantTablesRepository
from app.schema.restaurant_table_schema import RestaurantTableCreate
class RestaurantTableService:
    def __init__(self, db: AsyncSession):
        self.db = RestaurantTablesRepository(db)
    
    async def get_all_restaurant_tables_by_restaurant_id(self, restaurant_id: int):
        restaurant_tables = await self.db.get_all_restaurant_tables_by_restaurant_id(restaurant_id)
        if not restaurant_tables:
            raise HTTPException(status_code=404, detail="Restaurant tables not found")
        return restaurant_tables
        
    
    async def get_restaurant_table_by_id(self,  table_id: int):
        restaurant_table = await self.db.get_restaurant_table_by_id(table_id)
        if not restaurant_table:
            raise HTTPException(status_code=404, detail="Restaurant table not found")
        return restaurant_table
    
    async def create_restaurant_table(self, data: RestaurantTableCreate, restaurant_id: int):
        restaurant = RestaurantTable (
            table_name=data.name,
            capacity=data.capacity,
            table_type_id=data.table_type_id,
            restaurant_id=restaurant_id
        )
        return await self.db.create_restaurant_table(restaurant)
    
    async def delete_restaurant_table(self, table_id: int):
        table = await self.db.get_restaurant_table_by_id(table_id)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        await self.db.delete_restaurant_table(table)
        return {"message": "Table deleted successfully"}
    
    
        
         
        
    
    
        
    
        