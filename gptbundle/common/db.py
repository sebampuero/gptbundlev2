from collections.abc import Generator

from sqlmodel import Session, create_engine

from .config import settings

engine = create_engine(str(settings.sqlalchemy_database_uri))


def get_pg_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
