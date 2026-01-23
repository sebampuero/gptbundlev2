from elasticsearch import ConflictError, Elasticsearch

from gptbundle.common.config import settings
from gptbundle.messaging.exceptions import ChatAlreadyExistsError
from gptbundle.messaging.schemas import Chat


class ElasticsearchRepository:
    _index_initialized = False

    def __init__(self):
        self.client = self._create_client()
        if not ElasticsearchRepository._index_initialized:
            self.create_index_if_not_exists()
            ElasticsearchRepository._index_initialized = True

    def _create_client(self) -> Elasticsearch:
        return Elasticsearch(
            hosts=settings.ELASTICSEARCH_HOST,
            basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        )

    def create_index_if_not_exists(self) -> None:
        if not self.client.indices.exists(index="chats"):
            body = {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": {"properties": {"user_email": {"type": "keyword"}}},
            }
            self.client.indices.create(index="chats", body=body)

    def store_chat(self, chat: Chat) -> None:
        try:
            self.client.index(
                index="chats", document=chat.dict(), id=chat.chat_id, op_type="create"
            )
        except ConflictError as e:
            raise ChatAlreadyExistsError(
                f"Chat with id {chat.chat_id} already exists"
            ) from e

    def delete_chat(self, chat_id: str) -> None:
        self.client.delete(index="chats", id=chat_id)

    def search_chats(self, user_email: str, query: str) -> list[Chat]:
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"messages.content": query}},
                    ],
                    "filter": [
                        {"term": {"user_email": user_email}},
                    ],
                }
            }
        }
        response = self.client.search(index="chats", body=search_query)
        found_matches = [Chat(**hit["_source"]) for hit in response["hits"]["hits"]]
        return sorted(found_matches, key=lambda x: x.timestamp, reverse=True)
