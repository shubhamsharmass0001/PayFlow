"""Webhooks Module Models.

Enums Used:
    - WebhookInboundStatus:
        - RECEIVED: Webhook payload captured and queued for processing.
        - PROCESSED: Successfully dispatched and transaction state updated.
        - FAILED: Processing encountered validation or application error.
        - IGNORED: Duplicate or unsupported event type.
    - WebhookDeliveryStatus:
        - PENDING: Queued for outbound delivery to merchant endpoint.
        - DELIVERED: Successfully received 2xx response from merchant webhook.
        - FAILED: Max retry attempts reached without 2xx acknowledgement.
        - RETRYING: Temporary delivery error; scheduled for exponential backoff retry.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class WebhookInboundStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    IGNORED = "IGNORED"


class WebhookDeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class WebhookEventInbound(Base, TimestampMixin):
    __tablename__ = "webhook_events_inbound"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    provider_event_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    headers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )
    status: Mapped[WebhookInboundStatus] = mapped_column(
        Enum(WebhookInboundStatus, name="webhook_inbound_status"),
        default=WebhookInboundStatus.RECEIVED,
        nullable=False,
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


class WebhookSubscription(Base, TimestampMixin):
    __tablename__ = "webhook_subscriptions"

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
    target_url: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    secret_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    subscribed_events: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    merchant = relationship("Merchant")
    deliveries = relationship(
        "WebhookDelivery",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )


class WebhookDelivery(Base, TimestampMixin):
    __tablename__ = "webhook_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    response_status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    response_body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    status: Mapped[WebhookDeliveryStatus] = mapped_column(
        Enum(WebhookDeliveryStatus, name="webhook_delivery_status"),
        default=WebhookDeliveryStatus.PENDING,
        nullable=False,
    )
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    subscription = relationship("WebhookSubscription", back_populates="deliveries")
