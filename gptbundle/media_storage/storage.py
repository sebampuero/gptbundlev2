import logging

import boto3
from botocore.exceptions import ClientError

from gptbundle.common.config import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        region_name=settings.S3_REGION,
    )


def upload_file(file_data: bytes, key: str):
    client = get_s3_client()
    try:
        client.put_object(Bucket=settings.S3_BUCKET_NAME, Key=key, Body=file_data)
        logger.info(f"Successfully uploaded file to {key}")
    except ClientError as e:
        logger.error(f"Failed to upload file to {key}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unknown error while uploading file to {key}: {e}")
        raise e


def generate_presigned_url(key: str, expiration=3600):
    client = get_s3_client()
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
            ExpiresIn=expiration,
        )
        logger.info(f"Successfully generated presigned URL for {key}")
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for {key}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unknown error while generating presigned URL for {key}: {e}")
        raise e


def move_file(source_key: str, target_key: str):
    client = get_s3_client()
    try:
        copy_source = {"Bucket": settings.S3_BUCKET_NAME, "Key": source_key}
        client.copy_object(
            CopySource=copy_source, Bucket=settings.S3_BUCKET_NAME, Key=target_key
        )
        client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=source_key)
        logger.info(f"Successfully moved file from {source_key} to {target_key}")
    except ClientError as e:
        logger.error(f"Failed to move file from {source_key} to {target_key}: {e}")
        raise e
    except Exception as e:
        logger.error(
            f"Unknown error while moving file from {source_key} to {target_key}: {e}"
        )
        raise e


def delete_objects(keys: list[str]):
    if not keys:
        return
    client = get_s3_client()
    try:
        delete_list = [{"Key": key} for key in keys]
        client.delete_objects(
            Bucket=settings.S3_BUCKET_NAME, Delete={"Objects": delete_list}
        )
        logger.info(f"Successfully deleted {len(keys)} objects from S3")
    except ClientError as e:
        logger.error(f"Failed to delete objects from S3: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unknown error while deleting objects from S3: {e}")
        raise e
