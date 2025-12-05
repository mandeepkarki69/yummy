# app/services/auth_services.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import secrets

from app.repositories.auth_repository import AuthRepository
from app.utils.oauth2 import create_access_token, create_refresh_token, verify_refresh_token, revoke_token
from app.utils.security import verify_password, get_password_hash
from app.schema.user_schema import LoginResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.utils.email_sender import send_email, EmailNotConfigured


class AuthServices:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)
        self.otp_expiry_minutes = 2

    def _generate_otp(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

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

        access_token = create_access_token({
                "user_id": user.id,
                "role": user.role
         })
        refresh_token = create_refresh_token({
                "user_id": user.id,
                "role": user.role
        })

        # Return full LoginResponse structure
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.name,
            "email": user.email,
            "user_role": user.role
        }

    async def refresh(self, refresh_token: str):
        payload = verify_refresh_token(refresh_token)
        user = await self.repo.get_by_id(payload["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        access_token = create_access_token({
            "user_id": user.id,
            "role": user.role
        })
        # Rotate refresh token to reduce replay window
        new_refresh = create_refresh_token({
            "user_id": user.id,
            "role": user.role
        })
        revoke_token(refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.name,
            "email": user.email,
            "user_role": user.role,
        }

    async def logout(self, access_token: str, refresh_token: str | None = None):
        revoke_token(access_token)
        if refresh_token:
            revoke_token(refresh_token)
        return {"message": "Logged out"}

    async def _send_reset_code(self, user, code: str):
        try:
            send_email(
                to_email=user.email,
                subject="Your password reset code",
                body=(
                    f"Hi {user.name},\n\n"
                    f"Your OTP for password reset is: {code}\n"
                    f"This code expires in {self.otp_expiry_minutes} minutes.\n\n"
                    "If you did not request this, you can ignore this email."
                ),
            )
        except EmailNotConfigured:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email service not configured")

    async def forgot_password(self, data: ForgotPasswordRequest):
        user = await self.repo.login(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

        latest = await self.repo.get_latest_reset_code(user.id)
        now = datetime.now(timezone.utc)
        if latest and not latest.used and latest.expires_at > now and (latest.created_at + timedelta(minutes=2)) > now:
            remaining = int((latest.created_at + timedelta(minutes=2) - now).total_seconds() // 1)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OTP already sent. Please wait {remaining} seconds before requesting a new one.",
            )

        code = self._generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.otp_expiry_minutes)
        await self.repo.create_reset_code(user.id, code, expires_at)
        await self._send_reset_code(user, code)
        return {"message": "OTP sent"}

    async def reset_password(self, data: ResetPasswordRequest):
        user = await self.repo.login(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP or email")

        reset_entry = await self.repo.get_valid_reset_code(user.id, data.otp)
        if not reset_entry:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

        user.password = get_password_hash(data.new_password)
        await self.repo.update_user(user)
        await self.repo.mark_reset_used(reset_entry)
        return {"message": "Password updated successfully"}
