"""Payment Links Module Models.

Enums Used:
    - PaymentLinkStatus:
        - ACTIVE: Link is live and accessible for payment.
        - PAID: Full payment received via this link.
        - EXPIRED: Link reached its expiration deadline.
        - CANCELLED: Deactivated by the merchant before payment.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class PaymentLinkStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class PaymentLink(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "payment_links"

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
    payment_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_requests.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    short_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    status: Mapped[PaymentLinkStatus] = mapped_column(
        Enum(PaymentLinkStatus, name="payment_link_status"),
        default=PaymentLinkStatus.ACTIVE,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    max_uses: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )
    use_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    allow_partial: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    merchant = relationship("Merchant")
    invoice = relationship("Invoice")
    customer = relationship("Customer")
    payment_request = relationship("PaymentRequest")
