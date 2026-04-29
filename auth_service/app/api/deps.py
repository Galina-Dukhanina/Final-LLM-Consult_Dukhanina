from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError, UserNotFoundError
from app.core.security import decode_token
from app.db.models import User
from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUsecase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repo(db: AsyncSession = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db)


def get_auth_uc(users_repo: UsersRepository = Depends(get_users_repo)) -> AuthUsecase:
    return AuthUsecase(users_repo)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()

    sub = payload.get("sub")
    if not sub:
        raise InvalidTokenError()

    try:
        return int(sub)
    except ValueError:
        raise InvalidTokenError()


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    users_repo: UsersRepository = Depends(get_users_repo),
) -> User:
    user = await users_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    return user
