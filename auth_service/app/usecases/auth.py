from jose import ExpiredSignatureError, JWTError

from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic


class AuthUsecase:
    def __init__(self, users_repo: UsersRepository):
        self._users_repo = users_repo

    async def register(self, data: RegisterRequest) -> UserPublic:
        existing = await self._users_repo.get_by_email(str(data.email))
        if existing is not None:
            raise UserAlreadyExistsError()

        user = await self._users_repo.create(
            email=str(data.email),
            password_hash=hash_password(data.password),
            role="user",
        )
        return UserPublic(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )

    async def login(self, *, email: str, password: str) -> TokenResponse:
        user = await self._users_repo.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(sub=str(user.id), role=user.role)
        return TokenResponse(access_token=token, token_type="bearer")

    async def me(self, *, token: str) -> UserPublic:
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
            user_id = int(sub)
        except ValueError:
            raise InvalidTokenError()

        user = await self._users_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        return UserPublic(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )
