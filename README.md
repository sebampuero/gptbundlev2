# GPTBundle V2

This is "almost" a complete rewrite of the first version of the [GPTBundle](https://github.com/sebampuero/simple_chatgpt_4). This version is a full-stack chat application designed to interface with various Large Language Models (LLMs). This project provides a React-based frontend (vibe-coded to 80%) and a FastAPI backend (vibe-coded to 40-50%).

This was a fun project to see how vibe-coding works and how important it is **not** to 100% rely on AI completely. Several changes needed to be checked and tested before letting the AI generate the final code.

## Features

- **Multi-Model Support**: Interact with various LLMs via OpenRouter (powered by LiteLLM).
- **Real-time Chat**: Streaming LLM responses leveraging WebSockets.
- **Image Generation**: Generate images with integrated S3 storage for persistent media handling.
- **Chat History**: History management utilizing (local) DynamoDB for scalable storage. Configurable with real AWS DynamoDB.
- **Search**: Full-text search capabilities powered by Elasticsearch.
- **Modern UI**: Improved user interface built with React, TypeScript, and Chakra UI.

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12+
- **Database**: PostgreSQL (Relational), DynamoDB (NoSQL), Elasticsearch (Search)
- **LLM Utility**: LiteLLM
- **Authentication**: JWT, Passlib
- **Infrastructure**: Boto3 (AWS SDK)

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: Chakra UI, Lucide React
- **Language**: TypeScript

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js (for local frontend development)
- Python 3.12+ (for local backend development)

### Environment Setup

Copies of environment files should be created from examples `.env.example`.

The environment variables need to be loaded up in the OS. For that, the following command can be run:

```bash
set -a && source .env && set +a
```

### Running with Docker

The recommended way to run the application stack is via Docker Compose:

```bash
docker-compose up -d --build
```

This starts the following services:
- **web**: FastAPI backend (exposed on port 8000)
- **db**: PostgreSQL database (exposed on port 5432)
- **dynamodb-local**: Local DynamoDB instance (exposed on port 9000)
- **elasticsearch**: Elasticsearch instance (exposed on port 9200)

### Local Development

#### Backend

The backend package is located in `gptbundle/`.

1. Install dependencies (using your preferred package manager, e.g., `uv` or `pip`):
   ```bash
   pip install -e .[dev]
   ```
2. Run database migrations using Alembic.
3. Start the server:
   ```bash
   fastapi dev
   ```

#### Frontend

The frontend application is located in `react-ts-vite-app/`.

1. Navigate to the directory:
   ```bash
   cd react-ts-vite-app
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## CLI Tools

The project includes an administrative CLI (`admin-cli`).
Usage:
```bash
admin-cli --help
```
