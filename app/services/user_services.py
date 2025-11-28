from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.schema.user_schema import UserCreate, AdminCreate
from app.utils.oauth2 import create_access_token
from app.utils.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_user(self, user_id: int):
        return await self.repo.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str):
        
        return await self.repo.get_user_by_email(email)
    
    async def get_all_users(self, admin_id: int):
        return await self.repo.get_all_users(admin_id)

    async def create_user(self, user_data: UserCreate, admin_id: int):
        hashed_password = get_password_hash(user_data.password)
        user_data.password = hashed_password
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role= user_data.role,
            created_by=admin_id
        )
        return await self.repo.create_user(user)
    
    async def create_admin_user(self, user_data: AdminCreate):
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Password does not match")

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user model
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password,
            role="admin"
        )

        # Save user to DB
        created_user = await self.repo.create_admin_user(user)

        # Generate token using saved user details
        token = create_access_token({
            "user_id": created_user.id,
            "role": created_user.role
        })

        # Return response with user + token
        return {
        "id": created_user.id,
        "name": created_user.name,
        "email": created_user.email,
        "role": created_user.role,
        "access_token": token,
        "token_type": "bearer"
        }


    
    
    
    
    
    
    
