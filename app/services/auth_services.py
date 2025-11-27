# app/services/auth_services.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.repositories.auth_repository import AuthRepository
from app.utils.oauth2 import create_access_token
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

        # Create JWT token
        # app/services/auth_services.py

        token = create_access_token({
                "user_id": user.id,
                "role": user.role
         })


        # Return full LoginResponse structure
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.name,
            "email": user.email,
            "user_role": user.role
        }
