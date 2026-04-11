from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    SUBDIRECTORY: str = ""
    PROJECT_NAME: str = "gptbundle"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    REDIS_URL: str = "redis://redis:6379/0"

    AWS_REGION: str = "eu-central-1"
    AWS_ENDPOINT_URL_DYNAMODB: str

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str = "gptbundle"
    S3_REGION: str = "eu-central-1"
    S3_DOC_PREFIX: str = "pdfdocuments"

    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    VECTOR_STORE_COLLECTION_NAME: str = "gptbundle"
    MISTRAL_EMBED_MODEL: str = "mistral-embed"
    MISTRAL_API_KEY: str
    SPLITTER_CHUNK_SIZE: int = 2000
    SPLITTER_CHUNK_OVERLAP: int = 200

    ELASTICSEARCH_HOST: str = "http://localhost:9200"
    ELASTICSEARCH_USER: str = "elastic"
    ELASTICSEARCH_PASSWORD: str = "changemepls"

    OPENROUTER_API_KEY: str
    OPENROUTER_MODELS_URL: str = "https://openrouter.ai/api/v1/models"

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DEVELOPMENT_MODE: bool = False

    ROOT_LOG_LEVEL: str = "INFO"
    APP_LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    ALLOW_REGISTRATION: bool = True

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
