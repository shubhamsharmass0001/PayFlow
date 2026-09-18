import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.merchants.models import (
    KycDocumentStatus,
    KycDocumentType,
    KycStatus,
    RiskTier,
    StaffRole,
)


class MerchantOnboardRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=255)
    legal_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    pan: str = Field(
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
        description="Indian Permanent Account Number (PAN): 5 letters, 4 digits, 1 letter",
    )
    gstin: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
        description="Indian Goods and Services Tax Identification Number (GSTIN): 15 characters",
    )
    mcc_code: str = Field(
        pattern=r"^[0-9]{4}$",
        description="4-digit Merchant Category Code",
    )
    initial_upi_vpa: Optional[str] = Field(default=None, max_length=100)

    @field_validator("pan")
    @classmethod
    def validate_pan_uppercase(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("gstin")
    @classmethod
    def validate_gstin_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().upper()
        return None


class MerchantUpdateRequest(BaseModel):
    business_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    legal_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    upi_vpa: Optional[str] = Field(default=None, max_length=100)
    mcc_code: Optional[str] = Field(default=None, pattern=r"^[0-9]{4}$")


class KycDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    document_type: KycDocumentType
    document_number: str
    file_url: str
    status: KycDocumentStatus
    verified_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime


class MerchantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_name: str
    legal_name: str
    email: str
    phone: str
    kyc_status: KycStatus
    upi_vpa: Optional[str] = None
    mcc_code: Optional[str] = None
    risk_tier: RiskTier
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MerchantDetailResponse(BaseModel):
    merchant: MerchantResponse
    kyc_documents: List[KycDocumentResponse]


class StaffAssignRequest(BaseModel):
    user_id: Optional[uuid.UUID] = None
    email: Optional[EmailStr] = None
    role: StaffRole = StaffRole.CASHIER
    store_id: Optional[uuid.UUID] = None


class StaffResponse(BaseModel):
    id: uuid.UUID
    merchant_id: uuid.UUID
    user_id: uuid.UUID
    user_email: str
    user_name: str
    store_id: Optional[uuid.UUID] = None
    role: StaffRole
    is_active: bool
    created_at: datetime
