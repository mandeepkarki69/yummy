from pydantic import BaseModel

class RestaurantCreate(BaseModel):
    name: str
    address: str
    phone: str
    description: str | None = None
    tax_rate: float = 0
    service_charge_rate: float = 0


class RestaurantUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    description: str | None = None
    tax_rate: float | None = None
    service_charge_rate: float | None = None


class RestaurantRead(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    description: str | None
    registered_by: int
    tax_rate: float
    service_charge_rate: float

    class Config:
        orm_mode = True
