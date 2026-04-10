from collections.abc import Sequence

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

from gptbundle.common.config import settings


class ChatMessageHistoryWrapper(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.message_history = RedisChatMessageHistory(
            session_id, url=settings.REDIS_URL
        )

    @property
    def messages(self) -> list[BaseMessage]:
        return self.message_history.messages

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        self.message_history.add_messages(messages)

    def clear(self) -> None:
        self.message_history.clear()

    def get_history(self) -> BaseChatMessageHistory:
        """
        Returns the wrapper itself.
        This function can be passed to RunnableWithMessageHistory's get_session_history.
        """
        return self
