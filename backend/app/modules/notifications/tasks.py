"""Notifications Module Celery Tasks.

Dispatches operational notifications via asynchronous background workers.

Architecture & Production Notice:
  For this prototype build, "sending" SMS, Email, or Push notifications means:
  1. Emitting a realistic-looking structured log entry.
  2. Persisting an immutable notification row in the database with status SENT.
  
  In a production build:
  - PUSH notifications would dispatch via Firebase Cloud Messaging (FCM) to registered
    device tokens for the Flutter mobile application (Phase 23/24). Real FCM provider
    credentials are NOT faked here per system architecture specifications.
  - SMS notifications would dispatch via SMS gateway providers (e.g. Twilio, Gupshup).
  - Email notifications would dispatch via transactional SMTP (e.g. AWS SES, SendGrid).
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from app.core.celery_app import celery_app
from app.core.logging import logger
from app.modules.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)


def _render_template(template: str, payload: Optional[Dict[str, Any]] = None) -> tuple[str, str]:
    """Generates realistic title and body text based on event template and parameters."""
    data = payload or {}
    
    if template == "payment_success":
        amount = data.get("amount", "0.00")
        tx_id = data.get("transaction_id", "N/A")[:8]
        return (
            "Payment Received",
            f"Successfully collected INR {amount} via UPI (Txn #{tx_id}). Funds allocated for payout.",
        )
    elif template == "payment_failed":
        amount = data.get("amount", "0.00")
        reason = data.get("reason") or "Card/VPA transaction declined by bank"
        return (
            "Payment Attempt Failed",
            f"Payment of INR {amount} could not be completed. Reason: {reason}.",
        )
    elif template == "refund_processed":
        amount = data.get("amount", "0.00")
        tx_id = data.get("transaction_id", "N/A")[:8]
        return (
            "Refund Processed",
            f"Refund of INR {amount} successfully initiated for transaction #{tx_id}.",
        )
    elif template == "invoice_overdue":
        inv_num = data.get("invoice_number", data.get("invoice_id", "N/A"))
        amount = data.get("amount", "0.00")
        due_date = data.get("due_date", "earlier today")
        return (
            "Invoice Overdue Alert",
            f"Invoice #{inv_num} for INR {amount} is overdue past due date {due_date}.",
        )
    elif template == "risk_signal_raised":
        rule = data.get("rule_triggered", "ANOMALOUS_VELOCITY")
        level = data.get("risk_level", "HIGH")
        score = data.get("risk_score", "75.00")
        return (
            f"Risk Signal Alert: {level}",
            f"Risk guardrail [{rule}] flagged activity (Risk Score: {score}/100). Flagged for compliance review.",
        )
    else:
        title = template.replace("_", " ").title()
        content = data.get("message") or f"Notification for event: {template}"
        return title, content


@celery_app.task(name="notifications.deliver")
def deliver_notification(
    user_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    channel: str = "PUSH",
    template: str = "general",
    payload: Optional[Dict[str, Any]] = None,
    recipient: Optional[str] = None,
) -> Dict[str, Any]:
    """Background task delivering a notification and recording it in the ledger."""
    from app.db.session import SessionLocal
    from app.modules.auth.models import User
    from app.modules.merchants.models import Merchant

    db = SessionLocal()
    try:
        m_uuid = uuid.UUID(merchant_id) if merchant_id else None
        u_uuid = uuid.UUID(user_id) if user_id else None

        # Resolve channel enum
        try:
            chan_enum = NotificationChannel(channel.upper())
        except (ValueError, KeyError):
            chan_enum = NotificationChannel.PUSH

        # Resolve realistic recipient if missing
        effective_recipient = recipient
        if not effective_recipient:
            if u_uuid:
                u = db.query(User).filter(User.id == u_uuid).first()
                if u:
                    effective_recipient = u.email or u.phone or f"user_{str(u_uuid)[:8]}"
            if not effective_recipient and m_uuid:
                m = db.query(Merchant).filter(Merchant.id == m_uuid).first()
                if m:
                    effective_recipient = m.email or m.phone or f"merchant_{str(m_uuid)[:8]}"
        if not effective_recipient:
            effective_recipient = "merchant_admin"

        title, content = _render_template(template, payload)
        now = datetime.now(timezone.utc)

        # Realistic provider logging (FCM push / SMS / Email)
        logger.info(
            "mock_notification_dispatched",
            channel=chan_enum.value,
            provider="FCM_MOCK" if chan_enum == NotificationChannel.PUSH else "COMM_GATEWAY_MOCK",
            recipient=effective_recipient,
            template=template,
            title=title,
            merchant_id=str(m_uuid) if m_uuid else None,
            user_id=str(u_uuid) if u_uuid else None,
            sent_at=now.isoformat(),
        )

        notification = Notification(
            user_id=u_uuid,
            merchant_id=m_uuid,
            recipient=effective_recipient,
            channel=chan_enum,
            template=template,
            payload=payload,
            title=title,
            content=content,
            status=NotificationStatus.SENT,
            is_read=False,
            sent_at=now,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        return {
            "status": "SENT",
            "notification_id": str(notification.id),
            "recipient": effective_recipient,
            "channel": chan_enum.value,
            "template": template,
        }
    except Exception as exc:
        db.rollback()
        logger.error(
            "notification_delivery_failed",
            template=template,
            error=str(exc),
        )
        return {
            "status": "FAILED",
            "error": str(exc),
        }
    finally:
        db.close()
