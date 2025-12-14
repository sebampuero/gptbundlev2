from sqlmodel import Field, SQLModel
import uuid
from pydantic import EmailStr


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True)
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserLogin(SQLModel):
    username: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

class UserResponse(UserBase):
    id: uuid.UUID