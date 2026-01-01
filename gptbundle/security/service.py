import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Cookie
from passlib.context import CryptContext

from gptbundle.common.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def generate_access_token(subject: str) -> str:
    to_encode = {
        "sub": subject,
        "exp": datetime.now(UTC)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def generate_refresh_token(subject: str) -> str:
    to_encode = {
        "sub": subject,
        "exp": datetime.now(UTC)
        + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def get_current_user(
    token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> str | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        logger.error(f"Token expired: {token}")
        return None
    except jwt.InvalidTokenError:
        logger.error(f"Invalid token: {token}")
        return None
    except Exception as e:
        logger.error(f"Unknown error when validating token: {e}")
        return None
