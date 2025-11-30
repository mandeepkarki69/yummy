from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.table_model import RestaurantTable
from app.models.restaurant_model import Restaurant
from app.models.table_type_model import TableType

class RestaurantTablesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    
    async  def get_all_restaurant_tables_by_restaurant_id(self, restaurant_id: int):
        restaurant = await self.session.get(Restaurant, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        result = await self.session.execute(select(RestaurantTable).where(RestaurantTable.restaurant_id == restaurant_id))
        return result.scalars().all()
        
    async def get_restaurant_table_by_id(self, table_id: int):
        result = await self.session.execute(select(RestaurantTable).where(RestaurantTable.id == table_id))
        return result.scalars().first()
    
    async def create_restaurant_table(self, table: RestaurantTable):
        self.session.add(table)
        await self.session.commit()
        await self.session.refresh(table)
        return table
    
    async def get_table_by_table_type(self, table_type_id: int):
        table_type = await self.session.get(TableType, table_type_id)
        if not table_type:
            raise HTTPException(status_code=404, detail="Table type not found")
        result = await self.session.execute(select(RestaurantTable).where(RestaurantTable.table_type_id == table_type_id))
        return result.scalars().all()
    
    async def update_restaurant_table(self, table: RestaurantTable):
        await self.session.commit()
        await self.session.refresh(table)
        return table
    
    async def delete_restaurant_table(self, table: RestaurantTable):
        await self.session.delete(table)   
        await self.session.commit()
        return table


    
  
    
    
    
    
    