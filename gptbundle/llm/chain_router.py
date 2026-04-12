import logging

from langchain_core.runnables.base import Runnable

from .conversational_chain import get_chain as get_conversational_chain
from .rag_chain import get_chain as get_rag_chain
from .rag_chain import ingest_pdf

logger = logging.getLogger(__name__)


class ChainRouter:
    def __init__(self):
        self._conversational_chain: Runnable | None = None
        self._rag_chain: Runnable | None = None
        self._chat_id_to_type: dict[str, str] = {}

    def route(
        self,
        use_rag: bool,
        chat_id: str,
        is_rag_chat: bool = False,
    ) -> Runnable:
        if use_rag or is_rag_chat or self._chat_id_to_type.get(chat_id) == "rag":
            logger.debug(f"Routing to RAG chain for chat_id: {chat_id}")

            if self._chat_id_to_type.get(chat_id) != "rag":
                logger.info(f"Chat {chat_id} promoted to RAG mode.")
                self._chat_id_to_type[chat_id] = "rag"

            if use_rag:
                logger.info(f"Ingesting files for chat_id: {chat_id}")
                ingest_pdf(chat_id)

            if self._rag_chain is None:
                logger.info("Initializing singleton RAG chain")
                self._rag_chain = get_rag_chain()
            return self._rag_chain

        logger.debug(f"Routing to conversational chain for chat_id: {chat_id}")
        if self._conversational_chain is None:
            logger.info("Initializing singleton conversational chain")
            self._conversational_chain = get_conversational_chain()
        return self._conversational_chain


router = ChainRouter()
