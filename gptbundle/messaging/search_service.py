from .elasticsearch_repository import ElasticsearchRepository
from .schemas import Chat


def search_chats_by_keyword(
    es_repo: ElasticsearchRepository, user_email: str, search_term: str
) -> list[Chat]:
    return es_repo.search_chats(user_email, search_term)
