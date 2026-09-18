from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.rate_limit import check_login_rate_limit
from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.auth.service import (
    authenticate_user,
    register_user,
    revoke_token,
    rotate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    return register_user(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain access & refresh tokens",
)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    # Enforce Redis rate limiting per IP + username/phone
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_login_rate_limit(client_ip=client_ip, identifier=payload.username)

    return authenticate_user(db, payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and acquire a fresh access token",
)
def refresh(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return rotate_refresh_token(db, payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke active refresh tokens",
)
def logout(
    payload: LogoutRequest = LogoutRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    revoke_token(
        db=db,
        raw_token=payload.refresh_token,
        user_id=str(current_user.id) if not payload.refresh_token else None,
    )
    return {"message": "Successfully logged out"}
