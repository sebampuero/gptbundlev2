import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket
from starlette.websockets import WebSocketDisconnect

from gptbundle.llm.service import generate_image_response, generate_text_response
from gptbundle.media_storage.storage import move_file
from gptbundle.security.service import get_current_user

from .elasticsearch_repository import ElasticsearchRepository
from .exceptions import ChatAlreadyExistsError
from .repository import ChatRepository
from .schemas import (
    Chat,
    ChatCreate,
    ChatPaginatedResponse,
    MessageCreate,
    MessageRole,
    WebSocketMessage,
    WebSocketMessageType,
)
from .search_service import search_chats_by_keyword
from .service import (
    append_messages,
    create_chat,
    delete_chat,
    get_chat,
    get_chats_by_user_email_paginated,
)

logger = logging.getLogger(__name__)

router = APIRouter()

ChatRepositoryDep = Annotated[ChatRepository, Depends(ChatRepository)]
ElasticsearchRepositoryDep = Annotated[
    ElasticsearchRepository, Depends(ElasticsearchRepository)
]
UserEmailDep = Annotated[str, Depends(get_current_user)]


@router.get(
    "/chat/{chat_id}/{timestamp}",
    response_model=Chat,
    responses={
        404: {"description": "Chat not found"},
        401: {"description": "User not authenticated"},
    },
)
async def retrieve_chat(
    chat_repo: ChatRepositoryDep,
    chat_id: str,
    timestamp: float,
    user_email: UserEmailDep,
) -> Any:
    logger.info(f"Received GET Request for chat: {chat_id} and timestamp: {timestamp}")
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )
    chat = await get_chat(
        chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp, user_email=user_email
    )
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )
    return chat


@router.get(
    "/chats",
    response_model=ChatPaginatedResponse,
    responses={
        404: {"description": "Chats not found"},
        401: {"description": "User not authenticated"},
    },
)
async def retrieve_chats(
    chat_repo: ChatRepositoryDep,
    user_email: UserEmailDep,
    limit: int | None = Query(None, description="Limit the number of chats returned"),
    last_eval_key: str | None = Query(
        None, description="The last evaluated key for pagination (JSON string)"
    ),
) -> Any:
    logger.info(f"Received GET Request for chats of user: {user_email}")
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    evaluated_key = None
    if last_eval_key:
        try:
            evaluated_key = json.loads(last_eval_key)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid last_eval_key format. Expected JSON string.",
            ) from e

    chats_response = await get_chats_by_user_email_paginated(
        chat_repo=chat_repo,
        user_email=user_email,
        limit=limit,
        last_evaluated_key=evaluated_key,
    )
    if not chats_response["items"]:
        raise HTTPException(
            status_code=404,
            detail="Chats not found",
        )
    return chats_response


@router.delete(
    "/chat/{chat_id}/{timestamp}",
    responses={
        404: {"description": "Chat not found"},
        401: {"description": "User not authenticated"},
    },
)
async def remove_chat(
    chat_repo: ChatRepositoryDep,
    es_repo: ElasticsearchRepositoryDep,
    chat_id: str,
    timestamp: float,
    user_email: UserEmailDep,
) -> Any:
    logger.info(
        f"Received DELETE Request for chat: {chat_id} and timestamp: {timestamp}"
    )
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )
    deleted = await delete_chat(
        chat_repo=chat_repo,
        chat_id=chat_id,
        timestamp=timestamp,
        user_email=user_email,
        es_repo=es_repo,
    )
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )


@router.get(
    "/search_chats",
    response_model=list[Chat],
    responses={
        404: {"description": "Chats not found"},
        401: {"description": "User not authenticated"},
    },
)
async def search_chats(
    es_repo: ElasticsearchRepositoryDep,
    user_email: UserEmailDep,
    search_term: str,
) -> Any:
    logger.info(
        f"Received GET Request for search_chats for user: {user_email} "
        f"and search_term: {search_term}"
    )
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    chats = await search_chats_by_keyword(
        es_repo=es_repo, user_email=user_email, search_term=search_term
    )
    if not chats:
        raise HTTPException(
            status_code=404,
            detail="Chats not found",
        )
    return chats


@router.post(
    "/image_generation",
    response_model=MessageCreate,
    responses={
        401: {"description": "User not authenticated"},
    },
)
async def generate_image(
    chat_id: str,
    chat_timestamp: float,
    user_email: UserEmailDep,
    user_message: MessageCreate,
    chat_repo: ChatRepositoryDep,
    es_repo: ElasticsearchRepositoryDep,
) -> Any:
    logger.info(
        f"Received POST Request for image generation for "
        f"chat id: {chat_id} and timestamp: {chat_timestamp}"
    )
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )
    response_message = await generate_image_response(user_message)
    logger.debug(f"The generated response message is {response_message}")
    try:
        chat = await create_chat(
            chat_in=ChatCreate(
                user_email=user_email,
                messages=[user_message],
                chat_id=chat_id,
                timestamp=chat_timestamp,
            ),
            chat_repo=chat_repo,
            es_repo=es_repo,
        )
        await append_messages(
            chat_id=chat.chat_id,
            timestamp=chat.timestamp,
            messages=[response_message],
            chat_repo=chat_repo,
            user_email=user_email,
            es_repo=es_repo,
        )
    except ChatAlreadyExistsError as e:
        logger.debug(f"Chat existed already: {e}")
        await append_messages(
            chat_id=chat_id,
            timestamp=chat_timestamp,
            messages=[user_message, response_message],
            chat_repo=chat_repo,
            user_email=user_email,
            es_repo=es_repo,
        )
    except Exception as e:
        logger.error(f"Error creating chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error creating chat",
        ) from e
    return response_message


@router.websocket("/chat/text_ws")
async def websocket_text_generation_endpoint(
    websocket: WebSocket,
    chat_repo: ChatRepositoryDep,
    es_repo: ElasticsearchRepositoryDep,
    user_email: UserEmailDep,
):
    """This websocket endpoint handles the text generation for a chat."""
    await websocket.accept()

    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    while True:
        try:
            data = await websocket.receive_json()

            if "user_message" not in data:
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR,
                        content="Invalid message format",
                    ).model_dump()
                )
                continue

            user_message = MessageCreate.model_validate(data["user_message"])
            active_chat_id = data.get("chat_id")
            active_timestamp_raw = data.get("timestamp")

            try:
                active_timestamp = (
                    float(active_timestamp_raw)
                    if active_timestamp_raw is not None
                    else None
                )
            except (ValueError, TypeError):
                active_timestamp = None

            if active_chat_id is None or active_timestamp is None:
                logger.error(f"Invalid chat_id or timestamp provided: {data}")
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR,
                        content="There was an error, please try again later.",
                    ).model_dump()
                )
                continue

            if user_message.media_s3_keys:
                for s3_key in user_message.media_s3_keys:
                    await asyncio.to_thread(
                        move_file, s3_key, s3_key.replace("temp/", "permanent/")
                    )
                user_message.media_s3_keys = [
                    s3_key.replace("temp/", "permanent/")
                    for s3_key in user_message.media_s3_keys
                ]

            try:
                logger.debug(f"Creating new chat for user: {user_email}")
                chat_in = ChatCreate(
                    user_email=user_email,
                    messages=[user_message],
                    chat_id=active_chat_id,
                    timestamp=active_timestamp,
                )
                await create_chat(chat_repo=chat_repo, chat_in=chat_in, es_repo=es_repo)
                logger.debug(
                    f"Created new chat for user: {user_email} "
                    f"with chat_id: {active_chat_id} and "
                    f"timestamp: {active_timestamp}"
                )
            except ChatAlreadyExistsError:
                logger.debug(f"Chat {active_chat_id} exists, appending message")
                result_of_append = await append_messages(
                    chat_repo=chat_repo,
                    chat_id=active_chat_id,
                    timestamp=active_timestamp,
                    messages=[user_message],
                    user_email=user_email,
                    es_repo=es_repo,
                )
                if not result_of_append:
                    await websocket.send_json(
                        WebSocketMessage(
                            type=WebSocketMessageType.ERROR,
                            content="Failed to append message to existing chat",
                        ).model_dump()
                    )
                    continue
            except Exception as e:
                logger.error(f"Error processing chat message: {e}")
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR,
                        content="There was an error, please try again later.",
                    ).model_dump()
                )
                continue

            llm_model = user_message.llm_model

            ai_message = MessageCreate(
                content="", role=MessageRole.ASSISTANT, llm_model=llm_model
            )
            user_chat = get_chat(
                active_chat_id, active_timestamp, chat_repo, user_email
            )

            try:
                async for chunk in await generate_text_response(user_chat):
                    token = chunk.choices[0].delta.content
                    if token:
                        ai_message.content += token
                        await websocket.send_json(
                            WebSocketMessage(
                                type=WebSocketMessageType.TOKEN, content=token
                            ).model_dump()
                        )
            except Exception as e:
                logger.error(f"Error during LLM generation: {e}")
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR,
                        content="The LLM had an error, please try again later.",
                    ).model_dump()
                )
                continue

            try:
                await append_messages(
                    chat_repo=chat_repo,
                    chat_id=active_chat_id,
                    timestamp=active_timestamp,
                    messages=[ai_message],
                    user_email=user_email,
                    es_repo=es_repo,
                )
                logger.debug(
                    f"Appended AI message to chat: {active_chat_id} "
                    f"and timestamp: {active_timestamp}"
                )
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.STREAM_FINISHED
                    ).model_dump()
                )
            except Exception as e:
                logger.error(f"Error persisting AI message: {e}")
                # We don't send an ERROR message here because tokens were already sent
                # but we should signal finish if possible or just log it
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.STREAM_FINISHED
                    ).model_dump()
                )

        except WebSocketDisconnect:
            logger.debug(f"WebSocket {websocket.client} disconnected")
            break
        except Exception as e:
            logger.error(f"Unexpected error in websocket {websocket.client}: {e}")
            try:
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR, content="Internal server error"
                    ).model_dump()
                )
            except Exception:
                pass
            break
