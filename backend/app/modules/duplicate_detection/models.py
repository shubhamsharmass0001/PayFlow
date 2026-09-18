"""Duplicate Detection Module Models.

Enums Used:
    - DuplicateFlagReason:
        - IDENTICAL_IDEMPOTENCY_KEY: Replayed payload with same idempotency token.
        - IDENTICAL_AMOUNT_AND_VPA: Same amount and payer VPA within rapid threshold window.
        - TIMEFRAME_BURST: Suspicious rapid-fire submissions.
        - PROVIDER_RRN_COLLISION: Banking RRN / reference collision detected.
    - DuplicateFlagStatus:
        - SUSPECTED: Flagged automatically by detection rules.
        - CONFIRMED_DUPLICATE: Verified duplicate payment; hold or refund recommended.
        - FALSE_POSITIVE: Validated as legitimate distinct transactions.
        - RESOLVED: Manually or automatically cleared.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DuplicateFlagReason(str, enum.Enum):
    IDENTICAL_IDEMPOTENCY_KEY = "IDENTICAL_IDEMPOTENCY_KEY"
    IDENTICAL_AMOUNT_AND_VPA = "IDENTICAL_AMOUNT_AND_VPA"
    TIMEFRAME_BURST = "TIMEFRAME_BURST"
    PROVIDER_RRN_COLLISION = "PROVIDER_RRN_COLLISION"


class DuplicateFlagStatus(str, enum.Enum):
    SUSPECTED = "SUSPECTED"
    CONFIRMED_DUPLICATE = "CONFIRMED_DUPLICATE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"


class DuplicateTransactionFlag(Base, TimestampMixin):
    __tablename__ = "duplicate_transaction_flags"

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
    original_transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_transactions.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    duplicate_transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_transactions.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal("1.0000"),
        nullable=False,
    )
    flag_reason: Mapped[DuplicateFlagReason] = mapped_column(
        Enum(DuplicateFlagReason, name="duplicate_flag_reason"),
        nullable=False,
    )
    match_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[DuplicateFlagStatus] = mapped_column(
        Enum(DuplicateFlagStatus, name="duplicate_flag_status"),
        default=DuplicateFlagStatus.SUSPECTED,
        nullable=False,
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolution_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    merchant = relationship("Merchant")
    original_transaction = relationship(
        "PaymentTransaction",
        foreign_keys=[original_transaction_id],
    )
    duplicate_transaction = relationship(
        "PaymentTransaction",
        foreign_keys=[duplicate_transaction_id],
    )
    resolver = relationship("User")
