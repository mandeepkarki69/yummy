from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.restaurant_table_type_schema import RestaurantTableTypeRead, RestaurantTableTypeCreate
from app.services.restaurant_table_type_service import RestaurantTypeService
from app.utils.oauth2 import get_current_user
from app.utils.role_checker import RoleChecker
from app.schema.base_response import BaseResponse

router = APIRouter(prefix="/restaurants/table-types", tags=["Restaurant Table Type"])


# Create Table Type
@router.post(
    "/{restaurant_id}",
    response_model=BaseResponse[RestaurantTableTypeRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def create_table_type(
    restaurant_id: int,
    data: RestaurantTableTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RestaurantTypeService(db)
    table_type = await service.create_restaurant_table_type(data, restaurant_id)

    return BaseResponse(
        status="success",
        message="Table type created successfully",
        data=table_type,
    )


# Get All Table Types for a Restaurant
@router.get(
    "/{restaurant_id}",
    response_model=BaseResponse[list[RestaurantTableTypeRead]],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def get_all_table_types(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTypeService(db)
    table_types = await service.get_all_restaurant_table_types_by_id(restaurant_id)

    return BaseResponse(
        status="success",
        message=f"{len(table_types)} table types fetched successfully",
        data=table_types,
    )


# Get Single Table Type
@router.get(
    "/single/{table_type_id}",
    response_model=BaseResponse[RestaurantTableTypeRead],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def get_table_type(table_type_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTypeService(db)
    table_type = await service.get_restaurant_table_type_by_id(table_type_id)

    return BaseResponse(
        status="success",
        message="Table type fetched successfully",
        data=table_type,
    )
    
    
# Delete Table Type
@router.delete(
    "/{table_type_id}",
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def delete_table_type(table_type_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTypeService(db)
    result = await service.delete_restaurant_table_type(table_type_id)

    return BaseResponse(
        status="success",
        message=result["message"],
        data=None,
    )
