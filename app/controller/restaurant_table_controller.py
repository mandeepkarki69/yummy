from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.restaurant_table_schema import RestaurantTableCreate, RestaurantTableRead, RestaurantTableUpdate
from app.services.restaurant_table_service import RestaurantTableService
from app.utils.oauth2 import get_current_user
from app.utils.role_checker import RoleChecker
from app.schema.base_response import BaseResponse

router = APIRouter(prefix="/restaurants/tables", tags=["Restaurant Tables"])


# Create Table
@router.post(
    "/{restaurant_id}",
    response_model=BaseResponse[RestaurantTableRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def create_table(
    restaurant_id: int,
    data: RestaurantTableCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RestaurantTableService(db)
    table = await service.create_restaurant_table(data, restaurant_id)

    return BaseResponse(
        status="success",
        message="Table created successfully",
        data=table,
    )
    
@router.put(
    "/{table_id}",
    response_model=BaseResponse[RestaurantTableRead],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def update_table(table_id: int, data: RestaurantTableUpdate, db: AsyncSession = Depends(get_db)):
    service = RestaurantTableService(db)
    table = await service.update_restaurant_table(table_id, data)

    return BaseResponse(
        status="success",
        message="Table updated successfully",
        data=table,
    )
    
@router.get(
    "/by-table-type/{table_id}",  response_model=BaseResponse[RestaurantTableRead],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],)
async def get_table_by_table_type(table_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTableService(db)
    table = await service.get_table_by_table_type(table_id)

    return BaseResponse(
        status="success",
        message="Table fetched successfully",
        data=table,
    )
    
# Get Single Table
@router.get(
    "/single/{table_id}",
    response_model=BaseResponse[RestaurantTableRead],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def get_table(table_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTableService(db)
    table = await service.get_restaurant_table_by_id(table_id)

    return BaseResponse(
        status="success",
        message="Table fetched successfully",
        data=table,
    )



# Get All Tables for Restaurant
@router.get(
    "/all/{restaurant_id}",
    response_model=BaseResponse[list[RestaurantTableRead]],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def get_all_tables(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTableService(db)
    tables = await service.get_all_restaurant_tables_by_restaurant_id(restaurant_id)

    return BaseResponse(
        status="success",
        message=f"{len(tables)} tables fetched successfully",
        data=tables,
    )
    
# Delete Table
@router.delete(
    "/{table_id}",
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def delete_table(table_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantTableService(db)
    result = await service.delete_restaurant_table(table_id)

    return BaseResponse(
        status="success",
        message=result["message"],
        data=None,
    )
