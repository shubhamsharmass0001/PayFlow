import uuid
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re

PHONE_REGEX = re.compile(r"^\+?[0-9]{10,15}$")


class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full customer name")
    phone: str = Field(..., min_length=10, max_length=20, description="Customer phone number")
    email: Optional[EmailStr] = Field(None, description="Optional customer email address")
    upi_vpa: Optional[str] = Field(None, max_length=100, description="Customer default UPI VPA handle")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = v.strip().replace(" ", "").replace("-", "")
        if not PHONE_REGEX.match(clean):
            raise ValueError("Phone number must contain 10-15 digits with optional leading +")
        return clean


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated name")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Updated phone")
    email: Optional[EmailStr] = Field(None, description="Updated email")
    upi_vpa: Optional[str] = Field(None, max_length=100, description="Updated UPI VPA")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().replace(" ", "").replace("-", "")
        if not PHONE_REGEX.match(clean):
            raise ValueError("Phone number must contain 10-15 digits with optional leading +")
        return clean


class CustomerResponse(BaseModel):
    id: uuid.UUID
    merchant_id: uuid.UUID
    name: str
    phone: str
    email: Optional[str] = None
    upi_vpa: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    warning: Optional[str] = Field(None, description="Deduplication or profile warning notice")

    model_config = ConfigDict(from_attributes=True)


class CustomerQueryFilter(BaseModel):
    search: Optional[str] = Field(None, description="Case-insensitive search against name, phone, or email")
    sort_by: Literal["name", "phone", "email", "created_at"] = Field(
        default="created_at", description="Field to sort by"
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="desc", description="Sort direction"
    )
