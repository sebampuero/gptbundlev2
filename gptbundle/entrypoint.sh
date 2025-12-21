#! /usr/bin/env bash

export PYTHONPATH=$(pwd)

export OPENROUTER_API_KEY="$(cat /run/secrets/openrouter_api_key)"

uv run alembic upgrade head
python3 gptbundle/initial_table_bootstrap.py
uv run fastapi run gptbundle/main.py --port 8000 --host 0.0.0.0