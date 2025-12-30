import jwt

from gptbundle.common.config import settings
from gptbundle.security.service import (
    generate_access_token,
    generate_refresh_token,
    get_password_hash,
    pwd_context,
    verify_password,
)


def test_get_password_hash_structure():
    password = "supersecretpassword"
    hashed = get_password_hash(password)

    assert isinstance(hashed, str)
    assert hashed.startswith("$argon2")


def test_get_password_hash_verification():
    password = "supersecretpassword"
    hashed = get_password_hash(password)

    assert pwd_context.verify(password, hashed)
    assert not pwd_context.verify("wrongpassword", hashed)


def test_verify_password():
    password = "supersecretpassword"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_password_hash_uniqueness():
    password = "samepassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Argon2 should use random salts by default
    assert hash1 != hash2


def test_generate_access_token():
    subject = "test@example.com"
    token = generate_access_token(subject)

    assert isinstance(token, str)

    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == subject
    assert "exp" in payload


def test_generate_refresh_token():
    subject = "test@example.com"
    token = generate_refresh_token(subject)

    assert isinstance(token, str)

    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == subject
    assert "exp" in payload
