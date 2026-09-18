import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.shared.exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for a plaintext password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | uuid.UUID,
    expires_delta: Optional[timedelta] = None,
    claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generates a short-lived (default 15 minutes) signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "exp": expire,
        "iat": now,
        "nbf": now,
    }
    if claims:
        to_encode.update(claims)

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and verifies a JWT token. Returns payload dict or None if invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def generate_refresh_token() -> str:
    """Generates a cryptographically random URL-safe refresh token string."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Produces a deterministic SHA-256 hash for secure storage and indexed lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    """FastAPI dependency that extracts and validates the bearer token, returning the authenticated User."""
    from app.modules.auth.models import User

    if not credentials or not credentials.credentials:
        raise UnauthorizedException(
            message="Missing or invalid authentication token",
            code="AUTH_MISSING_TOKEN",
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException(
            message="Invalid or expired authentication token",
            code="AUTH_INVALID_TOKEN",
        )

    if payload.get("type") != "access":
        raise UnauthorizedException(
            message="Token type is not valid for access",
            code="AUTH_INVALID_TOKEN_TYPE",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(
            message="Token payload is missing subject",
            code="AUTH_INVALID_TOKEN",
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException(
            message="Malformed user identifier in token",
            code="AUTH_INVALID_TOKEN",
        )

    user = db.query(User).filter(User.id == user_uuid, User.deleted_at.is_(None)).first()
    if not user:
        raise UnauthorizedException(
            message="User account associated with this token was not found",
            code="AUTH_USER_NOT_FOUND",
        )

    if not user.is_active:
        raise UnauthorizedException(
            message="User account is deactivated",
            code="AUTH_USER_INACTIVE",
        )

    return user
