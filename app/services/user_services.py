from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.schema.user_schema import UserCreate
from app.utils.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_user(self, user_id: int):
        return await self.repo.get_user_by_id(user_id)

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
    
    
    
