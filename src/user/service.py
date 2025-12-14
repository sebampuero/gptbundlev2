from .models import UserCreate, UserLogin, User
from src.security.service import get_password_hash, verify_password
from sqlmodel import Session, select, update


def create_user(user_create: UserCreate, session: Session) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_email(email: str, session: Session) -> User | None:
    return session.exec(select(User).where(User.email == email)).one_or_none()


def get_user_by_username(username: str, session: Session) -> User | None:
    return session.exec(select(User).where(User.username == username)).one_or_none()


def login(user: UserLogin, session: Session) -> User | None:
    db_user = get_user_by_username(user.username, session)
    if not db_user:
        return None
    if not verify_password(user.password, db_user.hashed_password):
        return None
    return db_user
