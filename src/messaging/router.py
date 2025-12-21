from typing import Any, Annotated, List
from fastapi import Depends, APIRouter, HTTPException, WebSocket
from src.common.db import get_pg_db
from src.llm.service import generate_text_response
from .service import create_chat, get_chat, get_chats_by_user_email, append_messages, delete_chat
from .repository import ChatRepository
from .schemas import ChatCreate, Chat, MessageCreate, WebSocketMessage, MessageRole, WebSocketMessageType
import logging
from starlette.websockets import WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

ChatRepositoryDep = Annotated[ChatRepository, Depends(ChatRepository)]


@router.post(
    "/chat",
    response_model=Chat
)
def new_chat(chat_repo: ChatRepositoryDep, chat_in: ChatCreate) -> Any:
    logger.info(f"Received POST Request for new chat: {chat_in}")
    chat = create_chat(chat_repo=chat_repo, chat_in=chat_in)
    return chat


@router.get(
    "/chat/{chat_id}/{timestamp}",
    response_model=Chat,
    responses={
        404: {"description": "Chat not found"}
    },
) #TODO: add authorization. An authenticated user may request a chat of another user. Maybe we can pass the email along the request
# after the middleware authenticates the user and validates the token
def retrieve_chat(chat_repo: ChatRepositoryDep, chat_id: str, timestamp: float) -> Any:
    logger.info(f"Received GET Request for chat: {chat_id} and timestamp: {timestamp}")
    chat = get_chat(chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp)
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )
    return chat

@router.get(
    "/chats/{user_email}",
    response_model=list[Chat],
    responses={
        404: {"description": "Chats not found"}
    },
) # TODO: paginate this
def retrieve_chats(chat_repo: ChatRepositoryDep, user_email: str) -> Any:
    logger.info(f"Received GET Request for chats of user: {user_email}")
    chats = get_chats_by_user_email(chat_repo=chat_repo, user_email=user_email)
    if not chats:
        raise HTTPException(
            status_code=404,
            detail="Chats not found",
        )
    return chats

@router.delete(
    "/chat/{chat_id}/{timestamp}",
    responses={
        404: {"description": "Chat not found"}
    },
)
def remove_chat(chat_repo: ChatRepositoryDep, chat_id: str, timestamp: float) -> Any:
    logger.info(f"Received DELETE Request for chat: {chat_id} and timestamp: {timestamp}")
    deleted = delete_chat(chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

@router.websocket("/chat/text_ws/{chat_id}/{timestamp}")
async def websocket_text_generation_endpoint(websocket: WebSocket, chat_repo: ChatRepositoryDep, chat_id: str, timestamp: float):
    """This websocket endpoint handles the text generation for a chat."""
    await websocket.accept()
    
    active_chat_id = None if chat_id == "new" else chat_id
    active_timestamp = None if timestamp == 0 else timestamp

    while True:
        try:
            data = await websocket.receive_json()
            
            if "messages" not in data or not isinstance(data["messages"], list):
                await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.ERROR, content="Invalid message format").model_dump())
                continue

            if active_chat_id is None and active_timestamp is None:
                try:
                    logger.info(f"Creating new chat for user: {data.get('user_email')}")
                    chat_in = ChatCreate(
                        user_email=data.get("user_email"),
                        messages=[MessageCreate.model_validate(m) for m in data["messages"]]
                    )
                    chat = create_chat(chat_repo=chat_repo, chat_in=chat_in)
                    active_chat_id = chat.chat_id
                    active_timestamp = chat.timestamp
                    logger.info(f"Created new chat for user: {data.get('user_email')} with chat_id: {active_chat_id} and timestamp: {active_timestamp}")
                    await websocket.send_json(WebSocketMessage(
                        type=WebSocketMessageType.NEW_CHAT, 
                        chat_id=active_chat_id, 
                        timestamp=active_timestamp
                    ).model_dump())
                except Exception as e:
                    await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.ERROR, content=f"Failed to create chat: {str(e)}").model_dump())
                    continue
            else:
                try:
                    new_messages = [MessageCreate.model_validate(m) for m in data["messages"]]
                    append_messages(chat_repo=chat_repo, chat_id=active_chat_id, timestamp=active_timestamp, messages=new_messages)
                except Exception as e:
                    await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.ERROR, content=f"Failed to append messages: {str(e)}").model_dump())
                    continue

            last_message = data["messages"][-1]
            llm_model = last_message.get("llm_model", "openrouter/mistralai/devstral-2512:free") # default free model
            
            ai_message = MessageCreate(
                content="",
                role=MessageRole.ASSISTANT,
                llm_model=llm_model
            )

            try:
                async for chunk in await generate_text_response(data):
                    token = chunk.choices[0].delta.content
                    if token:
                        ai_message.content += token
                        await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.TOKEN, content=token).model_dump())
                
                append_messages(chat_repo=chat_repo, chat_id=active_chat_id, timestamp=active_timestamp, messages=[ai_message])
                logger.info(f"Appended AI message to chat: {active_chat_id} and timestamp: {active_timestamp}")
                await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.STREAM_FINISHED).model_dump())
                
            except Exception as e:
                logger.error(f"Error during LLM generation: {e}")
                await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.ERROR, content=f"LLM Error: {str(e)}").model_dump())

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            break
        except Exception as e:
            logger.error(f"Unexpected error in websocket: {e}")
            try:
                await websocket.send_json(WebSocketMessage(type=WebSocketMessageType.ERROR, content="Internal server error").model_dump())
            except:
                pass
            break