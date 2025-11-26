# app/controller/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_services import AuthServices
from app.schema.user_schema import LoginResponse
from app.schema.base_response import BaseResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=BaseResponse[LoginResponse])
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    service = AuthServices(db)
    result = await service.login(credentials)

    return BaseResponse(
        status="success",
        message="Login successful",
        data=result
    )
