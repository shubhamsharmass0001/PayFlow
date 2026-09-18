"""Reconciliation Module Models.

Enums Used:
    - ReconciliationStatus:
        - PENDING: Batch uploaded or generated, awaiting processing.
        - PROCESSING: Active comparison between internal records and provider reports.
        - MATCHED: All transactions matched perfectly without discrepancy.
        - DISCREPANCIES_FOUND: One or more discrepancies flagged for review.
        - COMPLETED: Reconciliation closed and signed off.
    - ReconciliationEntryStatus:
        - MATCHED: Amounts, timestamps, and terminal statuses align.
        - AMOUNT_MISMATCH: Bank settlement amount differs from ledger value.
        - STATUS_MISMATCH: Internal status differs from bank status.
        - MISSING_IN_INTERNAL: Found in bank statement but missing from PayFlow.
        - MISSING_IN_PROVIDER: Found in PayFlow ledger but absent from bank settlement.
"""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ReconciliationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    MATCHED = "MATCHED"
    DISCREPANCIES_FOUND = "DISCREPANCIES_FOUND"
    COMPLETED = "COMPLETED"


class ReconciliationEntryStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    STATUS_MISMATCH = "STATUS_MISMATCH"
    MISSING_IN_INTERNAL = "MISSING_IN_INTERNAL"
    MISSING_IN_PROVIDER = "MISSING_IN_PROVIDER"


class MatchStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class ReconciliationBatch(Base, TimestampMixin):
    __tablename__ = "reconciliation_batches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    batch_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    mdr_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal("0.0150"),
        nullable=False,
    )
    status: Mapped[ReconciliationStatus] = mapped_column(
        Enum(ReconciliationStatus, name="reconciliation_status"),
        default=ReconciliationStatus.PENDING,
        nullable=False,
    )
    total_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    matched_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    mismatched_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    discrepancy_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    merchant = relationship("Merchant")
    entries = relationship(
        "ReconciliationEntry",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class ReconciliationEntry(Base, TimestampMixin):
    __tablename__ = "reconciliation_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reconciliation_batches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_transactions.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    provider_ref_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    expected_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    actual_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    match_status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="reconciliation_match_status"),
        default=MatchStatus.MATCHED,
        index=True,
        nullable=False,
    )
    status: Mapped[ReconciliationEntryStatus] = mapped_column(
        Enum(ReconciliationEntryStatus, name="reconciliation_entry_status"),
        default=ReconciliationEntryStatus.MATCHED,
        nullable=False,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    batch = relationship("ReconciliationBatch", back_populates="entries")
    transaction = relationship("PaymentTransaction")
