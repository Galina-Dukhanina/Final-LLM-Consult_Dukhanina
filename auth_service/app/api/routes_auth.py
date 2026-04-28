from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_uc, oauth2_scheme
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUsecase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(
    data: RegisterRequest, uc: AuthUsecase = Depends(get_auth_uc)
) -> UserPublic:
    return await uc.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    uc: AuthUsecase = Depends(get_auth_uc),
) -> TokenResponse:
    return await uc.login(email=form.username, password=form.password)


@router.get("/me", response_model=UserPublic)
async def me(
    token: str = Depends(oauth2_scheme),
    uc: AuthUsecase = Depends(get_auth_uc),
) -> UserPublic:
    return await uc.me(token=token)
