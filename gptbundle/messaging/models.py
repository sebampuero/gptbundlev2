from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
)
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

from gptbundle.common.config import settings


class UserEmailIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "user_email-index"
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    user_email = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)


class MessageItem(MapAttribute):
    content = UnicodeAttribute()
    role = UnicodeAttribute()
    message_type = UnicodeAttribute()
    media = UnicodeAttribute(null=True)
    llm_model = UnicodeAttribute()


class Chat(Model):
    class Meta:
        table_name = "Chat"
        region = settings.AWS_REGION
        host = settings.AWS_ENDPOINT_URL_DYNAMODB
        read_capacity_units = 1
        write_capacity_units = 1

    chat_id = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)
    user_email = UnicodeAttribute()
    messages = ListAttribute(of=MessageItem)

    user_email_index = UserEmailIndex()
