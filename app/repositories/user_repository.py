from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_all_users(self, admin_id: int):
        stmt = select(User).where(User.created_by == admin_id)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return users

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create_user(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def create_admin_user(self, user: User ):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
