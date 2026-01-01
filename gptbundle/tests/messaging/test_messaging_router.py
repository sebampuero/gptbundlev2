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


def is_valid_uuid4(uuid_string: str) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return uuid_obj.version == 4
    except ValueError:
        return False


def create_test_chat(
    chat_id: str | None = None,
    timestamp: float | None = None,
    user_email: str = "test@example.com",
    content: str = "Test message",
) -> tuple[str, float]:
    chat_repo = ChatRepository()
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
    }
    if chat_id is not None:
        kwargs["chat_id"] = chat_id
    if timestamp is not None:
        kwargs["timestamp"] = timestamp

    chat_in = ChatCreate(**kwargs)
    chat = create_chat(chat_repo=chat_repo, chat_in=chat_in)
    return chat.chat_id, chat.timestamp


def test_retrieve_chat_success(client: TestClient, cleanup_chats: list):
    user_email = "test_get_api@example.com"
    chat_id, timestamp = create_test_chat(user_email=user_email, content="Found me")
    cleanup_chats.append((chat_id, timestamp))

    # Retrieve it
    response = client.get(f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}")
    assert response.status_code == 200
    content = response.json()
    assert content["chat_id"] == chat_id
    assert content["user_email"] == user_email


def test_retrieve_chat_not_found(client: TestClient):
    chat_id = "non_existent_chat"
    timestamp = datetime.now().timestamp()

    response = client.get(f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


def test_retrieve_chats_success(client: TestClient, cleanup_chats: list):
    user_email = "multi_chat_user@example.com"

    # Create two chats
    c1_id, c1_ts = create_test_chat(user_email=user_email, content="Msg 1")
    cleanup_chats.append((c1_id, c1_ts))

    c2_id, c2_ts = create_test_chat(user_email=user_email, content="Msg 2")
    cleanup_chats.append((c2_id, c2_ts))

    # Retrieve all
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats/{user_email}",
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) == 2


def test_retrieve_chats_not_found(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/messaging/chats/nobody@example.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Chats not found"


def test_delete_chat_success(client: TestClient, cleanup_chats: list):
    user_email = "test_delete_api@example.com"
    chat_id, timestamp = create_test_chat(
        user_email=user_email, content="To be deleted"
    )
    # No need to add to cleanup_chats since we're deleting it

    # Delete the chat
    delete_response = client.delete(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}"
    )
    assert delete_response.status_code == 200

    # Verify it's deleted
    get_response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}"
    )
    assert get_response.status_code == 404


def test_delete_chat_not_found(client: TestClient):
    chat_id = "non_existent_delete_chat"
    timestamp = datetime.now().timestamp()

    response = client.delete(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


def test_websocket_chat_endpoint_first_connection(
    client: TestClient, cleanup_chats: list
):
    chat_payload = {
        "user_email": "test@email.com",
        "messages": [
            {
                "content": "Hello, please repeat this as is: 'I am a test model!'",
                "role": MessageRole.USER,
                "message_type": "text",
                "media": None,
                "llm_model": "openrouter/mistralai/devstral-2512:free",
            }
        ],
    }
    total_response = ""

    with client.websocket_connect(
        f"{settings.API_V1_STR}/messaging/chat/text_ws/new/0"
    ) as websocket:
        websocket.send_json(chat_payload)
        while True:
            message = websocket.receive_json()
            ws_msg: WebSocketMessage = WebSocketMessage.model_validate(message)

            if ws_msg.type == WebSocketMessageType.NEW_CHAT:
                assert is_valid_uuid4(ws_msg.chat_id)
                assert ws_msg.chat_timestamp > 0
                cleanup_chats.append((ws_msg.chat_id, ws_msg.chat_timestamp))
            elif ws_msg.type == WebSocketMessageType.TOKEN:
                total_response += ws_msg.content
            elif ws_msg.type == WebSocketMessageType.STREAM_FINISHED:
                break
            elif ws_msg.type == WebSocketMessageType.ERROR:
                pytest.fail(f"Websocket error: {ws_msg.content}")

    assert "I am a test model!" in total_response


def test_websocket_chat_endpoint_existing_chat_several_messages(
    client: TestClient, cleanup_chats: list
):
    chat_id = "some_test_id"
    timestamp = datetime.now().timestamp()
    user_email = "test@email.com"
    chat_id, timestamp = create_test_chat(user_email=user_email, content="Dummy")
    cleanup_chats.append((chat_id, timestamp))
    chat_payload = {
        "user_email": user_email,
        "messages": [
            {
                "content": "Hello, please repeat this as is: 'I am a test model!'",
                "role": MessageRole.USER,
                "message_type": "text",
                "media": None,
                "llm_model": "openrouter/mistralai/devstral-2512:free",
            },
            {
                "content": "I am a test model!",
                "role": MessageRole.ASSISTANT,
                "message_type": "text",
                "media": None,
                "llm_model": "openrouter/mistralai/devstral-2512:free",
            },
            {
                "content": "Now say 'Bye!'",
                "role": MessageRole.USER,
                "message_type": "text",
                "media": None,
                "llm_model": "openrouter/mistralai/devstral-2512:free",
            },
        ],
    }
    total_response = ""

    with client.websocket_connect(
        f"{settings.API_V1_STR}/messaging/chat/text_ws/{chat_id}/{timestamp}"
    ) as websocket:
        websocket.send_json(chat_payload)
        while True:
            message = websocket.receive_json()
            ws_msg: WebSocketMessage = WebSocketMessage.model_validate(message)
            assert ws_msg.type != WebSocketMessageType.NEW_CHAT
            if ws_msg.type == WebSocketMessageType.TOKEN:
                total_response += ws_msg.content
            elif ws_msg.type == WebSocketMessageType.STREAM_FINISHED:
                break
            elif ws_msg.type == WebSocketMessageType.ERROR:
                pytest.fail(f"Websocket error: {ws_msg.content}")

    assert "Bye!" in total_response

    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats/{user_email}",
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1  # should exist only one chat and not have created two
