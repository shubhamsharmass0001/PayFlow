"""Splits & Payment Plans Module Models.

Enums Used:
    - PlanType:
        - DEPOSIT: Upfront booking deposit followed by balance at completion.
        - INSTALLMENT: Periodic recurring payment splits (e.g. monthly/weekly).
        - MILESTONE: Release payments tied to project/delivery milestones.
        - CUSTOM_SPLIT: Custom flexible proportion or percentage split.
    - PaymentPlanStatus:
        - ACTIVE: Plan is in progress with remaining installments.
        - COMPLETED: All installments fulfilled and cleared.
        - CANCELLED: Terminated before completion.
        - DEFAULTED: Unpaid past grace period threshold.
    - InstallmentStatus:
        - PENDING: Due in future or awaiting settlement.
        - PARTIALLY_PAID: Part of installment amount received.
        - PAID: Fully settled installment.
        - OVERDUE: Due date passed without payment.
        - CANCELLED: Installment voided.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class PlanType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    INSTALLMENT = "INSTALLMENT"
    MILESTONE = "MILESTONE"
    CUSTOM_SPLIT = "CUSTOM_SPLIT"


class PaymentPlanStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DEFAULTED = "DEFAULTED"


class InstallmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class PaymentPlan(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "payment_plans"

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
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    plan_type: Mapped[PlanType] = mapped_column(
        Enum(PlanType, name="plan_type"),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    status: Mapped[PaymentPlanStatus] = mapped_column(
        Enum(PaymentPlanStatus, name="payment_plan_status"),
        default=PaymentPlanStatus.ACTIVE,
        nullable=False,
    )

    merchant = relationship("Merchant")
    invoice = relationship("Invoice")
    customer = relationship("Customer")
    installments = relationship(
        "PaymentPlanInstallment",
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class PaymentPlanInstallment(Base, TimestampMixin):
    __tablename__ = "payment_plan_installments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    payment_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_plans.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    installment_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    label: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[InstallmentStatus] = mapped_column(
        Enum(InstallmentStatus, name="installment_status"),
        default=InstallmentStatus.PENDING,
        nullable=False,
    )

    plan = relationship("PaymentPlan", back_populates="installments")
