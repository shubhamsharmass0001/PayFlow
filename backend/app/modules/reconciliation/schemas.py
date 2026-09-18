"""Reconciliation Module Schemas."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.reconciliation.models import (
    MatchStatus,
    ReconciliationEntryStatus,
    ReconciliationStatus,
)


class ReconciliationRunRequest(BaseModel):
    """Request payload for triggering an on-demand reconciliation run."""
    period_start: Optional[datetime] = Field(
        None,
        description="Start timestamp of the reconciliation window (defaults to 24h prior)",
    )
    period_end: Optional[datetime] = Field(
        None,
        description="End timestamp of the reconciliation window (defaults to current time)",
    )
    mdr_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Illustrative mock MDR fee rate (e.g. 0.015 for 1.5%). NOTE: Illustrative/mock only.",
    )
    tolerance: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Variance tolerance threshold in INR (defaults to 0.05)",
    )
    grace_period_hours: Optional[int] = Field(
        None,
        ge=0,
        description="Grace period in hours before an un-settled transaction is flagged UNMATCHED (defaults to 24)",
    )


class ReconciliationEntryResponse(BaseModel):
    """Represents a single transaction reconciliation item."""
    id: uuid.UUID
    batch_id: uuid.UUID
    transaction_id: Optional[uuid.UUID] = None
    provider_ref_id: Optional[str] = None
    expected_amount: Decimal
    actual_amount: Decimal
    match_status: MatchStatus
    status: ReconciliationEntryStatus
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReconciliationBatchResponse(BaseModel):
    """Summary of a reconciliation batch execution."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    batch_date: date
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    mdr_rate: Decimal
    status: ReconciliationStatus
    total_records: int
    matched_records: int
    mismatched_records: int
    discrepancy_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReconciliationBatchDetailResponse(ReconciliationBatchResponse):
    """Detailed reconciliation batch including child entry records."""
    entries: List[ReconciliationEntryResponse] = []
