# gptbundlev2

A project created with FastAPI CLI.

## Quick Start

### Start the development server:

```bash
docker run -p 8000:8000 gptbundlev2
```

## Docker Compose

To run the application with the database:

```bash
docker-compose up --build
```


Visit http://localhost:8000

### Deploy to FastAPI Cloud:

> Reader's note: These commands are not quite ready for prime time yet, but will be soon! Join the waiting list at https://fastapicloud.com!

```bash
uv run fastapi login
uv run fastapi deploy
```

## Project Structure

- `main.py` - Your FastAPI application
- `pyproject.toml` - Project dependencies

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [FastAPI Cloud](https://fastapicloud.com)
