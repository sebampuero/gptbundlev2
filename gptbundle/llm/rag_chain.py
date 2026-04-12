import logging

from langchain_chroma import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import S3DirectoryLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.runnables import (
    ConfigurableField,
    RunnableConfig,
    RunnableLambda,
    RunnableWithMessageHistory,
)
from langchain_core.runnables.base import Runnable
from langchain_core.vectorstores import VectorStore
from langchain_mistralai import MistralAIEmbeddings
from langchain_openrouter import ChatOpenRouter
from langchain_text_splitters import RecursiveCharacterTextSplitter

from gptbundle.common.config import settings

from .chat_message_history_wrapper import get_chat_history

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


def _get_document_loader(prefix: str) -> S3DirectoryLoader:
    return S3DirectoryLoader(
        bucket=settings.S3_BUCKET_NAME,
        prefix=prefix,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    )


def _get_vector_store(chat_id: str):
    return Chroma(
        collection_name=f"{settings.VECTOR_STORE_COLLECTION_NAME}_{chat_id}",
        embedding_function=MistralAIEmbeddings(
            model=settings.MISTRAL_EMBED_MODEL,
            api_key=settings.MISTRAL_API_KEY,
        ),
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
    )


def _ingest(vector_store: VectorStore, loader: BaseLoader):
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.SPLITTER_CHUNK_SIZE,
        chunk_overlap=settings.SPLITTER_CHUNK_OVERLAP,
        add_start_index=True,
    )
    vector_store.add_documents(documents=text_splitter.split_documents(docs))


def ingest_pdf(chat_id: str):
    loader = _get_document_loader(
        f"{settings.S3_PERMANENT_PREFIX}{settings.S3_DOC_PREFIX}{chat_id}/"
    )
    vector_store = _get_vector_store(chat_id)
    _ingest(vector_store, loader)


def _get_dynamic_retriever(query: str, config: RunnableConfig):
    session_id = config["configurable"].get("session_id")
    if not session_id:
        logger.error("session_id not found in config for dynamic retriever")
        raise ValueError("session_id is required")

    vector_store = _get_vector_store(session_id)
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    )
    return retriever.invoke(query, config=config)


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

    retriever = RunnableLambda(_get_dynamic_retriever)

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

    rag_chain_with_history = RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=get_chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return rag_chain_with_history
