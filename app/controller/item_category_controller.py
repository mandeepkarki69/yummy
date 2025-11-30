from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.oauth2 import get_current_user
from app.utils.role_checker import RoleChecker
from app.services.item_category_service import ItemCategoryService
from app.schema.item_category_schema import ItemCategorySchemaCreate, ItemCategorySchemaRead ,ItemCategorySchemaUpdate
from app.schema.base_response import BaseResponse

router = APIRouter(prefix="/item-categories", tags=["Item Category"])

@router.post(
    "/{restaurant_id}",
    response_model=BaseResponse[ItemCategorySchemaRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def create_item_category(
    restaurant_id : int ,
    data: ItemCategorySchemaCreate,
    db: AsyncSession = Depends(get_db),
    
):
    service = ItemCategoryService(db)
    category = await service.create_item_category(data, restaurant_id)

    return BaseResponse(
        status="success",
        message="Item category created successfully",
        data=category,
)
    
    
@router.get(
    "/{item_category_id}",
    response_model=BaseResponse[ItemCategorySchemaRead],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def get_item_category(item_category_id: int, db: AsyncSession = Depends(get_db)):
    service = ItemCategoryService(db)
    category = await service.get_item_category_by_id(item_category_id)

    return BaseResponse(
        status="success",
        message="Item category fetched successfully",
        data=category,
    )
    
    
    
@router.put(
    "/{item_category_id}",
    response_model=BaseResponse[ItemCategorySchemaRead],
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def update_item_category(item_category_id: int, data: ItemCategorySchemaUpdate, db: AsyncSession = Depends(get_db)):
    service = ItemCategoryService(db)
    category = await service.update_item_category(data, item_category_id)

    return BaseResponse(
        status="success",
        message="Item category updated successfully",
        data=category,
    )
    
@router.delete(
    "/{item_category_id}",
    response_model=BaseResponse[None],
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def delete_item_category(item_category_id: int, db: AsyncSession = Depends(get_db)):
    service = ItemCategoryService(db)
    await service.delete_item_category(item_category_id)
    return BaseResponse(
        status="success",
        message="Item category deleted successfully",
        data=None,
    )
