from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.schema.user_schema import UserCreate, AdminCreate, AdminRegisterVerify, AdminRegisterResend
from app.utils.oauth2 import create_access_token
from app.utils.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.email_sender import send_email, EmailNotConfigured
import secrets
import string
from datetime import datetime, timedelta, timezone

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.otp_expiry_minutes = 2

    def _generate_password(self, length: int = 8) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _generate_otp(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    def _ensure_passwords_match(self, password: str, confirm: str):
        if password != confirm:
            raise HTTPException(status_code=400, detail="Password does not match")

    async def get_user(self, user_id: int):
        return await self.repo.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str):
        
        return await self.repo.get_user_by_email(email)
    
    async def get_all_users(self, admin_id: int):
        return await self.repo.get_all_users(admin_id)

    async def create_user(self, user_data: UserCreate, admin_id: int):
        plain_password = user_data.password or self._generate_password()
        hashed_password = get_password_hash(plain_password)
        user_data.password = hashed_password
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role= user_data.role,
            created_by=admin_id
        )
        created = await self.repo.create_user(user)
        try:
            send_email(
                to_email=created.email,
                subject="Your Yummy account credentials",
                body=(
                    f"Hi {created.name},\n\n"
                    "An account has been created for you.\n\n"
                    f"Email: {created.email}\n"
                    f"Password: {plain_password}\n\n"
                    "Please log in and change your password after first sign-in."
                ),
            )
        except EmailNotConfigured:
            # Skip silently if SMTP is not configured
            pass
        return created
    
    async def create_admin_user(self, user_data: AdminCreate):
        self._ensure_passwords_match(user_data.password, user_data.confirm_password)

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

    async def _send_admin_otp(self, email: str, code: str, name: str):
        try:
            send_email(
                to_email=email,
                subject="Your admin registration OTP",
                body=(
                    f"Hi {name},\n\n"
                    f"Your OTP for admin registration is: {code}\n"
                    f"This code expires in {self.otp_expiry_minutes} minutes.\n\n"
                    "If you did not request this, you can ignore this email."
                ),
            )
        except EmailNotConfigured:
            raise HTTPException(status_code=500, detail="Email service not configured")

    async def admin_register_request(self, data: AdminCreate):
        self._ensure_passwords_match(data.password, data.confirm_password)
        existing = await self.repo.get_user_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        latest = await self.repo.get_latest_admin_register_code(data.email)
        now = datetime.now(timezone.utc)
        if latest and not latest.used and latest.expires_at > now and (latest.created_at + timedelta(minutes=2)) > now:
            remaining = int((latest.created_at + timedelta(minutes=2) - now).total_seconds() // 1)
            raise HTTPException(status_code=400, detail=f"OTP already sent. Please wait {remaining} seconds before requesting a new one.")

        code = self._generate_otp()
        expires_at = now + timedelta(minutes=self.otp_expiry_minutes)
        await self.repo.create_admin_register_code(data.email, code, expires_at)
        await self._send_admin_otp(data.email, code, data.name)
        return {"message": "OTP sent"}

    async def admin_register_verify(self, data: AdminRegisterVerify):
        self._ensure_passwords_match(data.password, data.confirm_password)
        existing = await self.repo.get_user_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        entry = await self.repo.get_valid_admin_register_code(data.email, data.otp)
        if not entry:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        hashed_password = get_password_hash(data.password)
        user = User(
            name=data.name,
            email=data.email,
            password=hashed_password,
            role="admin"
        )
        created_user = await self.repo.create_admin_user(user)
        await self.repo.mark_admin_register_code_used(entry, created_user.id)

        token = create_access_token({"user_id": created_user.id, "role": created_user.role})
        return {
            "id": created_user.id,
            "name": created_user.name,
            "email": created_user.email,
            "role": created_user.role,
            "access_token": token,
            "token_type": "bearer"
        }

    async def admin_register_resend(self, data: AdminRegisterResend):
        latest = await self.repo.get_latest_admin_register_code(data.email)
        now = datetime.now(timezone.utc)
        if latest and not latest.used and latest.expires_at > now and (latest.created_at + timedelta(minutes=2)) > now:
            remaining = int((latest.created_at + timedelta(minutes=2) - now).total_seconds() // 1)
            raise HTTPException(status_code=400, detail=f"OTP already sent. Please wait {remaining} seconds before requesting a new one.")

        existing = await self.repo.get_user_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        code = self._generate_otp()
        expires_at = now + timedelta(minutes=self.otp_expiry_minutes)
        await self.repo.create_admin_register_code(data.email, code, expires_at)
        await self._send_admin_otp(data.email, code, data.email.split("@")[0])
        return {"message": "OTP sent"}


    
    
    
    
    
    
    
