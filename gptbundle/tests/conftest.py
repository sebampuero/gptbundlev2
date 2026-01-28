import asyncio

import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest_asyncio.fixture(loop_scope="function")
async def engine_fixture():
    """
    Fixture to provide a fresh engine for each test.
    This ensures the engine is bound to the current event loop.
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    from gptbundle.common.config import settings

    engine = create_async_engine(str(settings.sqlalchemy_database_uri))
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="function")
async def session(engine_fixture):
    """
    Fixture to provide a session for tests.
    """
    async with AsyncSession(engine_fixture) as session:
        yield session


@pytest_asyncio.fixture(name="cleanup_users", loop_scope="function")
async def cleanup_users_fixture():
    """
    Fixture to track and delete users created during tests.
    """
    user_ids = []
    yield user_ids

    if not user_ids:
        return

    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlmodel import delete

    from gptbundle.common.config import settings
    from gptbundle.user.models import User

    engine = create_async_engine(str(settings.sqlalchemy_database_uri))
    async with AsyncSession(engine) as session:
        for user_id in user_ids:
            statement = delete(User).where(User.id == user_id)
            await session.exec(statement)
        await session.commit()
    await engine.dispose()


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession):
    """
    Fixture to provide an AsyncClient with overridden database dependency.
    """
    from httpx import ASGITransport, AsyncClient

    from gptbundle.common.db import get_pg_db
    from gptbundle.main import app

    def get_session_override():
        return session

    app.dependency_overrides[get_pg_db] = get_session_override

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(name="cleanup_chats")
async def cleanup_chats_fixture():
    """
    Fixture to track and delete chats created during tests.
    Usage:
        def test_something(cleanup_chats):
            chat = create_chat(...)
            cleanup_chats.append((chat.chat_id, chat.timestamp))
    """
    chat_keys = []
    yield chat_keys

    if not chat_keys:
        return

    from gptbundle.messaging.models import Chat

    for chat_id, timestamp in chat_keys:
        try:
            await asyncio.to_thread(Chat.get, chat_id, timestamp).delete()
        except Chat.DoesNotExist:
            pass


@pytest_asyncio.fixture(name="es_repo")
async def es_repo_fixture():
    """
    Fixture to provide an ElasticsearchRepository instance.
    """
    from gptbundle.messaging.elasticsearch_repository import ElasticsearchRepository

    # is this why singleton is not very wanted?
    # because testing it is "clunky"
    ElasticsearchRepository._client = None
    yield ElasticsearchRepository()
    ElasticsearchRepository._client.close()


@pytest_asyncio.fixture(name="cleanup_es")
async def cleanup_es_fixture(es_repo):
    """
    Fixture to track and delete Elasticsearch documents created during tests.
    Usage:
        def test_something(cleanup_es):
            cleanup_es.append(chat_id)
    """
    chat_ids = []
    yield chat_ids

    if not chat_ids:
        return

    for chat_id in chat_ids:
        try:
            await es_repo.delete_chat(chat_id)
        except Exception:
            pass
