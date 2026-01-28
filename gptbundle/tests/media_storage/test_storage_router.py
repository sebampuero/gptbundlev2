import io

import boto3
import pytest
from moto import mock_aws

from gptbundle.common.config import settings
from gptbundle.security.service import generate_access_token


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


@pytest.mark.asyncio
async def test_upload_media_success(client, s3_setup):
    user_email = "test@example.com"
    token = generate_access_token(user_email)

    # Prepare files
    file1 = ("test1.jpg", io.BytesIO(b"dummy image 1"), "image/jpeg")
    file2 = ("test2.png", io.BytesIO(b"dummy image 2"), "image/png")

    response = await client.post(
        f"{settings.API_V1_STR}/storage/upload_media",
        files=[("files", file1), ("files", file2)],
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) == 2

    for key in data["keys"]:
        assert key.startswith("temp/")
        # Verify file exists in S3
        response_s3 = s3_setup.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        assert response_s3["Body"].read() in [b"dummy image 1", b"dummy image 2"]


@pytest.mark.asyncio
async def test_upload_media_unauthenticated(client):
    file1 = ("test1.jpg", io.BytesIO(b"dummy image 1"), "image/jpeg")

    response = await client.post(
        f"{settings.API_V1_STR}/storage/upload_media", files=[("files", file1)]
    )

    assert response.status_code == 401
