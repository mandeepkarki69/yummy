from pydantic import BaseModel

class ItemCategorySchemaCreate(BaseModel):
    name: str 
    
class ItemCategorySchemaRead(BaseModel):
    id: int
    name: str
    restaurant_id : int
    
    class Config:
        from_attributes = True
        
class ItemCategorySchemaUpdate(BaseModel):
    name: str | None = None
    
    

    
    
    
