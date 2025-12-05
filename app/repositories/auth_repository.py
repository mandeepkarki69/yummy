from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from app.models.user_model import User, PasswordResetCode

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        return user

    async def get_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_reset_code(self, user_id: int, code: str, expires_at: datetime):
        reset = PasswordResetCode(user_id=user_id, code=code, expires_at=expires_at, used=False)
        self.db.add(reset)
        await self.db.commit()
        await self.db.refresh(reset)
        return reset

    async def get_valid_reset_code(self, user_id: int, code: str):
        result = await self.db.execute(
            select(PasswordResetCode).where(
                PasswordResetCode.user_id == user_id,
                PasswordResetCode.code == code,
                PasswordResetCode.used == False,
                PasswordResetCode.expires_at > datetime.now(timezone.utc),
            ).order_by(PasswordResetCode.created_at.desc())
        )
        return result.scalars().first()

    async def get_latest_reset_code(self, user_id: int):
        result = await self.db.execute(
            select(PasswordResetCode)
            .where(PasswordResetCode.user_id == user_id)
            .order_by(PasswordResetCode.created_at.desc())
        )
        return result.scalars().first()

    async def mark_reset_used(self, reset: PasswordResetCode):
        reset.used = True
        await self.db.commit()
        await self.db.refresh(reset)
        return reset

    async def update_user(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user
