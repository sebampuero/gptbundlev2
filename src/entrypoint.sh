#! /usr/bin/env bash

export PYTHONPATH=$(pwd)

uv run alembic upgrade head
python3 src/initial_table_bootstrap.py
uv run fastapi run src/main.py --port 8000 --host 0.0.0.0