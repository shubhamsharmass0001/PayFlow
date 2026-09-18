"""Settlements Module Models.

IMPORTANT — MDR / fee notice:
  All fee computations (MDR rate, GST on MDR, net payout) in this module are
  ILLUSTRATIVE and MOCK only. They do not reflect live NPCI fee schedules,
  interchange tariffs, or any real banking rate card. They exist purely for
  prototype simulation.

Enums Used:
    - SettlementCycle:
        - T_PLUS_0: Same-day real-time settlement.
        - T_PLUS_1: Next business day standard payout.
        - T_PLUS_2: Extended two-business-day cycle.
        - ON_DEMAND: Instant payout requested manually by merchant.
    - SettlementStatus:
        - PENDING: Batch compiled, awaiting payout instruction generation.
        - PROCESSING: Payout batch submitted to nodal bank / payment gateway.
        - SETTLED: Bank confirmed UTR and funds credited to merchant account.
        - FAILED: Bank rejected payout (e.g. invalid IFSC, account frozen).
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
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SettlementCycle(str, enum.Enum):
    T_PLUS_0 = "T_PLUS_0"
    T_PLUS_1 = "T_PLUS_1"
    T_PLUS_2 = "T_PLUS_2"
    ON_DEMAND = "ON_DEMAND"


class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


class Settlement(Base, TimestampMixin):
    __tablename__ = "settlements"

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
    # The source reconciliation batch that triggered this settlement
    reconciliation_batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reconciliation_batches.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    settlement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    settlement_cycle: Mapped[SettlementCycle] = mapped_column(
        Enum(SettlementCycle, name="settlement_cycle"),
        default=SettlementCycle.T_PLUS_1,
        nullable=False,
    )
    # Transaction count for this settlement batch
    transaction_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    # Pre-aggregated financial fields (chart-ready)
    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    mdr_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Illustrative MDR deduction — mock only, not a live fee schedule",
    )
    tax_on_mdr: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Illustrative 18% GST on MDR — mock only",
    )
    deduction_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=True,
        comment="Total deductions (mdr_amount + tax_on_mdr)",
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="= gross_amount - mdr_amount - tax_on_mdr",
    )
    status: Mapped[SettlementStatus] = mapped_column(
        Enum(SettlementStatus, name="settlement_status"),
        default=SettlementStatus.PENDING,
        nullable=False,
    )
    # Mock UTR: Unique Transaction Reference issued by the nodal bank.
    # In this prototype this is a simulated reference and does NOT represent
    # a real NEFT/IMPS UTR number.
    utr_reference: Mapped[Optional[str]] = mapped_column(
        String(50),
        index=True,
        nullable=True,
        comment="Mock UTR reference — illustrative only, not a live bank UTR",
    )
    bank_account_ref: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    settled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    merchant = relationship("Merchant")
    line_items = relationship(
        "SettlementLineItem",
        back_populates="settlement",
        cascade="all, delete-orphan",
    )


class SettlementLineItem(Base):
    __tablename__ = "settlement_line_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id", ondelete="CASCADE"),
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
        comment="Gross transaction amount",
    )
    fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Illustrative MDR fee per transaction",
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Illustrative 18% GST on the MDR fee",
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="amount - fee_amount - tax_amount",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    settlement = relationship("Settlement", back_populates="line_items")
    transaction = relationship("PaymentTransaction")
