import logging

from langchain_core.runnables.base import Runnable

from .conversational_chain import get_chain as get_conversational_chain
from .rag_chain import get_chain as get_rag_chain

logger = logging.getLogger(__name__)


class ChainRouter:
    def __init__(self):
        # a chat can have the two types of chains: normal and rag
        # we store both for each chat_id
        self._chat_id_to_chain: dict[str, dict[str, Runnable]] = {}

    def route(
        self,
        use_rag: bool,
        chat_id: str,
        llm_model: str,
        reasoning_effort: str | None = None,
    ) -> Runnable:
        if use_rag:
            logger.debug(f"Using RAG chain for chat_id: {chat_id}")
            if chat_id not in self._chat_id_to_chain:
                self._chat_id_to_chain[chat_id] = {}
            if "rag" not in self._chat_id_to_chain[chat_id]:
                self._chat_id_to_chain[chat_id]["rag"] = get_rag_chain(
                    chat_id, llm_model, reasoning_effort
                )
            return self._chat_id_to_chain[chat_id]["rag"]
        else:
            logger.debug(f"Using conversational chain for chat_id: {chat_id}")
            if chat_id not in self._chat_id_to_chain:
                self._chat_id_to_chain[chat_id] = {}
            if "conversational" not in self._chat_id_to_chain[chat_id]:
                self._chat_id_to_chain[chat_id]["conversational"] = (
                    get_conversational_chain(llm_model, reasoning_effort)
                )
            return self._chat_id_to_chain[chat_id]["conversational"]


router = ChainRouter()
