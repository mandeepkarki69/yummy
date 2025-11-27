from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.schema.user_schema import UserCreate, AdminCreate
from app.utils.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_user(self, user_id: int):
        return await self.repo.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str):
        
        return await self.repo.get_user_by_email(email)
    
    async def get_all_users(self):
        return await self.repo.get_all_users()

    async def create_user(self, user_data: UserCreate):
        hashed_password = get_password_hash(user_data.password)
        user_data.password = hashed_password
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role= user_data.role  
        )
        return await self.repo.create_user(user)
    
    async def create_admin_user(self, user_data: AdminCreate):
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Password does not match")
         #now validating the passwords
        hashed_password = get_password_hash(user_data.password)
        user_data.password = hashed_password
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role= 'admin'
        )
        return await self.repo.create_admin_user(user)
    
    
    
    
    
    
    
