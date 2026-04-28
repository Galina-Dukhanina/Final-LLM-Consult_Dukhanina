from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except ExpiredSignatureError as e:
        raise ValueError("token expired") from e
    except JWTError as e:
        raise ValueError("invalid token") from e

    if not payload.get("sub"):
        raise ValueError("missing sub")

    return payload
