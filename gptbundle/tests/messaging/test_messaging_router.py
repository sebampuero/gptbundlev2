import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from gptbundle.common.config import settings
from gptbundle.messaging.repository import ChatRepository
from gptbundle.messaging.schemas import (
    ChatCreate,
    MessageCreate,
    MessageRole,
    WebSocketMessage,
    WebSocketMessageType,
)
from gptbundle.messaging.service import create_chat
from gptbundle.security.service import generate_access_token


def is_valid_uuid4(uuid_string: str) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return uuid_obj.version == 4
    except ValueError:
        return False


def create_test_chat(
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
    chat = create_chat(chat_repo=chat_repo, chat_in=chat_in, es_repo=es_repo)
    return chat.chat_id, chat.timestamp


def test_retrieve_chat_success(
    client: TestClient, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = "test_get_api@example.com"
    chat_id, timestamp = create_test_chat(
        es_repo=es_repo, user_email=user_email, content="Found me"
    )
    cleanup_chats.append((chat_id, timestamp))
    cleanup_es.append(chat_id)

    # Retrieve it
    token = generate_access_token(user_email)
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["chat_id"] == chat_id
    assert content["user_email"] == user_email


def test_retrieve_chat_not_found(client: TestClient):
    chat_id = "non_existent_chat"
    timestamp = datetime.now().timestamp()

    token = generate_access_token("not_found@example.com")
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


def test_retrieve_chats_success(
    client: TestClient, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = "multi_chat_user@example.com"

    # Create two chats
    c1_id, c1_ts = create_test_chat(
        es_repo=es_repo, user_email=user_email, content="Msg 1"
    )
    cleanup_chats.append((c1_id, c1_ts))
    cleanup_es.append(c1_id)

    c2_id, c2_ts = create_test_chat(
        es_repo=es_repo, user_email=user_email, content="Msg 2"
    )
    cleanup_chats.append((c2_id, c2_ts))
    cleanup_es.append(c2_id)

    # Retrieve all
    token = generate_access_token(user_email)
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats", cookies={"access_token": token}
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, dict)
    assert "items" in content
    assert len(content["items"]) == 2


def test_retrieve_chats_not_found(client: TestClient):
    token = generate_access_token("nobody@example.com")
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats", cookies={"access_token": token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chats not found"


def test_retrieve_chats_pagination(
    client: TestClient, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = "paginated_user@example.com"

    # Create 3 chats
    for i in range(3):
        c_id, c_ts = create_test_chat(
            es_repo=es_repo, user_email=user_email, content=f"Msg {i}"
        )
        cleanup_chats.append((c_id, c_ts))
        cleanup_es.append(c_id)

    token = generate_access_token(user_email)

    # Test limit=2
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats?limit=2",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["items"]) == 2
    assert content["last_eval_key"] is not None

    # Test second page
    last_key = json.dumps(content["last_eval_key"])
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats?limit=2&last_eval_key={last_key}",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["items"]) == 1
    assert content["last_eval_key"] is None


def test_delete_chat_success(
    client: TestClient, cleanup_chats: list, es_repo, cleanup_es: list
):
    user_email = "test_delete_api@example.com"
    chat_id, timestamp = create_test_chat(
        es_repo=es_repo, user_email=user_email, content="To be deleted"
    )
    cleanup_es.append(chat_id)
    # No need to add to cleanup_chats since we're deleting it

    # Delete the chat
    token = generate_access_token(user_email)
    delete_response = client.delete(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert delete_response.status_code == 200

    # Verify it's deleted
    get_response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert get_response.status_code == 404


def test_delete_chat_not_found(client: TestClient):
    chat_id = "non_existent_delete_chat"
    timestamp = datetime.now().timestamp()

    token = generate_access_token("delete_not_found@example.com")
    response = client.delete(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        cookies={"access_token": token},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


def test_websocket_chat_endpoint_first_connection(
    client: TestClient, cleanup_chats: list, es_repo, cleanup_es: list
):
    total_response = ""

    payload = {
        "user_message": {
            "content": "Hello, please repeat this as is: 'I am a test model!'",
            "role": MessageRole.USER,
            "message_type": "text",
            "media_s3_keys": None,
            "llm_model": "openrouter/mistralai/devstral-2512:free",
        },
        "user_email": "test@email.com",
    }

    token = generate_access_token("test@email.com")
    with client.websocket_connect(
        f"{settings.API_V1_STR}/messaging/chat/text_ws/new/0",
        cookies={"access_token": token},
    ) as websocket:
        websocket.send_json(payload)
        while True:
            message = websocket.receive_json()
            ws_msg: WebSocketMessage = WebSocketMessage.model_validate(message)

            if ws_msg.type == WebSocketMessageType.NEW_CHAT:
                assert is_valid_uuid4(ws_msg.chat_id)
                assert ws_msg.chat_timestamp > 0
                cleanup_chats.append((ws_msg.chat_id, ws_msg.chat_timestamp))
                cleanup_es.append(ws_msg.chat_id)
            elif ws_msg.type == WebSocketMessageType.TOKEN:
                total_response += ws_msg.content
            elif ws_msg.type == WebSocketMessageType.STREAM_FINISHED:
                break
            elif ws_msg.type == WebSocketMessageType.ERROR:
                pytest.fail(f"Websocket error: {ws_msg.content}")

    assert "I am a test model!" in total_response


def test_websocket_string_timestamp(
    client: TestClient, cleanup_chats: list, es_repo, cleanup_es: list
):
    """Test that the websocket can handle a string timestamp from the client."""
    chat_id = str(uuid.uuid4())
    timestamp_str = str(datetime.now().timestamp())
    total_data = []

    payload = {
        "user_message": {
            "content": "Hello",
            "role": MessageRole.USER,
            "message_type": "text",
            "llm_model": "openrouter/mistralai/devstral-2512:free",
        },
        "chat_id": chat_id,
        "timestamp": timestamp_str,
    }

    token = generate_access_token("test_string_ts@email.com")
    with client.websocket_connect(
        f"{settings.API_V1_STR}/messaging/chat/text_ws",
        cookies={"access_token": token},
    ) as websocket:
        websocket.send_json(payload)
        while True:
            message = websocket.receive_json()
            ws_msg: WebSocketMessage = WebSocketMessage.model_validate(message)
            total_data.append(ws_msg)

            if ws_msg.type == WebSocketMessageType.STREAM_FINISHED:
                break
            elif ws_msg.type == WebSocketMessageType.ERROR:
                pytest.fail(f"Websocket error: {ws_msg.content}")

    # Cleanup
    cleanup_chats.append((chat_id, float(timestamp_str)))
    cleanup_es.append(chat_id)

    assert len(total_data) > 0
