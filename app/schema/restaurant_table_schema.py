from pydantic import BaseModel

class RestaurantTableCreate(BaseModel):
    name: str
    capacity: int
    table_type_id: int
    status: str | None = "free"
    
    

class RestaurantTableRead(BaseModel):
    id: int
    table_name: str
    capacity: int
    restaurant_id: int
    table_type_id: int
    status: str

    class Config:
        from_attributes = True
        
        
class RestaurantTableUpdate(BaseModel):
    table_name: str | None = None
    capacity: int | None = None
    table_type_id: int | None = None
    status: str | None = None
    
   
        


