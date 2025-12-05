# app/controller/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_services import AuthServices
from app.schema.user_schema import LoginResponse, RefreshRequest, LogoutRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schema.base_response import BaseResponse
from app.utils.oauth2 import oauth2_scheme

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


@router.post("/refresh", response_model=BaseResponse[LoginResponse])
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthServices(db)
    result = await service.refresh(data.refresh_token)

    return BaseResponse(
        status="success",
        message="Token refreshed successfully",
        data=result
    )


@router.post("/logout", response_model=BaseResponse[dict])
async def logout(
    data: LogoutRequest | None = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    service = AuthServices(db)
    refresh_token = data.refresh_token if data else None
    result = await service.logout(token, refresh_token)

    return BaseResponse(
        status="success",
        message="Logged out successfully",
        data=result
    )


@router.post("/forgot-password", response_model=BaseResponse[dict])
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthServices(db)
    result = await service.forgot_password(data)
    return BaseResponse(status="success", message="If that email exists, an OTP has been sent", data=result)


@router.post("/reset-password", response_model=BaseResponse[dict])
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthServices(db)
    result = await service.reset_password(data)
    return BaseResponse(status="success", message=result["message"], data={"message": result["message"]})
