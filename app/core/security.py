from datetime import datetime, timedelta, timezone
import uuid

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(data: dict) -> str:
    payload = data.copy()
    payload.update(
        {
            "type": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.EXPIRE_MINUTES),
        }
    )

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def generate_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload.update(
        {
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_EXPIRE_DAYS),
        }
    )

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")

    return payload


def verify_refresh_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    return payload
