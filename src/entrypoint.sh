#! /usr/bin/env bash

export PYTHONPATH=$(pwd)

export OPENAI_API_KEY="$(cat /run/secrets/openai_api_key)"
export DEEPSEEK_API_KEY="$(cat /run/secrets/deepseek_api_key)"
export OPENROUTER_API_KEY="$(cat /run/secrets/openrouter_api_key)"

uv run alembic upgrade head
python3 src/initial_table_bootstrap.py
uv run fastapi run src/main.py --port 8000 --host 0.0.0.0