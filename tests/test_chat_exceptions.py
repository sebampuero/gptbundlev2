import unittest
from unittest.mock import MagicMock, patch

import pytest
from elasticsearch import ConflictError
from pynamodb.exceptions import PutError

from gptbundle.messaging.elasticsearch_repository import ElasticsearchRepository
from gptbundle.messaging.exceptions import ChatAlreadyExistsError
from gptbundle.messaging.repository import ChatRepository
from gptbundle.messaging.schemas import Chat, ChatCreate


class TestChatExceptions(unittest.TestCase):
    @patch("gptbundle.messaging.repository.ChatModel")
    def test_repository_create_chat_raises_if_exists(self, mock_chat_model):
        repo = ChatRepository()
        chat_in = ChatCreate(
            chat_id="test_id",
            timestamp=123456789.0,
            user_email="test@example.com",
            messages=[],
        )

        # Mock save to raise PutError when condition fails
        mock_instance = mock_chat_model.return_value
        mock_instance.save.side_effect = PutError("Condition failed")

        with pytest.raises(ChatAlreadyExistsError):
            repo.create_chat(chat_in)

    @patch("gptbundle.messaging.elasticsearch_repository.Elasticsearch")
    def test_elasticsearch_store_chat_raises_if_exists(self, mock_es):
        # Mock ES client
        mock_client = MagicMock()
        mock_es.return_value = mock_client

        # Mock index creation check
        mock_client.indices.exists.return_value = True

        repo = ElasticsearchRepository()
        chat = Chat(
            chat_id="test_id",
            timestamp=123456789.0,
            user_email="test@example.com",
            messages=[],
        )

        # Mock index to raise ConflictError
        mock_client.index.side_effect = ConflictError("409", "conflict", {})

        with pytest.raises(ChatAlreadyExistsError):
            repo.store_chat(chat)


if __name__ == "__main__":
    unittest.main()
