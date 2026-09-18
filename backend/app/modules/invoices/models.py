"""Invoices Module Models.

Enums Used:
    - InvoiceStatus:
        - DRAFT: Created but not yet finalized or sent to the customer.
        - ISSUED: Finalized and dispatched for payment.
        - PARTIALLY_PAID: Received partial payment against total invoice amount.
        - PAID: Fully settled and cleared.
        - CANCELLED: Revoked before payment.
        - OVERDUE: Due date elapsed without full payment.
        - REFUNDED: Settled payment was refunded back to customer.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"
    REFUNDED = "REFUNDED"


class Invoice(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("merchant_id", "invoice_number", name="uq_invoices_merchant_number"),
        Index("ix_invoices_merchant_status", "merchant_id", "status"),
    )

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
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    invoice_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    tax_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    discount_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status"),
        default=InvoiceStatus.DRAFT,
        index=True,
        nullable=False,
    )
    allow_partial_payment: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    allow_split_payment: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    merchant = relationship("Merchant")
    store = relationship("Store")
    customer = relationship("Customer")
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
