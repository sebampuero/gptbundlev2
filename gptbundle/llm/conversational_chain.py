import logging

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableField
from langchain_core.runnables.base import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openrouter import ChatOpenRouter

from .chat_message_history_wrapper import get_chat_history

logger = logging.getLogger(__name__)


def get_chain() -> Runnable:
    llm = ChatOpenRouter(model_name="gpt-4o").configurable_fields(
        model_name=ConfigurableField(
            id="llm_model",
            name="LLM Model",
            description="The LLM model to use",
        ),
        reasoning=ConfigurableField(
            id="reasoning_effort",
            name="Reasoning Effort",
            description="The reasoning configuration (can be None)",
        ),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm
    conversational_chain = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return conversational_chain
