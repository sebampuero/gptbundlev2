from src.auth.service import get_password_hash, pwd_context

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

def test_password_hash_uniqueness():
    password = "samepassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Argon2 should use random salts by default
    assert hash1 != hash2
