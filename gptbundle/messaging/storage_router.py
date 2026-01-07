import asyncio
import logging
import os
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from gptbundle.messaging.storage import upload_file
from gptbundle.security.service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

UserEmailDep = Annotated[str, Depends(get_current_user)]


@router.post(
    "/upload_media",
    responses={
        401: {"description": "User not authenticated"},
        500: {"description": "Internal server error"},
    },
)
async def upload_media(
    user_email: UserEmailDep,
    files: list[UploadFile],
) -> Any:
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    generated_keys = []
    try:
        for file in files:
            # TODO: do a better verification of file extension and types,
            # do not rely on file extension only
            file_ext = os.path.splitext(file.filename or "")[1]
            unique_id = str(uuid.uuid4())
            key = f"temp/{unique_id}{file_ext}"
            file_content = await file.read()
            await asyncio.to_thread(upload_file, file_content, key)

            generated_keys.append(key)

        return {"keys": generated_keys}

    except Exception as e:
        logger.error(f"Error while uploading media for user {user_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
