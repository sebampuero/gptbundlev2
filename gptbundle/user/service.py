from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from gptbundle.security.service import get_password_hash, verify_password

from .exceptions import UserAlreadyExistsError
from .models import User, UserCreate, UserLogin


async def create_user(user_create: UserCreate, session: AsyncSession) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise UserAlreadyExistsError() from e
    await session.refresh(db_obj)
    return db_obj


async def get_user_by_email(
    email: str, session: AsyncSession, include_inactive: bool = False
) -> User | None:
    statement = select(User).where(User.email == email)
    if not include_inactive:
        statement = statement.where(User.is_active)
    return (await session.exec(statement)).one_or_none()


async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    return (
        await session.exec(
            select(User).where(User.username == username, User.is_active)
        )
    ).one_or_none()


async def login(user: UserLogin, session: AsyncSession) -> User | None:
    db_user = await get_user_by_username(user.username, session)
    if not db_user:
        return None
    if not verify_password(user.password, db_user.hashed_password):
        return None
    return db_user


async def delete_user_by_email(email: str, session: AsyncSession) -> bool:
    user = await get_user_by_email(email, session)
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True


async def deactivate_user(email: str, session: AsyncSession) -> bool:
    user = await get_user_by_email(email, session)
    if not user:
        return False
    user.is_active = False
    session.add(user)
    await session.commit()
    return True


async def activate_user(email: str, session: AsyncSession) -> bool:
    user = await get_user_by_email(email, session, include_inactive=True)
    if not user:
        return False
    user.is_active = True
    session.add(user)
    await session.commit()
    return True


async def get_users(session: AsyncSession) -> list[User]:
    return (await session.exec(select(User))).all()


async def delete_all_users(session: AsyncSession) -> int:
    from sqlmodel import delete

    statement = delete(User)
    result = await session.exec(statement)
    await session.commit()
    return result.rowcount
