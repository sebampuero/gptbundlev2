#! /usr/bin/env bash

export PYTHONPATH=$(pwd)

export OPENROUTER_API_KEY="$(cat /run/secrets/openrouter_api_key)"
export JWT_SECRET_KEY="$(cat /run/secrets/jwt_secret_key)"
export S3_ACCESS_KEY_ID="$(cat /run/secrets/s3_access_key_id)"
export S3_SECRET_ACCESS_KEY="$(cat /run/secrets/s3_secret_access_key)"

uv run alembic upgrade head
python3 gptbundle/initial_table_bootstrap.py
uv run fastapi run gptbundle/main.py --port 8000 --host 0.0.0.0