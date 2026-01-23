import logging
from typing import Any

from pynamodb.exceptions import DeleteError, PutError

from .exceptions import ChatAlreadyExistsError
from .models import Chat as ChatModel
from .schemas import Chat, ChatCreate, MessageCreate

logger = logging.getLogger(__name__)


class ChatRepository:
    def create_chat(self, chat_in: ChatCreate) -> Chat:
        messages_data = [msg.model_dump() for msg in chat_in.messages]
        created_chat = ChatModel(
            chat_id=chat_in.chat_id,
            timestamp=chat_in.timestamp,
            user_email=chat_in.user_email,
            messages=messages_data,
        )
        try:
            created_chat.save(condition=ChatModel.chat_id.does_not_exist())
        except PutError as e:
            raise ChatAlreadyExistsError(
                f"Chat with id {chat_in.chat_id} already exists"
            ) from e

        logger.debug(
            f"Created chat for user: {chat_in.user_email} "
            f"with chat_id: {chat_in.chat_id} and "
            f"timestamp: {chat_in.timestamp}"
        )
        return Chat.model_validate(created_chat)

    def get_chat(self, chat_id: str, timestamp: float, user_email: str) -> Chat | None:
        try:
            chat_model = ChatModel.get(chat_id, timestamp)
            if chat_model.user_email != user_email:
                logger.info(
                    f"User: {user_email} is not authorized "
                    f"to retrieve chat: {chat_id} and "
                    f"timestamp: {timestamp}"
                )
                return None
            logger.debug(
                f"Retrieved chat for user: {user_email} "
                f"with chat_id: {chat_id} and "
                f"timestamp: {timestamp}"
            )
            return self._create_chat_from_model(chat_model)
        except ChatModel.DoesNotExist:
            return None

    def get_chats_by_user_email(self, user_email: str) -> list[Chat]:
        chats = ChatModel.user_email_index.query(user_email)
        logger.debug(f"Retrieved chats for user: {user_email}")
        return [self._create_chat_from_model(chat) for chat in chats]

    def get_chats_by_user_email_paginated(
        self,
        user_email: str,
        limit: int | None = None,
        last_evaluated_key: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        query_args: dict[str, Any] = {"scan_index_forward": False}
        if limit:
            query_args["limit"] = limit
        if last_evaluated_key:
            query_args["last_evaluated_key"] = last_evaluated_key

        chats_iterator = ChatModel.user_email_index.query(user_email, **query_args)
        items = [self._create_chat_from_model(chat) for chat in chats_iterator]

        logger.debug(f"Retrieved paginated chats for user: {user_email}")
        return {
            "items": items,
            "last_eval_key": chats_iterator.last_evaluated_key,
        }

    def append_messages(
        self,
        chat_id: str,
        timestamp: float,
        messages: list[MessageCreate],
        user_email: str,
    ) -> bool:
        try:
            chat_model = ChatModel.get(chat_id, timestamp)
            if chat_model.user_email != user_email:
                logger.info(
                    f"User: {user_email} is not authorized to "
                    f"append messages to chat: {chat_id} and "
                    f"timestamp: {timestamp}"
                )
                return False
            chat_model.messages.extend([msg.model_dump() for msg in messages])
            chat_model.save()
            logger.debug(
                f"Appended messages to chat: {chat_id} and timestamp: {timestamp}"
            )
            return True
        except ChatModel.DoesNotExist:
            return False

    def delete_chat(self, chat_id: str, timestamp: float, user_email: str) -> bool:
        try:
            chat_model = ChatModel.get(chat_id, timestamp)
            if chat_model.user_email != user_email:
                logger.info(
                    f"User: {user_email} is not authorized to "
                    f"delete chat: {chat_id} and "
                    f"timestamp: {timestamp}"
                )
                return False
            chat_model.delete()
            logger.debug(f"Deleted chat: {chat_id} and timestamp: {timestamp}")
            return True
        except (ChatModel.DoesNotExist, DeleteError):
            return False

    def _create_chat_from_model(self, chat_model: ChatModel) -> Chat:
        return Chat(
            chat_id=chat_model.chat_id,
            timestamp=chat_model.timestamp,
            user_email=chat_model.user_email,
            messages=[
                MessageCreate(
                    content=msg.content,
                    role=msg.role,
                    message_type=msg.message_type,
                    media_s3_keys=msg.media_s3_keys,
                    llm_model=msg.llm_model,
                )
                for msg in chat_model.messages
            ],
        )
