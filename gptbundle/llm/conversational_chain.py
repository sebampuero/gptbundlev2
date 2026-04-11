import logging

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.runnables.base import Runnable
from langchain_openrouter import ChatOpenRouter

from .chat_message_history_wrapper import ChatMessageHistoryWrapper

logger = logging.getLogger(__name__)


def get_chain(
    chat_id: str, llm_model: str, reasoning_effort: str | None = None
) -> Runnable:
    if reasoning_effort:
        llm = ChatOpenRouter(model=llm_model, reasoning={"effort": reasoning_effort})
    else:
        llm = ChatOpenRouter(model=llm_model)
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    history_wrapper = ChatMessageHistoryWrapper(chat_id)

    chain = prompt | llm
    conversational_chain = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=history_wrapper.get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return conversational_chain
