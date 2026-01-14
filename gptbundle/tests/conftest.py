import pytest
from sqlmodel import Session

from gptbundle.common.db import engine


@pytest.fixture
def session():
    """
    Fixture to provide a session for tests.
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(name="cleanup_users")
def cleanup_users_fixture(session: Session):
    """
    Fixture to track and delete users created during tests.
    Usage:
        def test_something(session, cleanup_users):
            user = create_user(...)
            cleanup_users.append(user.id)
    """
    user_ids = []
    yield user_ids

    if not user_ids:
        return

    from sqlmodel import delete

    from gptbundle.user.models import User

    for user_id in user_ids:
        statement = delete(User).where(User.id == user_id)
        session.exec(statement)
    session.commit()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Fixture to provide a TestClient with overridden database dependency.
    """
    from fastapi.testclient import TestClient

    from gptbundle.common.db import get_pg_db
    from gptbundle.main import app

    def get_session_override():
        return session

    app.dependency_overrides[get_pg_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="cleanup_chats")
def cleanup_chats_fixture():
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
            Chat.get(chat_id, timestamp).delete()
        except Chat.DoesNotExist:
            pass


@pytest.fixture(name="es_repo")
def es_repo_fixture():
    """
    Fixture to provide an ElasticsearchRepository instance.
    """
    from gptbundle.messaging.elasticsearch_repository import ElasticsearchRepository

    return ElasticsearchRepository()


@pytest.fixture(name="cleanup_es")
def cleanup_es_fixture(es_repo):
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
            es_repo.delete_chat(chat_id)
        except Exception:
            pass
