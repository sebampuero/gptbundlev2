import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket
from starlette.websockets import WebSocketDisconnect

from gptbundle.llm.service import generate_text_response
from gptbundle.security.service import get_current_user

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
UserEmailDep = Annotated[str, Depends(get_current_user)]


@router.get(
    "/chat/{chat_id}/{timestamp}",
    response_model=Chat,
    responses={
        404: {"description": "Chat not found"},
        401: {"description": "User not authenticated"},
    },
)
def retrieve_chat(
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
    chat = get_chat(
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
def retrieve_chats(
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

    chats_response = get_chats_by_user_email_paginated(
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
def remove_chat(
    chat_repo: ChatRepositoryDep,
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
    deleted = delete_chat(
        chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp, user_email=user_email
    )
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )


@router.websocket("/chat/text_ws/{chat_id}/{timestamp}")
async def websocket_text_generation_endpoint(
    websocket: WebSocket,
    chat_repo: ChatRepositoryDep,
    chat_id: str,
    timestamp: float,
    user_email: UserEmailDep,
):
    """This websocket endpoint handles the text generation for a chat."""
    await websocket.accept()

    active_chat_id = None if chat_id == "new" else chat_id
    active_timestamp = None if timestamp == 0 else timestamp

    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    while True:
        try:
            data = await websocket.receive_json()

            if "messages" not in data or not isinstance(data["messages"], list):
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR,
                        content="Invalid message format",
                    ).model_dump()
                )
                continue

            if active_chat_id is None and active_timestamp is None:
                try:
                    logger.debug(f"Creating new chat for user: {user_email}")
                    chat_in = ChatCreate(
                        user_email=user_email,
                        messages=[
                            MessageCreate.model_validate(m) for m in data["messages"]
                        ],
                    )
                    chat = create_chat(chat_repo=chat_repo, chat_in=chat_in)
                    active_chat_id = chat.chat_id
                    active_timestamp = chat.timestamp
                    logger.debug(
                        f"Created new chat for user: {user_email} "
                        f"with chat_id: {active_chat_id} and "
                        f"timestamp: {active_timestamp}"
                    )
                    await websocket.send_json(
                        WebSocketMessage(
                            type=WebSocketMessageType.NEW_CHAT,
                            chat_id=active_chat_id,
                            chat_timestamp=active_timestamp,
                        ).model_dump()
                    )
                except Exception as e:
                    await websocket.send_json(
                        WebSocketMessage(
                            type=WebSocketMessageType.ERROR,
                            content=f"Failed to create chat: {str(e)}",
                        ).model_dump()
                    )
                    continue
            else:
                try:
                    new_messages = [
                        MessageCreate.model_validate(m) for m in data["messages"]
                    ]
                    result_of_append = append_messages(
                        chat_repo=chat_repo,
                        chat_id=active_chat_id,
                        timestamp=active_timestamp,
                        messages=new_messages,
                        user_email=user_email,
                    )
                    if not result_of_append:
                        await websocket.send_json(
                            WebSocketMessage(
                                type=WebSocketMessageType.ERROR,
                                content="Failed to append messages",
                            ).model_dump()
                        )
                        continue
                except Exception as e:
                    await websocket.send_json(
                        WebSocketMessage(
                            type=WebSocketMessageType.ERROR,
                            content=f"Failed to append messages: {str(e)}",
                        ).model_dump()
                    )
                    continue

            last_message = data["messages"][-1]
            llm_model = last_message.get(
                "llm_model", "openrouter/mistralai/devstral-2512:free"
            )  # default free model

            ai_message = MessageCreate(
                content="", role=MessageRole.ASSISTANT, llm_model=llm_model
            )

            try:
                async for chunk in await generate_text_response(data):
                    token = chunk.choices[0].delta.content
                    if token:
                        ai_message.content += token
                        await websocket.send_json(
                            WebSocketMessage(
                                type=WebSocketMessageType.TOKEN, content=token
                            ).model_dump()
                        )

                append_messages(
                    chat_repo=chat_repo,
                    chat_id=active_chat_id,
                    timestamp=active_timestamp,
                    messages=[ai_message],
                    user_email=user_email,
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
                logger.error(f"Error during LLM generation: {e}")
                await websocket.send_json(
                    WebSocketMessage(
                        type=WebSocketMessageType.ERROR, content=f"LLM Error: {str(e)}"
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
