"""Notifications Module Service.

Provides the generic dispatch interface `send_notification(user_id|merchant_id, channel, template, payload)`,
as well as notification querying and read receipt management for the mobile notification center.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
import uuid
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.modules.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from app.modules.notifications.schemas import MarkReadResponse, NotificationResponse
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams


class NotificationService:
    """Service for enqueueing and managing notifications."""

    @classmethod
    def send_notification(
        cls,
        merchant_id: Optional[Union[uuid.UUID, str]] = None,
        user_id: Optional[Union[uuid.UUID, str]] = None,
        channel: Union[NotificationChannel, str] = NotificationChannel.PUSH,
        template: str = "general",
        payload: Optional[Dict[str, Any]] = None,
        recipient: Optional[str] = None,
    ) -> str:
        """Enqueues a notification delivery task via Celery.

        Args:
            merchant_id: Target merchant UUID.
            user_id: Target user UUID.
            channel: Delivery channel (PUSH, SMS, EMAIL, WHATSAPP, IN_APP).
            template: Notification template key (e.g. payment_success, payment_failed, refund_processed).
            payload: Contextual parameters used to render template body.
            recipient: Explicit phone/email destination override.

        Returns:
            The Celery async task identifier string.
        """
        from app.modules.notifications.tasks import deliver_notification

        m_str = str(merchant_id) if merchant_id else None
        u_str = str(user_id) if user_id else None
        chan_str = channel.value if hasattr(channel, "value") else str(channel)

        try:
            task = deliver_notification.delay(
                user_id=u_str,
                merchant_id=m_str,
                channel=chan_str,
                template=template,
                payload=payload,
                recipient=recipient,
            )
            task_id = task.id if hasattr(task, "id") else "inline_dispatched"
            logger.info(
                "notification_enqueued",
                task_id=task_id,
                template=template,
                channel=chan_str,
                merchant_id=m_str,
                user_id=u_str,
            )
            return task_id
        except Exception as exc:
            logger.error(
                "notification_enqueue_failed",
                template=template,
                error=str(exc),
            )
            return "enqueue_error"

    @classmethod
    def list_merchant_notifications(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        pagination: PaginationParams,
        is_read: Optional[bool] = None,
    ) -> PaginatedResponse[NotificationResponse]:
        """Returns paginated notifications for the specified merchant."""
        query = db.query(Notification).filter(Notification.merchant_id == merchant_id)

        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)

        total = query.count()
        items = (
            query.order_by(Notification.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.limit)
            .all()
        )

        return PaginatedResponse.create(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            params=pagination,
        )

    @classmethod
    def mark_as_read(
        cls,
        db: Session,
        notification_id: uuid.UUID,
    ) -> MarkReadResponse:
        """Marks a notification as read with current timestamp."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise EntityNotFoundException("Notification", notification_id)

        now = datetime.now(timezone.utc)
        notification.is_read = True
        notification.read_at = now
        db.commit()
        db.refresh(notification)

        logger.info(
            "notification_marked_read",
            notification_id=str(notification_id),
            read_at=now.isoformat(),
        )

        return MarkReadResponse(
            id=notification.id,
            is_read=True,
            read_at=now,
        )

    @classmethod
    def trigger_merchant_alert(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        title: str,
        content: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        recipient: Optional[str] = None,
    ) -> Notification:
        """Directly persists an operational alert notification for a merchant."""
        notif = Notification(
            merchant_id=merchant_id,
            title=title,
            content=content,
            channel=channel,
            recipient=recipient or f"merchant_{merchant_id}",
            status=NotificationStatus.SENT,
            sent_at=datetime.now(timezone.utc),
            is_read=False,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

