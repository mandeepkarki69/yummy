from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.oauth2 import get_current_user
from app.utils.role_checker import RoleChecker
from app.services.restaurant_services import RestaurantService
from app.schema.restaurant_schema import RestaurantCreate, RestaurantRead, RestaurantUpdate
from app.schema.base_response import BaseResponse

router = APIRouter(prefix="/restaurants", tags=["Restaurant"])


# Create Restaurant
@router.post(
    "/",
    response_model=BaseResponse[RestaurantRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def create_restaurant(
    data: RestaurantCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RestaurantService(db)
    restaurant = await service.create_restaurant(data, current_user["user_id"])

    return BaseResponse(
        status="success",
        message="Restaurant created successfully",
        data=restaurant,
    )


# Update Restaurant
@router.put(
    "/{restaurant_id}",
    response_model=BaseResponse[RestaurantRead],
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def update_restaurant(
    restaurant_id: int, data: RestaurantUpdate, db: AsyncSession = Depends(get_db)
):
    service = RestaurantService(db)
    updated = await service.update_restaurant(restaurant_id, data)

    return BaseResponse(
        status="success",
        message="Restaurant updated successfully",
        data=updated,
    )


# Delete Restaurant
@router.delete(
    "/{restaurant_id}",
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def delete_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantService(db)
    result = await service.delete_restaurant(restaurant_id)

    return BaseResponse(
        status="success",
        message=result["message"],
        data=None,
    )


# Get Single Restaurant
@router.get(
    "/{restaurant_id}",
    response_model=BaseResponse[RestaurantRead],
)
async def get_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    service = RestaurantService(db)
    restaurant = await service.get_restaurant(restaurant_id)

    return BaseResponse(
        status="success",
        message="Restaurant fetched successfully",
        data=restaurant,
    )
