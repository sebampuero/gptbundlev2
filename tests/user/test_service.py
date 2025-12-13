from sqlmodel import Session
from src.user.service import create_user, get_user_by_email, get_user_by_username, login
from src.user.models import UserCreate, UserLogin
import pytest

def test_create_user(session: Session, cleanup_users: list):
    email = "test_create@example.com"
    username = "test_create_user"
    password = "password123"
    
    user_create = UserCreate(email=email, username=username, password=password)
    
    user = create_user(user_create, session)
    cleanup_users.append(user.id)
    
    assert user.email == email
    assert user.username == username
    assert user.id is not None
    assert user.hashed_password != password
    
    # Verify in DB
    db_user = get_user_by_email(email, session)
    assert db_user is not None
    assert db_user.id == user.id
