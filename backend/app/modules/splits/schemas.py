import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.payments.models import PaymentMethod
from app.modules.splits.models import InstallmentStatus, PaymentPlanStatus, PlanType


class InstallmentCreate(BaseModel):
    label: Optional[str] = Field(None, max_length=100, description="Installment label (e.g. Deposit, Phase 1)")
    due_date: datetime = Field(..., description="Due date/time for installment settlement")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Installment portion amount in INR")


class CreatePaymentPlanRequest(BaseModel):
    plan_type: PlanType = Field(
        ...,
        description="DEPOSIT | INSTALLMENT | MILESTONE | CUSTOM_SPLIT",
    )
    installments: List[InstallmentCreate] = Field(
        ...,
        min_length=1,
        description="Ordered list of installments",
    )


class InitiateInstallmentPaymentRequest(BaseModel):
    payer_vpa: Optional[str] = Field(None, max_length=100, description="Customer VPA")
    payment_method: PaymentMethod = Field(
        default=PaymentMethod.UPI_INTENT,
        description="Payment channel / method",
    )
    scenario: Optional[MockScenario] = Field(
        None,
        description="Dev/Testing explicit mock simulator scenario override",
    )


class PaymentPlanInstallmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_plan_id: uuid.UUID
    installment_number: int
    label: Optional[str] = None
    amount: Decimal
    paid_amount: Decimal
    due_date: datetime
    status: InstallmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None


class PaymentPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    plan_type: PlanType
    total_amount: Decimal
    status: PaymentPlanStatus
    installments: List[PaymentPlanInstallmentResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
