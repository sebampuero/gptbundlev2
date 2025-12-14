import pytest
from sqlmodel import Session
from src.common.db import engine


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
        
    from src.user.models import User
    from sqlmodel import delete
    
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
    from src.main import app
    from src.common.db import get_pg_db

    def get_session_override():
        return session

    app.dependency_overrides[get_pg_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
