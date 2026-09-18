"""Payment Requests Module Models.

Enums Used:
    - PaymentRequestStatus:
        - PENDING: Request initiated and sent to the payer VPA.
        - COMPLETED: Payer approved and payment was successfully processed.
        - EXPIRED: Time window elapsed before approval.
        - CANCELLED: Explicitly withdrawn by merchant or payer.
        - FAILED: Declined or payment gateway failure.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PaymentRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PaymentRequest(Base, TimestampMixin):
    __tablename__ = "payment_requests"
    __table_args__ = (
        Index("ix_payment_requests_merchant_status", "merchant_id", "status"),
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
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    status: Mapped[PaymentRequestStatus] = mapped_column(
        Enum(PaymentRequestStatus, name="payment_request_status"),
        default=PaymentRequestStatus.PENDING,
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    payer_vpa: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    purpose: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    merchant = relationship("Merchant")
    invoice = relationship("Invoice")
    customer = relationship("Customer")
