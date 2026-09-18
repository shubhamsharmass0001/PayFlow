import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from celery.utils.log import get_task_logger
import httpx

from app.core.celery_app import celery_app
from app.modules.webhooks.models import WebhookDelivery, WebhookDeliveryStatus, WebhookSubscription

logger = get_task_logger(__name__)


@celery_app.task(name="webhooks.deliver_webhook_outbound", bind=True, max_retries=3)
def deliver_webhook_outbound(self, delivery_id_str: str):
    """Asynchronous Celery task that delivers a signed webhook payload to a merchant target URL

    with retry, exponential backoff, attempt recording in webhook_deliveries, and terminal FAILED status.
    """
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        delivery_id = uuid.UUID(delivery_id_str)
        delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery_id).first()
        if not delivery:
            logger.error(f"Webhook delivery '{delivery_id_str}' not found.")
            return {"status": "error", "message": "Delivery record not found"}

        subscription = (
            db.query(WebhookSubscription)
            .filter(WebhookSubscription.id == delivery.subscription_id)
            .first()
        )
        if not subscription or not subscription.is_active:
            delivery.status = WebhookDeliveryStatus.FAILED
            delivery.response_body = "Subscription is inactive or deleted"
            db.commit()
            return {"status": "failed", "message": "Subscription inactive"}

        # Format and sign the payload with HMAC-SHA256
        payload_json = json.dumps(delivery.payload, default=str)
        signature = hmac.new(
            subscription.secret_key.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PayFlow-Webhook-Dispatcher/1.0",
            "X-PayFlow-Signature": signature,
            "X-PayFlow-Event": delivery.event_type,
            "X-PayFlow-Delivery": str(delivery.id),
        }

        # Attempt HTTP delivery
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(
                    subscription.target_url,
                    content=payload_json,
                    headers=headers,
                )

            if 200 <= resp.status_code < 300:
                delivery.status = WebhookDeliveryStatus.DELIVERED
                delivery.response_status_code = resp.status_code
                delivery.response_body = resp.text[:1000]
                delivery.next_retry_at = None
                db.commit()
                logger.info(f"Webhook delivery '{delivery_id}' succeeded with HTTP {resp.status_code}.")
                return {"status": "delivered", "status_code": resp.status_code}
            else:
                err_msg = f"HTTP {resp.status_code}: {resp.text[:500]}"
                return _handle_delivery_failure(self, db, delivery, resp.status_code, err_msg)

        except Exception as net_exc:
            return _handle_delivery_failure(self, db, delivery, None, str(net_exc), exc=net_exc)

    finally:
        db.close()


def _handle_delivery_failure(self, db, delivery, status_code: Optional[int], err_msg: str, exc=None):
    """Updates attempt count and transitions to RETRYING or marks permanently FAILED."""
    delivery.attempt_count += 1
    delivery.response_status_code = status_code
    delivery.response_body = err_msg[:1000]

    MAX_RETRIES = 3
    if delivery.attempt_count >= MAX_RETRIES:
        delivery.status = WebhookDeliveryStatus.FAILED
        delivery.next_retry_at = None
        db.commit()
        logger.warning(
            f"Webhook delivery '{delivery.id}' permanently marked FAILED after {delivery.attempt_count} attempts."
        )
        return {
            "status": "failed",
            "attempt_count": delivery.attempt_count,
            "error": err_msg,
        }
    else:
        delivery.status = WebhookDeliveryStatus.RETRYING
        backoff_seconds = 2 ** delivery.attempt_count
        delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_seconds)
        db.commit()
        logger.info(
            f"Webhook delivery '{delivery.id}' scheduled for retry {delivery.attempt_count}/{MAX_RETRIES} in {backoff_seconds}s."
        )
        raise self.retry(countdown=backoff_seconds, exc=exc)
