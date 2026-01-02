import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from gptbundle.common.config import settings
from gptbundle.common.db import get_pg_db
from gptbundle.security.service import generate_access_token, generate_refresh_token

from .exceptions import UserAlreadyExistsError
from .models import UserCreate, UserLogin, UserRegister, UserResponse
from .service import create_user, login

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_pg_db)]
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=UserResponse,
    responses={409: {"description": "Username or email is already taken."}},
)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    user_create = UserCreate.model_validate(user_in)
    try:
        user = create_user(session=session, user_create=user_create)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail="Username or email is already taken.",
        ) from e
    return user


@router.post(
    "/login",
    response_model=UserResponse,
    responses={403: {"description": "Invalid username or password"}},
)
def login_user(session: SessionDep, user_in: UserLogin, response: Response) -> Any:
    user = login(session=session, user=user_in)
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Invalid username or password",
        )
    access_token = generate_access_token(user.email)
    refresh_token = generate_refresh_token(user.email)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEVELOPMENT_MODE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEVELOPMENT_MODE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )
    return user
