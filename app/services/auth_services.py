from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.repositories.auth_repository import AuthRepository
from app.utils.oauth2 import create_access_token
from app.utils.security import verify_password



class AuthServices:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)

    async def login(self, credentials: OAuth2PasswordRequestForm):
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
        token = create_access_token({"user_id": user.id})

        return {
            "access_token": token,
            "token_type": "bearer"
        }
