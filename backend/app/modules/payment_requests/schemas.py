import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.payment_requests.models import PaymentRequestStatus


class PaymentRequestCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Requested payment amount, must be <= invoice remaining balance")
    purpose: Optional[str] = Field(None, max_length=255, description="Purpose or description of the payment installment")
    expires_at: Optional[datetime] = Field(None, description="Expiration deadline for this payment request")
    payer_vpa: Optional[str] = Field(None, max_length=100, description="Optional target payer UPI VPA")


class PaymentRequestResponse(BaseModel):
    id: uuid.UUID
    merchant_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    amount: Decimal
    purpose: Optional[str] = None
    status: PaymentRequestStatus
    expires_at: datetime
    payer_vpa: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
