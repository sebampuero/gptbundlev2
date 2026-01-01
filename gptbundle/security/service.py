import logging
from datetime import UTC, datetime, timedelta

import jwt
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


def validate_jwt_token(token: str) -> bool:
    try:
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        logger.error(f"Token expired: {token}")
        return False
    except jwt.InvalidTokenError:
        logger.error(f"Invalid token: {token}")
        return False
    except Exception as e:
        logger.error(f"Unknown error when validating token: {e}")
        return False
