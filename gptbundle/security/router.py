import logging
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response

from gptbundle.common.config import settings

from .service import generate_access_token, validate_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/refresh-token")
def refresh_token(
    response: Response, refresh_token: Annotated[str | None, Cookie()] = None
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is required")

    if not validate_jwt_token(token=refresh_token):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = generate_access_token(username=refresh_token)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEVELOPMENT_MODE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return "Refreshed access token."
