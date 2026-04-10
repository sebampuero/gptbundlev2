import logging

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.runnables.base import Runnable
from langchain_openrouter import ChatOpenRouter

from gptbundle.common.config import settings

logger = logging.getLogger(__name__)


def _get_session_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(session_id, url=settings.REDIS_URL)


def get_chain(llm_model: str, reasoning_effort: str | None = None) -> Runnable:
    if reasoning_effort:
        llm = ChatOpenRouter(model=llm_model, reasoning={"effort": reasoning_effort})
    else:
        llm = ChatOpenRouter(model=llm_model)
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    chain = prompt | llm
    conversational_chain = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=_get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    return conversational_chain
