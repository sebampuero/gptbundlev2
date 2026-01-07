import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, UploadFile

from gptbundle.security.service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

UserEmailDep = Annotated[str, Depends(get_current_user)]


@router.post(
    "/upload_media",
    responses={
        401: {"description": "User not authenticated"},
    },
)
def upload_media(
    user_email: UserEmailDep,
    files: list[UploadFile],
) -> Any:
    pass
