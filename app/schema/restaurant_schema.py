from pydantic import BaseModel

class RestaurantCreate(BaseModel):
    name: str
    address: str
    phone: str
    description: str | None = None


class RestaurantUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    description: str | None = None


class RestaurantRead(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    description: str | None
    registered_by: int

    class Config:
        orm_mode = True
