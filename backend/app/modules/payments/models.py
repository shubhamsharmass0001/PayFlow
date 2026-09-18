"""Payments Module Models.

Enums Used:
    - TransactionStatus:
        - INITIATED: Order / payment session created, awaiting customer action.
        - PENDING: Processing with NPCI / acquiring bank.
        - SUCCESS: Payment cleared, verified, and funds transferred.
        - FAILED: Declined by customer, bank, or validation failure.
        - TIMEOUT: Transaction timed out awaiting provider response.
        - REFUNDED: Total amount reversed to payer.
        - PARTIALLY_REFUNDED: Partial refund issued against transaction.
    - PaymentMethod:
        - UPI_COLLECT: Collect request sent to payer VPA.
        - UPI_INTENT: App-to-app deep-link intent invocation.
        - UPI_QR: Dynamic or static QR code scan and pay.
        - CARD: Credit or Debit card payment.
        - NET_BANKING: Direct net banking transfer.
        - WALLET: Prepaid wallet balance.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TransactionStatus(str, enum.Enum):
    CREATED = "CREATED"
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    DUPLICATE = "DUPLICATE"
    REFUND_INITIATED = "REFUND_INITIATED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    REFUND_FAILED = "REFUND_FAILED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"


class PaymentMethod(str, enum.Enum):
    UPI_COLLECT = "UPI_COLLECT"
    UPI_INTENT = "UPI_INTENT"
    UPI_QR = "UPI_QR"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class PaymentTransaction(Base, TimestampMixin):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        Index("ix_payment_transactions_merchant_status", "merchant_id", "status"),
        Index("ix_payment_transactions_merchant_created", "merchant_id", "created_at"),
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
    payment_link_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_links.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    upi_qr_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("upi_qr_codes.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    installment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_plan_installments.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status"),
        default=TransactionStatus.INITIATED,
        index=True,
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method"),
        default=PaymentMethod.UPI_QR,
        nullable=False,
    )
    mock_scenario: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    provider_ref_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    payer_vpa: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    payee_vpa: Mapped[Optional[str]] = mapped_column(
        String(100),
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
    invoice = relationship("Invoice")
    customer = relationship("Customer")
    status_history = relationship(
        "TransactionStatusHistory",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )


class TransactionStatusHistory(Base):
    __tablename__ = "transaction_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_transactions.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    from_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    to_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    transaction = relationship("PaymentTransaction", back_populates="status_history")
