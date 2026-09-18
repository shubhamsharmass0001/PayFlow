"""UPI QR Module Models.

Enums Used:
    - QrType:
        - STATIC: Permanent merchant/store QR without preset amount.
        - DYNAMIC: Transaction/invoice-specific QR with embedded amount and expiry.
    - QrStatus:
        - ACTIVE: Enabled and accepting payments.
        - INACTIVE: Temporarily paused by merchant.
        - EXPIRED: Validity timeframe has lapsed.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class QrType(str, enum.Enum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"


class QrStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class UpiQrCode(Base, TimestampMixin):
    __tablename__ = "upi_qr_codes"

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
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    payment_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_requests.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    qr_type: Mapped[QrType] = mapped_column(
        Enum(QrType, name="qr_type"),
        default=QrType.DYNAMIC,
        nullable=False,
    )
    upi_string: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    status: Mapped[QrStatus] = mapped_column(
        Enum(QrStatus, name="qr_status"),
        default=QrStatus.ACTIVE,
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    merchant = relationship("Merchant")
    store = relationship("Store")
    invoice = relationship("Invoice")
    payment_request = relationship("PaymentRequest")
