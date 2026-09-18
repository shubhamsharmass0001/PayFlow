"""Duplicate Detection Module Schemas."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.duplicate_detection.models import (
    DuplicateFlagReason,
    DuplicateFlagStatus,
)


class ResolveDuplicateFlagRequest(BaseModel):
    """Payload for resolving a suspected duplicate transaction flag."""
    reason: str = Field(..., min_length=1, description="Reason for marking the flag resolved")
    resolved_by: Optional[uuid.UUID] = Field(None, description="Optional user ID resolving the flag")


class DuplicateFlagResponse(BaseModel):
    """Full detail of a duplicate transaction flag."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    original_transaction_id: uuid.UUID
    duplicate_transaction_id: uuid.UUID
    confidence_score: Decimal
    flag_reason: DuplicateFlagReason
    match_reason: Optional[str] = None
    status: DuplicateFlagStatus
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DuplicateFlagSummaryResponse(BaseModel):
    """Summary count of unresolved duplicate flags for a merchant."""
    merchant_id: uuid.UUID
    unresolved_count: int
