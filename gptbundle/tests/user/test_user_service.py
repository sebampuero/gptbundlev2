from sqlmodel import Session

from gptbundle.user.models import UserCreate, UserLogin
from gptbundle.user.service import (
    activate_user,
    create_user,
    deactivate_user,
    delete_user_by_email,
    get_user_by_email,
    get_user_by_username,
    login,
)


def test_create_user(session: Session, cleanup_users: list):
    email = "test_create@example.com"
    username = "test_create_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)

    user = create_user(user_create, session)
    cleanup_users.append(user.id)

    assert user.email == email
    assert user.username == username
    assert user.id is not None
    assert user.hashed_password != password

    # Verify in DB
    db_user = get_user_by_email(email, session)
    assert db_user is not None
    assert db_user.id == user.id


def test_get_user_by_email(session: Session, cleanup_users: list):
    email = "test_email@example.com"
    username = "test_email_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = create_user(user_create, session)
    cleanup_users.append(user.id)

    # Test success
    found_user = get_user_by_email(email, session)
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == email

    # Test failure
    not_found = get_user_by_email("nonexistent@example.com", session)
    assert not_found is None


def test_get_user_by_username(session: Session, cleanup_users: list):
    email = "test_username@example.com"
    username = "test_username_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = create_user(user_create, session)
    cleanup_users.append(user.id)

    # Test success
    found_user = get_user_by_username(username, session)
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.username == username

    # Test failure
    not_found = get_user_by_username("nonexistent_user", session)
    assert not_found is None


def test_login(session: Session, cleanup_users: list):
    email = "test_login@example.com"
    username = "test_login_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = create_user(user_create, session)
    cleanup_users.append(user.id)

    # Test success
    login_data = UserLogin(username=username, password=password)
    logged_in_user = login(login_data, session)
    assert logged_in_user is not None
    assert logged_in_user.id == user.id

    # Test wrong username
    bad_username_data = UserLogin(username="wrong_user", password=password)
    assert login(bad_username_data, session) is None

    # Test wrong password
    bad_password_data = UserLogin(username=username, password="wrong_password")
    assert login(bad_password_data, session) is None


def test_delete_user_by_email_success(session: Session):
    email = "test_delete@example.com"
    username = "test_delete_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    create_user(user_create, session)

    assert get_user_by_email(email, session) is not None

    result = delete_user_by_email(email, session)
    assert result is True

    assert get_user_by_email(email, session) is None


def test_delete_user_by_email_not_found(session: Session):
    result = delete_user_by_email("nonexistent@example.com", session)
    assert result is False


def test_deactivate_user(session: Session, cleanup_users: list):
    email = "test_deactivate@example.com"
    username = "test_deactivate_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = create_user(user_create, session)
    cleanup_users.append(user.id)

    assert user.is_active is True

    result = deactivate_user(email, session)
    assert result is True

    db_user = get_user_by_email(email, session)
    assert db_user is None


def test_activate_user(session: Session, cleanup_users: list):
    email = "test_reactivate@example.com"
    username = "test_reactivate_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = create_user(user_create, session)
    cleanup_users.append(user.id)

    # Deactivate
    deactivate_user(email, session)
    assert get_user_by_email(email, session) is None

    # Reactivate
    result = activate_user(email, session)
    assert result is True

    db_user = get_user_by_email(email, session)
    assert db_user is not None
    assert db_user.is_active is True
