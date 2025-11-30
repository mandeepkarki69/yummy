
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.table_model import RestaurantTable
from app.repositories.restaurant_tables_repository import RestaurantTablesRepository
from app.schema.restaurant_table_schema import RestaurantTableCreate, RestaurantTableUpdate
class RestaurantTableService:
    def __init__(self, db: AsyncSession):
        self.db = RestaurantTablesRepository(db)
    
    async def get_all_restaurant_tables_by_restaurant_id(self, restaurant_id: int):
        restaurant_tables = await self.db.get_all_restaurant_tables_by_restaurant_id(restaurant_id)
        return restaurant_tables
        
    
    async def get_restaurant_table_by_id(self,  table_id: int):
        restaurant_table = await self.db.get_restaurant_table_by_id(table_id)
        if not restaurant_table:
            raise HTTPException(status_code=404, detail="Restaurant table not found")
        return restaurant_table
    
    async def get_table_by_table_type(self, table_type_id: int):
        tables = await self.db.get_table_by_table_type(table_type_id)
        if not tables:
            raise HTTPException(status_code=404, detail="Tables not found")
        return tables
    
    async def create_restaurant_table(self, data: RestaurantTableCreate, restaurant_id: int):
        # Ensure restaurant and table type belong together before creating the table
        await self.db.ensure_restaurant_exists(restaurant_id)
        await self.db.validate_table_type_for_restaurant(restaurant_id, data.table_type_id)
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
    
    async def update_restaurant_table(self, table_id: int, data: RestaurantTableUpdate):
        table = await self.db.get_restaurant_table_by_id(table_id)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        # Only update fields if they are provided
        if data.name is not None:
            table.table_name = data.name
        if data.capacity is not None:
            table.capacity = data.capacity
        if data.table_type_id is not None:
            table.table_type_id = data.table_type_id
        if data.status is not None:
            table.status = data.status

        return await self.db.update_restaurant_table(table)

    
    
        
         
        
    
    
        
    
        
