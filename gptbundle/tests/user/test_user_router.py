from fastapi.testclient import TestClient
from sqlmodel import Session

from gptbundle.common.config import settings


def test_register_user_success(client: TestClient, cleanup_users: list[int]):
    response = client.post(
        f"{settings.API_V1_STR}/user/register",
        json={
            "email": "test_api@example.com",
            "password": "password123",
            "username": "api_test_user",
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == "test_api@example.com"
    assert "id" in content
    assert "password" not in content
    cleanup_users.append(content["id"])


def test_register_user_duplicate_email(
    client: TestClient, session: Session, cleanup_users: list[int]
):
    from gptbundle.user.models import UserCreate
    from gptbundle.user.service import create_user

    user_in = UserCreate(
        email="duplicate@example.com", password="password123", username="duplicate_user"
    )
    user = create_user(session=session, user_create=user_in)
    cleanup_users.append(user.id)

    response = client.post(
        f"{settings.API_V1_STR}/user/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "username": "api_test_user_2",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Username or email is already taken."


def test_login_user_success(
    client: TestClient, session: Session, cleanup_users: list[int]
):
    from gptbundle.user.models import UserCreate
    from gptbundle.user.service import create_user

    user_in = UserCreate(
        email="login_test@example.com", password="password123", username="login_user"
    )
    user = create_user(session=session, user_create=user_in)
    cleanup_users.append(user.id)

    response = client.post(
        f"{settings.API_V1_STR}/user/login",
        json={"username": "login_user", "password": "password123"},
    )
    assert response.status_code == 200
    content = response.json()
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None
    assert refresh_token is not None
    assert content["email"] == "login_test@example.com"


def test_login_user_not_found(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/user/login",
        json={"username": "non_existent_user", "password": "password123"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid username or password"


def test_register_user_disabled(client: TestClient):
    from unittest.mock import patch

    with patch("gptbundle.user.router.settings.ALLOW_REGISTRATION", False):
        response = client.post(
            f"{settings.API_V1_STR}/user/register",
            json={
                "email": "disabled@example.com",
                "password": "password123",
                "username": "disabled_user",
            },
        )
        assert response.status_code == 422
        assert response.json()["detail"] == "Registration is currently disabled."
