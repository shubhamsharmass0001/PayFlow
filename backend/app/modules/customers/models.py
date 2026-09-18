"""Customers Module Models.

Enums Used:
    None (Customer profiles use standard identity attributes).
"""

import uuid
from typing import Optional
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_merchant_phone", "merchant_id", "phone"),
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
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
        nullable=True,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
    )
    upi_vpa: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    merchant = relationship("Merchant")
