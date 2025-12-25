import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from gptbundle.common.config import settings
from gptbundle.messaging.schemas import (
    MessageRole,
    WebSocketMessage,
    WebSocketMessageType,
)


def is_valid_uuid4(uuid_string: str) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return uuid_obj.version == 4
    except ValueError:
        return False


def test_new_chat_success(client: TestClient, cleanup_chats: list):
    user_email = "test_api@example.com"

    response = client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "user_email": user_email,
            "messages": [
                {
                    "content": "Hello API",
                    "role": MessageRole.USER,
                    "message_type": "text",
                    "llm_model": "gpt4",
                }
            ],
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert is_valid_uuid4(content["chat_id"])
    assert isinstance(content["timestamp"], float)
    assert content["timestamp"] < datetime.now().timestamp()
    assert content["user_email"] == user_email
    assert len(content["messages"]) == 1
    assert content["messages"][0]["content"] == "Hello API"

    cleanup_chats.append((content["chat_id"], content["timestamp"]))


def test_retrieve_chat_success(client: TestClient, cleanup_chats: list):
    chat_id = "test_get_api_chat"
    timestamp = datetime.now().timestamp()
    user_email = "test_get_api@example.com"

    # Create chat first
    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": chat_id,
            "timestamp": timestamp,
            "user_email": user_email,
            "messages": [
                {
                    "content": "Found me",
                    "role": MessageRole.USER,
                    "message_type": "text",
                    "llm_model": "gpt4",
                }
            ],
        },
    )
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
    timestamp = datetime.now().timestamp()

    # Create two chats
    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": "chat_1",
            "timestamp": timestamp,
            "user_email": user_email,
            "messages": [
                {
                    "content": "Msg 1",
                    "role": MessageRole.USER,
                    "message_type": "text",
                    "llm_model": "gpt4",
                }
            ],
        },
    )
    cleanup_chats.append(("chat_1", timestamp))

    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": "chat_2",
            "timestamp": timestamp + 1,
            "user_email": user_email,
            "messages": [
                {
                    "content": "Msg 2",
                    "role": MessageRole.USER,
                    "message_type": "text",
                    "llm_model": "gpt4",
                }
            ],
        },
    )
    cleanup_chats.append(("chat_2", timestamp + 1))

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
    chat_id = "test_delete_api_chat"
    timestamp = datetime.now().timestamp()
    user_email = "test_delete_api@example.com"

    # Create chat first
    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": chat_id,
            "timestamp": timestamp,
            "user_email": user_email,
            "messages": [
                {
                    "content": "To be deleted",
                    "role": MessageRole.USER,
                    "message_type": "text",
                    "llm_model": "gpt4",
                }
            ],
        },
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
    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": chat_id,
            "timestamp": timestamp,
            "user_email": user_email,
            "messages": [
                {
                    "content": "Dummy",
                    "role": MessageRole.USER,
                    "message_type": "text",
                    "llm_model": "gpt4",
                }
            ],
        },
    )
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
