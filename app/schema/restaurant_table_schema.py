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
        


