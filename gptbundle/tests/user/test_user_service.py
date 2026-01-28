import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

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


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, cleanup_users: list):
    email = "test_create@example.com"
    username = "test_create_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)

    user = await create_user(user_create, session)
    cleanup_users.append(user.id)

    assert user.email == email
    assert user.username == username
    assert user.id is not None
    assert user.hashed_password != password

    # Verify in DB
    db_user = await get_user_by_email(email, session)
    assert db_user is not None
    assert db_user.id == user.id


@pytest.mark.asyncio
async def test_get_user_by_email(session: AsyncSession, cleanup_users: list):
    email = "test_email@example.com"
    username = "test_email_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = await create_user(user_create, session)
    cleanup_users.append(user.id)

    # Test success
    found_user = await get_user_by_email(email, session)
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == email

    # Test failure
    not_found = await get_user_by_email("nonexistent@example.com", session)
    assert not_found is None


@pytest.mark.asyncio
async def test_get_user_by_username(session: AsyncSession, cleanup_users: list):
    email = "test_username@example.com"
    username = "test_username_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = await create_user(user_create, session)
    cleanup_users.append(user.id)

    # Test success
    found_user = await get_user_by_username(username, session)
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.username == username

    # Test failure
    not_found = await get_user_by_username("nonexistent_user", session)
    assert not_found is None


@pytest.mark.asyncio
async def test_login(session: AsyncSession, cleanup_users: list):
    email = "test_login@example.com"
    username = "test_login_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = await create_user(user_create, session)
    cleanup_users.append(user.id)

    # Test success
    login_data = UserLogin(username=username, password=password)
    logged_in_user = await login(login_data, session)
    assert logged_in_user is not None
    assert logged_in_user.id == user.id

    # Test wrong username
    bad_username_data = UserLogin(username="wrong_user", password=password)
    assert await login(bad_username_data, session) is None

    # Test wrong password
    bad_password_data = UserLogin(username=username, password="wrong_password")
    assert await login(bad_password_data, session) is None


@pytest.mark.asyncio
async def test_delete_user_by_email_success(session: AsyncSession):
    email = "test_delete@example.com"
    username = "test_delete_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    await create_user(user_create, session)

    assert await get_user_by_email(email, session) is not None

    result = await delete_user_by_email(email, session)
    assert result is True

    assert await get_user_by_email(email, session) is None


@pytest.mark.asyncio
async def test_delete_user_by_email_not_found(session: AsyncSession):
    result = await delete_user_by_email("nonexistent@example.com", session)
    assert result is False


@pytest.mark.asyncio
async def test_deactivate_user(session: AsyncSession, cleanup_users: list):
    email = "test_deactivate@example.com"
    username = "test_deactivate_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = await create_user(user_create, session)
    cleanup_users.append(user.id)

    assert user.is_active is True

    result = await deactivate_user(email, session)
    assert result is True

    db_user = await get_user_by_email(email, session)
    assert db_user is None


@pytest.mark.asyncio
async def test_activate_user(session: AsyncSession, cleanup_users: list):
    email = "test_reactivate@example.com"
    username = "test_reactivate_user"
    password = "password123"

    user_create = UserCreate(email=email, username=username, password=password)
    user = await create_user(user_create, session)
    cleanup_users.append(user.id)

    # Deactivate
    await deactivate_user(email, session)
    assert await get_user_by_email(email, session) is None

    # Reactivate
    result = await activate_user(email, session)
    assert result is True

    db_user = await get_user_by_email(email, session)
    assert db_user is not None
    assert db_user.is_active is True
