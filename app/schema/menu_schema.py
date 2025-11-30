from pydantic import BaseModel
from typing import Optional, List


class MenuCreate(BaseModel):
    name: str
    price: float
    item_category_id: int
    description: Optional[str] = None


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    item_category_id: Optional[int] = None
    description: Optional[str] = None


class MenuRead(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    image: Optional[str]
    restaurant_id: int
    item_category_id: Optional[int]

    class Config:
        from_attributes = True


class MenuCategoryGroup(BaseModel):
    category_id: int
    category_name: str
    items: List[MenuRead]

