import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def test_decode_and_validate_valid_token() -> None:
    token = jwt.encode(
        {"sub": "123", "role": "user", "exp": 4102444800},  # 2100-01-01
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    payload = decode_and_validate(token)
    assert payload["sub"] == "123"


def test_decode_and_validate_invalid_token_raises() -> None:
    with pytest.raises(ValueError):
        decode_and_validate("not-a-jwt")
