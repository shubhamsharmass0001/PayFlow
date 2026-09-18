import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    full_name: str = Field(min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    username: str = Field(description="Email address or phone number")
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
