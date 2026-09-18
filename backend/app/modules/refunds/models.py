"""Refunds Module Models.

Enums Used:
    - RefundStatus:
        - INITIATED: Refund requested by merchant or customer support.
        - PENDING: Processing with acquiring bank or UPI network.
        - SUCCESS: Amount credited back to payer source account.
        - FAILED: Refund rejected by bank or account closed.
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
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class RefundStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Refund(Base, TimestampMixin):
    __tablename__ = "refunds"

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
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_transactions.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    status: Mapped[RefundStatus] = mapped_column(
        Enum(RefundStatus, name="refund_status"),
        default=RefundStatus.INITIATED,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    provider_refund_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    merchant = relationship("Merchant")
    transaction = relationship("PaymentTransaction")
