"""Audit Module Models.

Enums Used:
    - AuditAction:
        - CREATE: New record / entity created.
        - UPDATE: Existing record attributes modified.
        - DELETE: Record soft or hard deleted.
        - LOGIN: User authenticated successfully.
        - LOGOUT: User session terminated.
        - STATUS_CHANGE: State machine transition (e.g. invoice or transaction status).
        - REFUND_TRIGGER: Operational manual or automated refund initiated.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    STATUS_CHANGE = "STATUS_CHANGE"
    REFUND_TRIGGER = "REFUND_TRIGGER"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_name", "entity_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    entity_name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
    )
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action"),
        nullable=False,
    )
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    merchant = relationship("Merchant")
    user = relationship("User")
