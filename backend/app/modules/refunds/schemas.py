"""Refunds Module Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.refunds.models import RefundStatus


class RefundCreate(BaseModel):
    """Payload to initiate a refund against a SUCCESS transaction.

    amount must be ≤ (transaction.amount − already_refunded).
    Multiple partial refunds against one transaction are allowed;
    this is a legitimate business case distinct from split-payment structuring.
    """

    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Amount to refund in INR (must not exceed remaining refundable balance)",
    )
    reason: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Human-readable refund reason (e.g. 'Customer returned item')",
    )


class RefundApproveRequest(BaseModel):
    """Optional notes when approving a refund (Manager/Owner only)."""

    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional approval notes for audit trail",
    )


class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    transaction_id: uuid.UUID
    amount: Decimal
    status: RefundStatus
    reason: str
    provider_refund_id: Optional[str] = None
    failure_reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
