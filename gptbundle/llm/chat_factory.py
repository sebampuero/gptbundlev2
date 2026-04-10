from typing import Any

from gptbundle.media_storage.storage import generate_presigned_url
from gptbundle.messaging.schemas import MessageCreate


def convert_input_to_lc_format(message: MessageCreate) -> dict[str, Any]:
    if not message.img_s3_keys:
        return {"question": message.content}

    question_content = [{"type": "text", "text": message.content}]
    for key in message.img_s3_keys:
        presigned_url = generate_presigned_url(key)
        question_content.append(
            {"type": "image_url", "image_url": {"url": presigned_url}}
        )

    return {"question": question_content}
