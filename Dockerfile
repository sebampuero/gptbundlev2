FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

ENV UV_CACHE_DIR=/app/.cache/uv

COPY pyproject.toml uv.lock ./

RUN chown -R 1000:1000 /app

USER 1000

RUN uv sync --frozen --no-dev --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

ENTRYPOINT ["sh", "gptbundle/entrypoint.sh"]
