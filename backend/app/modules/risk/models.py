"""Risk Module Models.

Enums Used:
    - RiskLevel:
        - LOW: Standard probability of legitimate transaction.
        - MEDIUM: Minor anomalies detected; monitored.
        - HIGH: Significant suspicious patterns (e.g. geo mismatch, device velocity).
        - CRITICAL: Known fraud vectors, blacklisted VPAs, or stolen credentials.
    - RiskAction:
        - ALLOW: Transaction authorized without friction.
        - FLAG_FOR_REVIEW: Approved but placed in post-authorization review queue.
        - CHALLENGE_2FA: Step-up authentication or MPIN re-verification triggered.
        - BLOCK: Transaction rejected immediately.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskAction(str, enum.Enum):
    ALLOW = "ALLOW"
    FLAG_FOR_REVIEW = "FLAG_FOR_REVIEW"
    CHALLENGE_2FA = "CHALLENGE_2FA"
    BLOCK = "BLOCK"


class RiskSignal(Base):
    __tablename__ = "risk_signals"

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
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_transactions.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    risk_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level"),
        default=RiskLevel.LOW,
        nullable=False,
    )
    rule_triggered: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    action_taken: Mapped[RiskAction] = mapped_column(
        Enum(RiskAction, name="risk_action"),
        default=RiskAction.ALLOW,
        nullable=False,
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )
    is_reviewed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolution_note: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    merchant = relationship("Merchant")
    transaction = relationship("PaymentTransaction")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

