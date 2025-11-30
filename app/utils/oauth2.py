from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES

# Simple in-memory revocation set; note this resets on restart
REVOKED_TOKENS: set[str] = set()


def _create_token(data: dict, expires_minutes: int, token_type: str):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "token_type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    return _create_token(data, ACCESS_TOKEN_EXPIRE_MINUTES, token_type="access")


def create_refresh_token(data: dict):
    return _create_token(data, REFRESH_TOKEN_EXPIRE_MINUTES, token_type="refresh")


def revoke_token(token: str):
    REVOKED_TOKENS.add(token)


def verify_token(token: str, credentials_exception, expected_type: str = "access"):
    if token in REVOKED_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        token_type: str = payload.get("token_type", "access")

        if user_id is None or role is None or token_type != expected_type:
            raise credentials_exception

        return {
            "user_id": user_id,
            "role": role
        }

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return verify_token(token, credentials_exception, expected_type="access")


def verify_refresh_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_token(token, credentials_exception, expected_type="refresh")
