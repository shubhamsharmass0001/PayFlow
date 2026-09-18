from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)
from app.modules.auth.models import RefreshToken, User
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.shared.exceptions import (
    ConflictException,
    UnauthorizedException,
)


def register_user(db: Session, request: RegisterRequest) -> AuthResponse:
    """Registers a new user account, generates initial access and refresh tokens."""
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise ConflictException(
            message=f"An account with email '{request.email}' already exists",
            code="AUTH_EMAIL_EXISTS",
            details={"email": request.email},
        )

    if request.phone:
        existing_phone = db.query(User).filter(User.phone == request.phone).first()
        if existing_phone:
            raise ConflictException(
                message=f"An account with phone number '{request.phone}' already exists",
                code="AUTH_PHONE_EXISTS",
                details={"phone": request.phone},
            )

    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        phone=request.phone,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.flush()

    tokens = _create_token_pair(db, user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )


def authenticate_user(db: Session, request: LoginRequest) -> TokenResponse:
    """Authenticates a user via email or phone number and password."""
    user = (
        db.query(User)
        .filter(
            (User.email == request.username) | (User.phone == request.username),
            User.deleted_at.is_(None),
        )
        .first()
    )

    if not user or not verify_password(request.password, user.hashed_password):
        raise UnauthorizedException(
            message="Invalid username or password",
            code="AUTH_INVALID_CREDENTIALS",
        )

    if not user.is_active:
        raise UnauthorizedException(
            message="User account is deactivated",
            code="AUTH_USER_INACTIVE",
        )

    tokens = _create_token_pair(db, user)
    db.commit()
    return tokens


def rotate_refresh_token(db: Session, raw_token: str) -> TokenResponse:
    """Validates the existing refresh token, rotates it (revoking the old one),

    and issues a brand-new token pair.
    """
    token_hash = hash_refresh_token(raw_token)
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )

    if not stored_token:
        raise UnauthorizedException(
            message="Invalid refresh token",
            code="AUTH_INVALID_REFRESH_TOKEN",
        )

    if stored_token.is_revoked:
        # Possible replay attack detected: revoke all tokens for this user
        db.query(RefreshToken).filter(
            RefreshToken.user_id == stored_token.user_id
        ).update({"is_revoked": True})
        db.commit()
        raise UnauthorizedException(
            message="Revoked refresh token presented. Session terminated for security.",
            code="AUTH_REFRESH_TOKEN_REVOKED",
        )

    now = datetime.now(timezone.utc)
    if stored_token.expires_at < now:
        stored_token.is_revoked = True
        db.commit()
        raise UnauthorizedException(
            message="Refresh token has expired. Please sign in again.",
            code="AUTH_REFRESH_TOKEN_EXPIRED",
        )

    # Invalidate current token (Strict rotation)
    stored_token.is_revoked = True

    user = db.query(User).filter(User.id == stored_token.user_id, User.deleted_at.is_(None)).first()
    if not user or not user.is_active:
        db.commit()
        raise UnauthorizedException(
            message="User account is inactive or not found",
            code="AUTH_USER_INACTIVE",
        )

    # Issue new pair
    tokens = _create_token_pair(db, user)
    db.commit()
    return tokens


def revoke_token(
    db: Session,
    raw_token: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """Revokes a specific refresh token and/or all refresh tokens for a user."""
    if raw_token:
        token_hash = hash_refresh_token(raw_token)
        db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).update({"is_revoked": True})

    if user_id:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({"is_revoked": True})

    db.commit()


def _create_token_pair(db: Session, user: User) -> TokenResponse:
    """Internal helper: generates access token (15m) + refresh token (7d) and records hash in DB."""
    access_token = create_access_token(
        subject=user.id,
        claims={"email": user.email, "is_superuser": user.is_superuser},
    )

    raw_refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh_token)

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_revoked=False,
    )
    db.add(refresh_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=900,  # 15 minutes in seconds
    )
