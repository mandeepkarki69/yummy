# app/routes/user_router.py
from app.utils.role_checker import RoleChecker
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schema.user_schema import UserCreate, UserRead, AdminCreate, AdminRead
from app.services.user_services import UserService
from app.schema.base_response import BaseResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/admin/register", response_model=BaseResponse[AdminRead], status_code=status.HTTP_201_CREATED)
async def create_admin_user(user: AdminCreate, db: AsyncSession = Depends(get_db)):
     service = UserService(db)
     existing_user = await service.repo.get_user_by_email(user.email)
     if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
     new_user = await service.create_admin_user(user)
     return BaseResponse(
        status="success",
        message="Admin user created successfully",
        data=new_user
    )

@router.post("/", response_model=BaseResponse[UserRead],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RoleChecker(["admin"]))])
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    
    service = UserService(db)
    existing_user = await service.repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await service.create_user(user)
    return BaseResponse(
        status="success",
        message="User created successfully",
        data=new_user
    )

@router.get("/all", response_model=BaseResponse[list[UserRead]],
            dependencies=[Depends(RoleChecker(["admin"]))])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    users = await service.get_all_users()
    return BaseResponse(
        status="success",
        message=f"{len(users)} users fetched successfully",
        data=users
    )

@router.get("/{user_id}", response_model=BaseResponse[UserRead], 
            dependencies=[Depends(RoleChecker(["admin"]))])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(
        status="success",
        message="User fetched successfully",
        data=user
    )
