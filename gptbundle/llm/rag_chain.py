import logging

from langchain_chroma import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import S3FileLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.runnables.base import Runnable
from langchain_core.vectorstores import VectorStore
from langchain_mistralai import MistralAIEmbeddings
from langchain_openrouter import ChatOpenRouter
from langchain_text_splitters import RecursiveCharacterTextSplitter

from gptbundle.common.config import settings

from .chat_message_history_wrapper import ChatMessageHistoryWrapper

logger = logging.getLogger(__name__)

contextualize_q_system_prompt = """
    Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
    """

system_prompt = """
    You are a helpful assistant.
    Your job is to answer questions based on the given context.
    \n\n
    Context: {context}
    """


def _get_document_loader(file_key: str) -> S3FileLoader:
    return S3FileLoader(
        bucket=settings.S3_BUCKET_NAME,
        key=file_key,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    )


def _get_vector_store():
    return Chroma(  # TODO: it shouldn't be created for every chat
        # maybe use the server version or pinecone?
        collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
        embedding_function=MistralAIEmbeddings(
            model=settings.MISTRAL_EMBED_MODEL,
            api_key=settings.MISTRAL_API_KEY,
        ),
    )


def _ingest(vector_store: VectorStore, loader: BaseLoader):
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.SPLITTER_CHUNK_SIZE,
        chunk_overlap=settings.SPLITTER_CHUNK_OVERLAP,
        add_start_index=True,
    )
    vector_store.add_documents(documents=text_splitter.split_documents(docs))


def _build_chain(chat_id: str, llm_model: str, reasoning_effort: str | None = None):
    loader = _get_document_loader(f"permanent/{chat_id}.pdf")
    vector_store = _get_vector_store()
    _ingest(vector_store, loader)
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    )
    logger.debug(f"Using retriever with config specs: {retriever.config_specs}")
    if reasoning_effort:
        llm = ChatOpenRouter(model=llm_model, reasoning={"effort": reasoning_effort})
    else:
        llm = ChatOpenRouter(model=llm_model)
    logger.info(f"Using LLM: {llm_model}")
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    history_wrapper = ChatMessageHistoryWrapper(chat_id)

    rag_chain_with_history = RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=history_wrapper.get_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    return rag_chain_with_history


def get_chain(
    chat_id: str, llm_model: str, reasoning_effort: str | None = None
) -> Runnable:
    return _build_chain(chat_id, llm_model, reasoning_effort)
