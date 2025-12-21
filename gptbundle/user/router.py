from typing import Any, Annotated
from fastapi import Depends, APIRouter, HTTPException
from gptbundle.common.db import get_pg_db
from sqlmodel import Session
from .models import UserResponse, UserCreate, UserRegister, UserLogin, User

from .service import create_user, get_user_by_email, get_user_by_username, login

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_pg_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    responses={
        409: {"description": "User with this email already exists in the system"}
    },
)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    user = get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = create_user(session=session, user_create=user_create)
    return user


@router.post(
    "/login",
    response_model=UserResponse,
    responses={
        404: {"description": "User with this username does not exist in the system"}
    },
)
def login_user(session: SessionDep, user_in: UserLogin) -> Any:
    user = get_user_by_username(session=session, username=user_in.username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = login(session=session, user=user_in)
    return user
