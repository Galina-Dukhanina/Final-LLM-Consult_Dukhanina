from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_auth_uc, get_current_user
from app.db.models import User
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
async def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
    )
