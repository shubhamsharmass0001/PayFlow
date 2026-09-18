import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class StoreCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    code: str = Field(
        min_length=2,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique alphanumeric store identifier within the merchant organization",
    )
    address_line1: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    upi_vpa: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional custom UPI VPA overriding the merchant's default VPA",
    )


class StoreUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    address_line1: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    upi_vpa: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    name: str
    code: str
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    upi_vpa: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
