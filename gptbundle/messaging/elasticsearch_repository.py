import logging

from elasticsearch import AsyncElasticsearch, ConflictError

from gptbundle.common.config import settings
from gptbundle.messaging.exceptions import ChatAlreadyExistsError
from gptbundle.messaging.schemas import Chat

logger = logging.getLogger(__name__)


class ElasticsearchRepository:
    _index_initialized = False
    _client: AsyncElasticsearch | None = None

    def __init__(self):
        if ElasticsearchRepository._client is None:
            ElasticsearchRepository._client = self._create_client()
        self.client = ElasticsearchRepository._client

    def _create_client(self) -> AsyncElasticsearch:
        return AsyncElasticsearch(
            hosts=settings.ELASTICSEARCH_HOST,
            basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        )

    async def create_index_if_not_exists(self) -> None:
        if not await self.client.indices.exists(index="chats"):
            body = {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": {"properties": {"user_email": {"type": "keyword"}}},
            }
            await self.client.indices.create(index="chats", body=body)

    async def store_chat(self, chat: Chat) -> None:
        if not ElasticsearchRepository._index_initialized:
            await self.create_index_if_not_exists()
            ElasticsearchRepository._index_initialized = True
        try:
            await self.client.index(
                index="chats",
                document=chat.dict(),
                id=chat.chat_id,
                op_type="create",
                refresh=True,
            )
            logger.debug(f"Chat with id {chat.chat_id} stored successfully in ES")
        except ConflictError as e:
            raise ChatAlreadyExistsError(
                f"Chat with id {chat.chat_id} already exists"
            ) from e

    async def update_chat(self, chat: Chat) -> None:
        if not ElasticsearchRepository._index_initialized:
            await self.create_index_if_not_exists()
            ElasticsearchRepository._index_initialized = True
        await self.client.index(
            index="chats", document=chat.dict(), id=chat.chat_id, refresh=True
        )

    async def delete_chat(self, chat_id: str) -> None:
        if not ElasticsearchRepository._index_initialized:
            await self.create_index_if_not_exists()
            ElasticsearchRepository._index_initialized = True
        await self.client.delete(index="chats", id=chat_id, refresh=True)

    async def search_chats(self, user_email: str, query: str) -> list[Chat]:
        if not ElasticsearchRepository._index_initialized:
            await self.create_index_if_not_exists()
            ElasticsearchRepository._index_initialized = True
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
        response = await self.client.search(index="chats", body=search_query)
        found_matches = [Chat(**hit["_source"]) for hit in response["hits"]["hits"]]
        return sorted(found_matches, key=lambda x: x.timestamp, reverse=True)
