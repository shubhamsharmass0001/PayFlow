import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.payment_links.models import PaymentLinkStatus


class PaymentLinkCreateRequest(BaseModel):
    expires_at: Optional[datetime] = Field(None, description="Optional link expiry datetime")
    max_uses: Optional[int] = Field(default=1, ge=1, le=1000, description="Maximum allowed payment attempts/uses")


class PaymentLinkResponse(BaseModel):
    id: uuid.UUID
    merchant_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    payment_request_id: Optional[uuid.UUID] = None
    short_code: str
    payment_url: str
    amount: Decimal
    status: PaymentLinkStatus
    expires_at: datetime
    max_uses: int
    use_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicPayPageResponse(BaseModel):
    slug: str
    merchant_name: str
    store_name: Optional[str] = None
    invoice_number: Optional[str] = None
    amount: Decimal = Field(..., description="Server-locked payable amount; client cannot tamper or modify")
    currency: str = "INR"
    purpose: Optional[str] = None
    status: PaymentLinkStatus
    expires_at: datetime
    upi_string: Optional[str] = None
    qr_data_url: Optional[str] = None
    is_mock_provider: bool = Field(
        default=True,
        description="True indicates transaction executes against PayFlow Mock Provider in prototype mode"
    )
    disclaimer: str = Field(
        default="Notice: Prototype Mock Mode. Triggering payment simulates mock settlement.",
        description="Educational and testing disclaimer"
    )
