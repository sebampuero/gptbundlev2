import json
import uuid
from datetime import datetime

import pytest

from gptbundle.common.config import settings
from gptbundle.messaging.repository import ChatRepository
from gptbundle.messaging.schemas import (
    ChatCreate,
    MessageCreate,
    MessageRole,
)
from gptbundle.messaging.service import create_chat
from gptbundle.security.service import generate_access_token


def is_valid_uuid4(uuid_string: str) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return uuid_obj.version == 4
    except ValueError:
        return False


async def create_test_chat(
    es_repo,
    chat_id: str | None = None,
    timestamp: float | None = None,
    user_email: str = "test@example.com",
    content: str = "Test message",
) -> tuple[str, float]:
    chat_repo = ChatRepository()
    chat_id = chat_id or str(uuid.uuid4())
    timestamp = timestamp or datetime.now().timestamp()

    kwargs = {
        "user_email": user_email,
        "messages": [
            MessageCreate(
                content=content,
                role=MessageRole.USER,
                message_type="text",
                llm_model="gpt4",
            )
        ],
        "chat_id": chat_id,
        "timestamp": timestamp,
    }

    chat_in = ChatCreate(**kwargs)
    chat = await create_chat(chat_repo=chat_repo, chat_in=chat_in, es_repo=es_repo)
    return chat.chat_id, chat.timestamp


@pytest.mark.asyncio
async def test_retrieve_chat_success(
    client, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = "test_get_api@example.com"
    chat_id, timestamp = await create_test_chat(
        es_repo=es_repo, user_email=user_email, content="Found me"
    )
    cleanup_chats.append((chat_id, timestamp))
    cleanup_es.append(chat_id)

    # Retrieve it
    token = generate_access_token(user_email)
    response = await client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["chat_id"] == chat_id
    assert content["user_email"] == user_email


@pytest.mark.asyncio
async def test_retrieve_chat_not_found(client):
    chat_id = "non_existent_chat"
    timestamp = datetime.now().timestamp()

    token = generate_access_token("not_found@example.com")
    response = await client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


@pytest.mark.asyncio
async def test_retrieve_chats_success(
    client, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = f"multi_chat_user_{uuid.uuid4().hex[:8]}@example.com"

    # Create two chats
    c1_id, c1_ts = await create_test_chat(
        es_repo=es_repo, user_email=user_email, content="Msg 1"
    )
    cleanup_chats.append((c1_id, c1_ts))
    cleanup_es.append(c1_id)

    c2_id, c2_ts = await create_test_chat(
        es_repo=es_repo, user_email=user_email, content="Msg 2"
    )
    cleanup_chats.append((c2_id, c2_ts))
    cleanup_es.append(c2_id)

    # Retrieve all
    token = generate_access_token(user_email)
    response = await client.get(
        f"{settings.API_V1_STR}/messaging/chats", cookies={"access_token": token}
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, dict)
    assert "items" in content
    assert len(content["items"]) == 2


@pytest.mark.asyncio
async def test_retrieve_chats_not_found(client):
    token = generate_access_token("nobody@example.com")
    response = await client.get(
        f"{settings.API_V1_STR}/messaging/chats", cookies={"access_token": token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chats not found"


@pytest.mark.asyncio
async def test_retrieve_chats_pagination(
    client, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = f"paginated_user_{uuid.uuid4().hex[:8]}@example.com"

    # Create 3 chats
    for i in range(3):
        c_id, c_ts = await create_test_chat(
            es_repo=es_repo, user_email=user_email, content=f"Msg {i}"
        )
        cleanup_chats.append((c_id, c_ts))
        cleanup_es.append(c_id)

    token = generate_access_token(user_email)

    # Test limit=2
    response = await client.get(
        f"{settings.API_V1_STR}/messaging/chats?limit=2",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["items"]) == 2
    assert content["last_eval_key"] is not None

    # Test second page
    last_key = json.dumps(content["last_eval_key"])
    response = await client.get(
        f"{settings.API_V1_STR}/messaging/chats?limit=2&last_eval_key={last_key}",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["items"]) == 1
    assert content["last_eval_key"] is None


@pytest.mark.asyncio
async def test_delete_chat_success(
    client, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = "test_delete_api@example.com"
    chat_id, timestamp = await create_test_chat(
        es_repo=es_repo, user_email=user_email, content="To be deleted"
    )
    cleanup_es.append(chat_id)
    # No need to add to cleanup_chats since we're deleting it

    # Delete the chat
    token = generate_access_token(user_email)
    delete_response = await client.delete(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert delete_response.status_code == 200

    # Verify it's deleted
    get_response = await client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_chat_not_found(client):
    chat_id = "non_existent_delete_chat"
    timestamp = datetime.now().timestamp()

    token = generate_access_token("delete_not_found@example.com")
    response = await client.delete(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"
