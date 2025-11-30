from fastapi import APIRouter, Depends, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.menu_service import MenuService
from app.schema.menu_schema import MenuRead, MenuUpdate, MenuCategoryGroup, MenuCreate
from app.schema.base_response import BaseResponse
from app.utils.role_checker import RoleChecker


router = APIRouter(prefix="/menus", tags=["Menu"])


@router.post(
    "/{restaurant_id}",
    response_model=BaseResponse[MenuRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def create_menu(
    restaurant_id: int,
    name: str = Form(...),
    price: float = Form(...),
    item_category_id: int = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    service = MenuService(db)
    data = MenuCreate(name=name, price=price, item_category_id=item_category_id, description=description)
    menu = await service.create_menu(restaurant_id, data, image)
    return BaseResponse(status="success", message="Menu item created successfully", data=menu)


@router.put(
    "/{menu_id}",
    response_model=BaseResponse[MenuRead],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def update_menu(
    menu_id: int,
    name: str | None = Form(None),
    price: float | None = Form(None),
    item_category_id: int | None = Form(None),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    service = MenuService(db)
    data = MenuUpdate(name=name, price=price, item_category_id=item_category_id, description=description)
    menu = await service.update_menu(menu_id, data, image)
    return BaseResponse(status="success", message="Menu item updated successfully", data=menu)


@router.delete(
    "/{menu_id}",
    response_model=BaseResponse[None],
    dependencies=[Depends(RoleChecker(["admin", "staff"]))],
)
async def delete_menu(menu_id: int, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    await service.delete_menu(menu_id)
    return BaseResponse(status="success", message="Menu item deleted successfully", data=None)


@router.get("/item/{menu_id}", response_model=BaseResponse[MenuRead])
async def get_menu(menu_id: int, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    menu = await service.get_menu_by_id(menu_id)
    return BaseResponse(status="success", message="Menu item fetched successfully", data=menu)


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=BaseResponse[list[MenuRead]],
)
async def get_menus_by_restaurant(
    restaurant_id: int,
    item_category_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = MenuService(db)
    menus = await service.get_menus_by_restaurant(restaurant_id, item_category_id)
    return BaseResponse(status="success", message=f"{len(menus)} menu items fetched", data=menus)


@router.get(
    "/restaurant/{restaurant_id}/grouped",
    response_model=BaseResponse[list[MenuCategoryGroup]],
)
async def get_grouped_menus(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    groups = await service.get_menus_grouped_by_category(restaurant_id)
    return BaseResponse(status="success", message="Menu items grouped by category fetched successfully", data=groups)

