from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    password = "Testpass123!"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_jwt_create_and_decode_contains_claims() -> None:
    token = create_access_token(sub="123", role="user", expires_minutes=5)
    payload = decode_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"

    assert "iat" in payload
    assert "exp" in payload
    assert isinstance(payload["iat"], int)
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > payload["iat"]
