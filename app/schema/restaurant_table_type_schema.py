from pydantic import BaseModel

class RestaurantTableTypeCreate(BaseModel):
    name: str
    

class RestaurantTableTypeRead(BaseModel):
    id: int
    name: str
    restaurant_id: int
    
    class Config:
        from_attributes = True
        
class RestaurantTableTypeUpdate(BaseModel):
    name: str | None = None
    
    class Config:
        from_attributes = True
    
    
        
        

    
    
    


