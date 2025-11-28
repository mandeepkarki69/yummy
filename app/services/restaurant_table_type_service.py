from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table_type_model import TableType
from app.repositories.restaurant_table_type_service import RestaurantTableTypeRepository

class RestaurantTypeService :
    def __init__(self, db: AsyncSession):
        self.repo = RestaurantTableTypeRepository(db)
        
    async def get_all_restaurant_table_types_by_id(self, restaurant_id: int):
        tabletypes = await self.repo.get_all_restaurant_table_types_by_id(restaurant_id)
        if not tabletypes:
            raise HTTPException(status_code=404, detail="Table types not found")
        return tabletypes
    
    async def get_restaurant_table_type_by_id(self, table_type_id: int):
        tabletype = await self.repo.get_restaurant_table_type_by_id(table_type_id)
        if not tabletype:
            raise HTTPException(status_code=404, detail="Table type not found")
        return tabletype
    
    async def create_restaurant_table_type(self, data: TableType, restaurant_id: int):
        tabletype = TableType (
            name=data.name,
            restaurant_id=restaurant_id
        )
        return await self.repo.create_restaurant_table_type(tabletype)
    
    async def delete_restaurant_table_type(self, table_type_id: int):
        tabletype = await self.repo.get_restaurant_table_type_by_id(table_type_id)
        if not tabletype:
            raise HTTPException(status_code=404, detail="Table type not found")
        await self.repo.delete_restaurant_table_type(tabletype)
        return {"message": "Table type deleted successfully"}
    
    
    
    
    
    