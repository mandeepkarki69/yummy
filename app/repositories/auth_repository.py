from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import User

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        return user
