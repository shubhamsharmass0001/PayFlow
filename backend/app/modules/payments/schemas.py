import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.payments.models import PaymentMethod, TransactionStatus


class InitiatePaymentRequest(BaseModel):
    merchant_id: uuid.UUID = Field(..., description="Target merchant identifier")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount in INR")
    currency: str = Field(default="INR", max_length=3, description="Currency code")
    invoice_id: Optional[uuid.UUID] = Field(None, description="Associated invoice UUID")
    customer_id: Optional[uuid.UUID] = Field(None, description="Associated customer UUID")
    payment_method: PaymentMethod = Field(
        default=PaymentMethod.UPI_INTENT,
        description="Payment channel / method",
    )
    payer_vpa: Optional[str] = Field(None, max_length=100, description="Customer VPA")
    payee_vpa: Optional[str] = Field(None, max_length=100, description="Merchant receiving VPA")
    installment_id: Optional[uuid.UUID] = Field(None, description="Associated payment plan installment UUID")
    scenario: Optional[MockScenario] = Field(
        None,
        description="Dev/Testing explicit mock simulator scenario override",
    )


class TransactionStatusHistoryResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    from_status: Optional[str] = None
    to_status: str
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    payment_link_id: Optional[uuid.UUID] = None
    upi_qr_id: Optional[uuid.UUID] = None
    installment_id: Optional[uuid.UUID] = None
    idempotency_key: str
    amount: Decimal
    currency: str
    status: TransactionStatus
    payment_method: PaymentMethod
    mock_scenario: Optional[str] = None
    provider_ref_id: Optional[str] = None
    payer_vpa: Optional[str] = None
    payee_vpa: Optional[str] = None
    failure_reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status_history: List[TransactionStatusHistoryResponse] = []
