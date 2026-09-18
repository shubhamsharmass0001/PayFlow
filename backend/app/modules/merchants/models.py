"""Merchants Module Models.

Enums Used:
    - KycStatus:
        - PENDING: Initial state when merchant registers.
        - UNDER_REVIEW: Documents submitted and undergoing review.
        - APPROVED: Verification successful, transactions enabled.
        - REJECTED: Verification failed or non-compliant.
    - RiskTier:
        - LOW: Trusted merchant with established volume and low dispute rates.
        - MEDIUM: Standard operational merchant with normal monitoring.
        - HIGH: Elevated dispute rates or high-risk business category.
        - PROHIBITED: Banned from processing transactions.
    - KycDocumentType:
        - PAN: Permanent Account Number card.
        - GSTIN: Goods and Services Tax Identification Number certificate.
        - INCORPORATION_CERT: Certificate of Incorporation or Business Registration.
        - BANK_STATEMENT: Cancelled cheque or recent bank statement.
        - AADHAAR: Identity proof document.
        - OTHER: Additional supporting regulatory document.
    - KycDocumentStatus:
        - SUBMITTED: Uploaded and awaiting compliance review.
        - VERIFIED: Document verified against issuing authority.
        - REJECTED: Document unreadable, expired, or invalid.
    - StaffRole:
        - OWNER: Full account control and financial settlement rights.
        - ADMIN: Operations and team configuration.
        - MANAGER: Store-level transaction and invoice management.
        - CASHIER: Payment collection and receipt issuance only.
        - ACCOUNTANT: Financial reporting and reconciliation access.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class KycStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RiskTier(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PROHIBITED = "PROHIBITED"


class KycDocumentType(str, enum.Enum):
    PAN = "PAN"
    GSTIN = "GSTIN"
    INCORPORATION_CERT = "INCORPORATION_CERT"
    BANK_STATEMENT = "BANK_STATEMENT"
    AADHAAR = "AADHAAR"
    OTHER = "OTHER"


class KycDocumentStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class StaffRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CASHIER = "CASHIER"
    ACCOUNTANT = "ACCOUNTANT"


class Merchant(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    business_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    legal_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
    )
    kyc_status: Mapped[KycStatus] = mapped_column(
        Enum(KycStatus, name="merchant_kyc_status"),
        default=KycStatus.PENDING,
        nullable=False,
    )
    upi_vpa: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    mcc_code: Mapped[Optional[str]] = mapped_column(
        String(4),
        nullable=True,
    )
    risk_tier: Mapped[RiskTier] = mapped_column(
        Enum(RiskTier, name="merchant_risk_tier"),
        default=RiskTier.MEDIUM,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    kyc_documents = relationship(
        "MerchantKycDocument",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    staff = relationship(
        "MerchantStaff",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )


class MerchantKycDocument(Base, TimestampMixin):
    __tablename__ = "merchant_kyc_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    document_type: Mapped[KycDocumentType] = mapped_column(
        Enum(KycDocumentType, name="kyc_document_type"),
        nullable=False,
    )
    document_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    file_url: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    status: Mapped[KycDocumentStatus] = mapped_column(
        Enum(KycDocumentStatus, name="kyc_document_status"),
        default=KycDocumentStatus.SUBMITTED,
        nullable=False,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    merchant = relationship("Merchant", back_populates="kyc_documents")


class MerchantStaff(Base, TimestampMixin):
    __tablename__ = "merchant_staff"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    role: Mapped[StaffRole] = mapped_column(
        Enum(StaffRole, name="merchant_staff_role"),
        default=StaffRole.CASHIER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    merchant = relationship("Merchant", back_populates="staff")
