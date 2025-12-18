import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from src.common.config import settings

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
            "messages": [{"text": "Hello API", "type": "human", "llm_model": "gpt4"}]
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert is_valid_uuid4(content["chat_id"])
    assert isinstance(content["timestamp"], float)
    assert content["timestamp"] < datetime.now().timestamp()
    assert content["user_email"] == user_email
    assert len(content["messages"]) == 1
    assert content["messages"][0]["text"] == "Hello API"
    
    cleanup_chats.append((content["chat_id"], content["timestamp"]))

def test_retrieve_chat_success(client: TestClient, cleanup_chats: list):
    chat_id = "test_get_api_chat"
    timestamp = datetime.now().timestamp()
    user_email = "test_get_api@example.com"
    
    # Create chat first
    create_response = client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": chat_id,
            "timestamp": timestamp,
            "user_email": user_email,
            "messages": [{"text": "Found me", "type": "human", "llm_model": "gpt4"}]
        },
    )
    cleanup_chats.append((chat_id, timestamp))
    
    # Retrieve it
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}"
    )
    assert response.status_code == 200
    content = response.json()
    assert content["chat_id"] == chat_id
    assert content["user_email"] == user_email

def test_retrieve_chat_not_found(client: TestClient):
    chat_id = "non_existent_chat"
    timestamp = datetime.now().timestamp()
    
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}"
    )
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
            "messages": [{"text": "Msg 1", "type": "human", "llm_model": "gpt4"}]
        },
    )
    cleanup_chats.append(("chat_1", timestamp))
    
    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": "chat_2",
            "timestamp": timestamp + 1,
            "user_email": user_email,
            "messages": [{"text": "Msg 2", "type": "human", "llm_model": "gpt4"}]
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
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chats/nobody@example.com"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chats not found"

def test_append_messages_success(client: TestClient, cleanup_chats: list):
    chat_id = "test_append_api_chat"
    timestamp = datetime.now().timestamp()
    user_email = "test_append_api@example.com"
    
    # Create chat first with one message
    client.post(
        f"{settings.API_V1_STR}/messaging/chat",
        json={
            "chat_id": chat_id,
            "timestamp": timestamp,
            "user_email": user_email,
            "messages": [{"text": "First message", "type": "human", "llm_model": "gpt4"}]
        },
    )
    cleanup_chats.append((chat_id, timestamp))
    
    # Append a new message
    append_response = client.put(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}",
        json=[{"text": "Second message", "type": "ai", "llm_model": "gpt4"}]
    )
    
    assert append_response.status_code == 200
    
    # Retrieve it
    response = client.get(
        f"{settings.API_V1_STR}/messaging/chat/{chat_id}/{timestamp}"
    )
    assert response.status_code == 200
    content = response.json()
    assert content["chat_id"] == chat_id
    assert len(content["messages"]) == 2
    assert content["messages"][0]["text"] == "First message"
    assert content["messages"][1]["text"] == "Second message"
    assert content["messages"][1]["type"] == "ai"

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
            "messages": [{"text": "To be deleted", "type": "human", "llm_model": "gpt4"}]
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
