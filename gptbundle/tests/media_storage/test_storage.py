import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from gptbundle.common.config import settings
from gptbundle.media_storage.storage import (
    generate_presigned_url,
    move_file,
    upload_file,
)


@pytest.fixture
def s3_setup(monkeypatch):
    monkeypatch.setattr(
        "gptbundle.media_storage.storage.settings.S3_ENDPOINT_URL", None
    )
    with mock_aws():
        s3 = boto3.client("s3", region_name=settings.S3_REGION)
        bucket_config = {}
        if settings.S3_REGION != "us-east-1":
            bucket_config["CreateBucketConfiguration"] = {
                "LocationConstraint": settings.S3_REGION
            }

        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME, **bucket_config)
        yield s3


def test_upload_file(s3_setup):
    test_data = b"hello world"
    test_key = "test_folder/test.txt"

    upload_file(test_data, test_key)

    response = s3_setup.get_object(Bucket=settings.S3_BUCKET_NAME, Key=test_key)
    assert response["Body"].read() == test_data


def test_generate_presigned_url(s3_setup):
    test_key = "test.txt"
    s3_setup.put_object(Bucket=settings.S3_BUCKET_NAME, Key=test_key, Body=b"test")

    url = generate_presigned_url(test_key)
    assert url is not None
    assert settings.S3_BUCKET_NAME in url
    assert test_key in url


def test_move_file(s3_setup):
    source_key = "temp/test.txt"
    target_key = "permanent/test.txt"
    test_data = b"move me"

    s3_setup.put_object(Bucket=settings.S3_BUCKET_NAME, Key=source_key, Body=test_data)

    move_file(source_key, target_key)

    # Check target exists with correct data
    response = s3_setup.get_object(Bucket=settings.S3_BUCKET_NAME, Key=target_key)
    assert response["Body"].read() == test_data

    # Check source is deleted
    with pytest.raises(ClientError):
        s3_setup.get_object(Bucket=settings.S3_BUCKET_NAME, Key=source_key)


def test_upload_file_error(s3_setup):
    # Try to upload to a non-existent bucket by patching settings
    from unittest.mock import patch

    with patch(
        "gptbundle.media_storage.storage.settings.S3_BUCKET_NAME", "non-existent-bucket"
    ):
        with pytest.raises(ClientError):
            upload_file(b"data", "key")
