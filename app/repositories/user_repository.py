from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import User, PasswordResetCode, AdminRegisterCode
from datetime import datetime, timezone

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

    async def mark_reset_used(self, reset: PasswordResetCode):
        reset.used = True
        await self.db.commit()
        await self.db.refresh(reset)
        return reset

    async def update_user(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_admin_register_code(self, email: str, code: str, expires_at: datetime):
        entry = AdminRegisterCode(email=email, code=code, expires_at=expires_at, used=False)
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_latest_admin_register_code(self, email: str):
        result = await self.db.execute(
            select(AdminRegisterCode)
            .where(AdminRegisterCode.email == email)
            .order_by(AdminRegisterCode.created_at.desc())
        )
        return result.scalars().first()

    async def get_valid_admin_register_code(self, email: str, code: str):
        result = await self.db.execute(
            select(AdminRegisterCode).where(
                AdminRegisterCode.email == email,
                AdminRegisterCode.code == code,
                AdminRegisterCode.used == False,
                AdminRegisterCode.expires_at > datetime.now(timezone.utc),
            ).order_by(AdminRegisterCode.created_at.desc())
        )
        return result.scalars().first()

    async def mark_admin_register_code_used(self, entry: AdminRegisterCode, user_id: int):
        entry.used = True
        entry.user_id = user_id
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
