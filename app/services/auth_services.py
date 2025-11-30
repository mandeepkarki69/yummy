# app/services/auth_services.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.repositories.auth_repository import AuthRepository
from app.utils.oauth2 import create_access_token, create_refresh_token, verify_refresh_token, revoke_token
from app.utils.security import verify_password
from app.schema.user_schema import LoginResponse


class AuthServices:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)

    async def login(self, credentials: OAuth2PasswordRequestForm) -> dict:
        # Get user by email
        user = await self.repo.login(credentials.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or password"
            )

        # Validate password
        if not verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token({
                "user_id": user.id,
                "role": user.role
         })
        refresh_token = create_refresh_token({
                "user_id": user.id,
                "role": user.role
        })

        # Return full LoginResponse structure
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.name,
            "email": user.email,
            "user_role": user.role
        }

    async def refresh(self, refresh_token: str):
        payload = verify_refresh_token(refresh_token)
        user = await self.repo.get_by_id(payload["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        access_token = create_access_token({
            "user_id": user.id,
            "role": user.role
        })
        # Rotate refresh token to reduce replay window
        new_refresh = create_refresh_token({
            "user_id": user.id,
            "role": user.role
        })
        revoke_token(refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.name,
            "email": user.email,
            "user_role": user.role,
        }

    async def logout(self, access_token: str, refresh_token: str | None = None):
        revoke_token(access_token)
        if refresh_token:
            revoke_token(refresh_token)
        return {"message": "Logged out"}
