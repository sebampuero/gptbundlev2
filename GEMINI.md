# GPTBundle V2 - Project Guide for Gemini

Welcome to **GPTBundle V2**, a full-stack chat application designed for multi-LLM interaction. This document provides a high-level technical overview, architectural patterns, and development guidelines to assist Gemini in understanding and contributing to this codebase.

## 🚀 Project Overview

GPTBundle V2 is a complete rewrite of the original GPTBundle, focused on scalability, real-time communication, and a modern tech stack. It integrates various AI services and storage solutions to provide a robust chat experience.

- **Primary Goal**: Interfacing with LLMs via OpenRouter/LiteLLM.
- **Key Capability**: Real-time streaming responses via WebSockets.
- **Secondary Features**: Image generation, PDF-based RAG (Retrieval-Augmented Generation), Chat history persistence, and Search.

## 🛠 Tech Stack

### Backend (Python 3.12+)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM/Database**: [SQLModel](https://sqlmodel.tiangolo.com/) + [PostgreSQL](https://www.postgresql.org/)
- **NoSQL (History)**: [PynamoDB](https://pynamodb.readthedocs.io/en/stable/) + [DynamoDB](https://aws.amazon.com/dynamodb/) (local/real)
- **Search**: [Elasticsearch](https://www.elastic.co/elasticsearch/)
- **LLM Abstraction**: [LiteLLM](https://github.com/BerriAI/litellm) / [LangChain](https://www.langchain.com/)
- **Caching/State**: [Redis](https://redis.io/)
- **Task Management**: FastAPI Background Tasks / Typer CLI
- **Tooling**: `uv` for dependency management, `ruff` for linting/formatting, `pytest` for testing.

### Frontend (React 19 + TypeScript)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Chakra UI](https://chakra-ui.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Communication**: WebSockets & REST API

## 📂 Project Structure

```text
.
├── gptbundle/              # Backend Root
│   ├── common/             # Config, DB connections, Logging
│   ├── llm/                # LLM Logic: chains, routers, services
│   ├── messaging/          # Chat history, WebSockets, Elasticsearch
│   ├── media_storage/      # S3/Local storage logic
│   ├── security/           # JWT, Passlib, Auth logic
│   ├── user/               # User management
│   ├── tests/              # Pytest suite
│   ├── main.py             # FastAPI Entrypoint
│   └── cli.py              # Typer Administrative CLI
├── react-ts-vite-app/      # Frontend Root
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── ...
├── docker-compose.yml      # Infrastructure (Postgres, DynamoDB, ES, etc.)
└── pyproject.toml          # Python Dependencies & Tool Config
```

## 🏗 Key Architectural Patterns

### 1. LLM Interaction & Streaming
The app uses `LiteLLM` for a unified interface to multiple models. Streaming is handled via **WebSockets** in `gptbundle/messaging/websocket_service.py` and `gptbundle/llm/service.py`. It supports both standard conversational chains and RAG-based chains.

### 2. Polyglot Persistence
- **PostgreSQL**: Stores relational data (Users, Chats metadata).
- **DynamoDB**: Stores the actual chat messages (using `PynamoDB` models). This allows for high-throughput message history.
- **Elasticsearch**: Indexes messages for full-text search.
- **S3 (or MinIO)**: Stores generated images and uploaded PDFs.

### 3. RAG Implementation
PDFs are processed and stored (likely using ChromaDB/Vector store - see `gptbundle/llm/rag_chain.py`). The `rag_chain` handles context retrieval and augmentation before sending prompts to the LLM.

## 🧪 Development Guidelines

### Coding Standards
- **Linting/Formatting**: Run `ruff check .` and `ruff format .`.
- **Typing**: Use Python type hints throughout the backend.
- **Environment**: Use `.env` files. Example in `.env.example`.

### Testing
- Tests are located in `gptbundle/tests`.
- Run tests with `pytest`.
- Use `gptbundle/tests/conftest.py` for shared fixtures (DB, client, mocks).
- Async tests are supported via `pytest-asyncio`.

### CLI Tools
Use `admin-cli` (defined in `gptbundle/cli.py`) for administrative tasks like database bootstrapping or user management.

## 💡 Tips for Gemini

- **Context is King**: When modifying LLM logic, check `gptbundle/llm/service.py` first.
- **WebSocket Debugging**: Most real-time logic resides in `gptbundle/messaging/router.py` (websocket endpoint) and `websocket_service.py`.
- **Database Changes**: We use `SQLModel` for Postgres and `PynamoDB` for DynamoDB. Ensure both are updated if message schemas change.
- **Vibe-Coding Disclaimer**: The project notes that parts were "vibe-coded". Be extra careful to verify logic and types in the frontend and some parts of the backend.

---
*Created on 2026-05-14 by Antigravity*
