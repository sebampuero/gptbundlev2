from .models import Chat as ChatModel
from .schemas import ChatCreate, Chat, MessageCreate
from typing import List
from pynamodb.exceptions import DeleteError

class ChatRepository:
    def create_chat(self, chat_in: ChatCreate) -> Chat:
        messages_data = [msg.model_dump() for msg in chat_in.messages]
        created_chat = ChatModel(
            chat_id=chat_in.chat_id,
            timestamp=chat_in.timestamp,
            user_email=chat_in.user_email,
            messages=messages_data,
        )
        created_chat.save()
        return Chat.model_validate(created_chat)

    def get_chat(self, chat_id: str, timestamp: float) -> Chat | None:
        try:
            chat_model = ChatModel.get(chat_id, timestamp)
            return self._create_chat_from_model(chat_model)
        except ChatModel.DoesNotExist:
            return None

    def get_chats_by_user_email(self, user_email: str) -> list[Chat]:
        chats = ChatModel.user_email_index.query(user_email)
        return [self._create_chat_from_model(chat) for chat in chats]
    
    def append_messages(self, chat_id: str, timestamp: float, messages: List[MessageCreate]) -> bool:
        try:
            chat_model = ChatModel.get(chat_id, timestamp)
            chat_model.messages.extend([msg.model_dump() for msg in messages])
            chat_model.save()
            return True
        except ChatModel.DoesNotExist:
            return False
    
    def delete_chat(self, chat_id: str, timestamp: float) -> bool:
        try:
            chat_model = ChatModel.get(chat_id, timestamp)
            chat_model.delete()
            return True
        except (ChatModel.DoesNotExist, DeleteError) as e:
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
                    media=msg.media,
                    llm_model=msg.llm_model) for msg in chat_model.messages
            ],
        )
