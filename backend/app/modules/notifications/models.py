"""Notifications Module Models.

Enums Used:
    - NotificationChannel:
        - SMS: Cellular Short Message Service alert.
        - EMAIL: Transaction receipt or invoice email.
        - WHATSAPP: WhatsApp Business interactive template message.
        - WEBHOOK: Direct programmatic callback notification.
        - IN_APP: In-app notification card / push alert.
    - NotificationStatus:
        - QUEUED: Enqueued in Celery or broker pipeline.
        - SENT: Dispatched to communications provider gateway.
        - DELIVERED: Delivery receipt confirmed.
        - FAILED: Gateway error or invalid recipient address.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class NotificationChannel(str, enum.Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    WEBHOOK = "WEBHOOK"
    IN_APP = "IN_APP"
    PUSH = "PUSH"


class NotificationStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    merchant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    recipient: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notification_channel"),
        default=NotificationChannel.IN_APP,
        nullable=False,
    )
    template: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    payload: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"),
        default=NotificationStatus.SENT,
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    merchant = relationship("Merchant")
    user = relationship("User")
