import asyncio
import logging

from fastapi import WebSocket

from gptbundle.common.config import settings
from gptbundle.llm.chat_factory import msg_schema_to_lc_base_message
from gptbundle.llm.chat_message_history_wrapper import ChatMessageHistoryWrapper
from gptbundle.llm.exceptions import ModelDoesNotSupportReasoningEffortError
from gptbundle.llm.service import generate_text_response
from gptbundle.media_storage.storage import move_file

from .elasticsearch_repository import ElasticsearchRepository
from .exceptions import ChatAlreadyExistsError
from .repository import ChatRepository
from .schemas import (
    ChatCreate,
    MessageCreate,
    MessageRole,
    WebSocketMessage,
    WebSocketMessageType,
)
from .service import append_messages, create_chat, get_chat

logger = logging.getLogger(__name__)


async def process_attachments(user_message: MessageCreate, chat_id: str) -> None:
    if user_message.img_s3_keys:
        for s3_key in user_message.img_s3_keys:
            await asyncio.to_thread(
                move_file,
                s3_key,
                s3_key.replace(settings.S3_TEMP_PREFIX, settings.S3_PERMANENT_PREFIX),
            )
        user_message.img_s3_keys = [
            s3_key.replace(settings.S3_TEMP_PREFIX, settings.S3_PERMANENT_PREFIX)
            for s3_key in user_message.img_s3_keys
        ]

    if user_message.pdf_s3_keys:
        for i, s3_key in enumerate(user_message.pdf_s3_keys):
            new_key = s3_key.replace(
                settings.S3_TEMP_PREFIX,
                f"{settings.S3_PERMANENT_PREFIX}{settings.S3_DOC_PREFIX}{chat_id}/",
            )
            await asyncio.to_thread(move_file, s3_key, new_key)
            user_message.pdf_s3_keys[i] = new_key


async def save_user_message(
    user_email: str,
    user_message: MessageCreate,
    active_chat_id: str,
    active_timestamp: float,
    chat_repo: ChatRepository,
    es_repo: ElasticsearchRepository,
) -> bool:
    try:
        chat_in = ChatCreate(
            user_email=user_email,
            messages=[user_message],
            chat_id=active_chat_id,
            timestamp=active_timestamp,
        )
        logger.debug(f"Creating new chat for user: {user_email}")
        await create_chat(chat_repo=chat_repo, chat_in=chat_in, es_repo=es_repo)
        logger.debug(
            f"Created new chat for user: {user_email} "
            f"with chat_id: {active_chat_id} and "
            f"timestamp: {active_timestamp}"
        )
        return True
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
        return result_of_append
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return False


async def prepare_chat_history(
    active_chat_id: str,
    active_timestamp: float,
    user_email: str,
    chat_repo: ChatRepository,
) -> bool:
    chat = await get_chat(
        chat_id=active_chat_id,
        timestamp=active_timestamp,
        chat_repo=chat_repo,
        user_email=user_email,
    )

    if chat:
        history_wrapper = ChatMessageHistoryWrapper(session_id=active_chat_id)
        history_wrapper.clear()
        lc_messages = [msg_schema_to_lc_base_message(m) for m in chat.messages]
        for msg in lc_messages:
            history_wrapper.add_message(msg)
        return chat.is_rag
    return False


async def stream_ai_response(
    websocket: WebSocket,
    user_message: MessageCreate,
    active_chat_id: str,
    active_timestamp: float,
    user_email: str,
    chat_repo: ChatRepository,
    es_repo: ElasticsearchRepository,
    is_rag_chat: bool = False,
) -> None:
    llm_model = user_message.llm_model
    ai_message = MessageCreate(
        content="", role=MessageRole.ASSISTANT, llm_model=llm_model
    )

    try:
        async for token in generate_text_response(
            user_message, active_chat_id, is_rag_chat
        ):
            ai_message.content += token
            await websocket.send_json(
                WebSocketMessage(
                    type=WebSocketMessageType.TOKEN, content=token
                ).model_dump()
            )
    except ModelDoesNotSupportReasoningEffortError as e:
        logger.error(
            f"Error during LLM generation: {e}", exc_info=True, stack_info=True
        )
        await websocket.send_json(
            WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content="The model does not support reasoning effort. "
                "Please try with another model.",
            ).model_dump()
        )
        return
    except Exception as e:
        logger.error(f"Error during LLM generation: {e}")
        await websocket.send_json(
            WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content="There was an error, please try again later.",
            ).model_dump()
        )
        return

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
            WebSocketMessage(type=WebSocketMessageType.STREAM_FINISHED).model_dump()
        )
    except Exception as e:
        logger.error(f"Error persisting AI message: {e}")
        await websocket.send_json(
            WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content="There was an error processing the AI Message, "
                "please try again.",
            ).model_dump()
        )
