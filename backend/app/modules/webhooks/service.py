import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
import app.core.rate_limit as rate_limit_module
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.modules.webhooks.models import (
    WebhookDelivery,
    WebhookDeliveryStatus,
    WebhookEventInbound,
    WebhookInboundStatus,
    WebhookSubscription,
)
from app.modules.webhooks.schemas import (
    InboundWebhookResponse,
    WebhookSubscriptionCreate,
)
from app.modules.webhooks.tasks import deliver_webhook_outbound
from app.shared.exceptions import (
    BadRequestException,
    ConflictException,
    EntityNotFoundException,
    UnauthorizedException,
)


class WebhookService:
    """Service handling Inbound simulator webhooks and Outbound merchant webhook dispatch."""

    # --------------------------------------------------------------------------
    # Inbound Webhooks (from UPI simulator)
    # --------------------------------------------------------------------------

    @staticmethod
    def verify_inbound_signature(raw_body: bytes, signature_header: Optional[str]) -> None:
        """Verifies HMAC-SHA256 signature against shared secret.

        Raises 401 UNAUTHORIZED if missing or invalid.
        """
        if not signature_header:
            raise UnauthorizedException(
                message="Missing required 'X-Webhook-Signature' header",
                code="MISSING_WEBHOOK_SIGNATURE",
            )

        expected_sig = hmac.new(
            settings.WEBHOOK_SECRET.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison preventing timing attacks
        if not hmac.compare_digest(signature_header.strip(), expected_sig):
            raise UnauthorizedException(
                message="Invalid HMAC webhook signature",
                code="INVALID_WEBHOOK_SIGNATURE",
            )

    @classmethod
    def process_inbound_webhook(
        cls,
        db: Session,
        raw_body: bytes,
        headers: Dict[str, str],
    ) -> InboundWebhookResponse:
        """Processes inbound simulator webhook with Redis SETNX concurrency lock,

        replay prevention via unique provider_event_id, and transaction state updating.
        """
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception:
            raise BadRequestException("Invalid JSON payload in webhook body", code="MALFORMED_WEBHOOK_JSON")

        # Extract or generate provider_event_id
        provider_event_id = (
            payload.get("event_id")
            or payload.get("id")
            or headers.get("x-event-id")
            or headers.get("X-Event-ID")
        )
        if not provider_event_id:
            # Fallback based on deterministic hash of body if omitted
            provider_event_id = f"evt_{hashlib.sha256(raw_body).hexdigest()[:16]}"

        # 1. Distributed Concurrency Lock (SETNX with 30s TTL)
        redis_client = rate_limit_module.get_redis_client()
        lock_key = f"payflow:lock:webhook:{provider_event_id}"
        lock_acquired = True

        if redis_client is not None:
            try:
                # SETNX with 30 seconds expiration
                lock_acquired = bool(redis_client.set(lock_key, "locked", nx=True, ex=30))
            except Exception:
                lock_acquired = True

        if not lock_acquired:
            raise ConflictException(
                message=f"Concurrent duplicate webhook delivery in progress for event '{provider_event_id}'",
                code="CONCURRENT_WEBHOOK_DELIVERY",
                details={"event_id": provider_event_id},
            )

        try:
            # 2. Replay Check: Verify if event was already processed
            existing_event = (
                db.query(WebhookEventInbound)
                .filter(WebhookEventInbound.provider_event_id == provider_event_id)
                .first()
            )
            if existing_event:
                return InboundWebhookResponse(
                    status="ignored",
                    event_id=provider_event_id,
                    message="Duplicate event already processed (replay ignored)",
                )

            # 3. Store raw payload in webhook_events_inbound
            event_type = payload.get("event_type") or payload.get("event") or "payment.updated"
            inbound_record = WebhookEventInbound(
                provider="MOCK_UPI_PROVIDER",
                provider_event_id=provider_event_id,
                event_type=event_type,
                payload=payload,
                headers=headers,
                status=WebhookInboundStatus.RECEIVED,
            )
            db.add(inbound_record)
            db.flush()

            # 4. Resolve and update matching payment_transaction
            tx_id_str = payload.get("transaction_id")
            target_status_str = payload.get("status")
            tx = None

            if tx_id_str:
                try:
                    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == uuid.UUID(str(tx_id_str))).first()
                except (ValueError, TypeError):
                    pass

            if not tx and payload.get("provider_ref_id"):
                tx = (
                    db.query(PaymentTransaction)
                    .filter(PaymentTransaction.provider_ref_id == payload["provider_ref_id"])
                    .first()
                )

            if not tx and payload.get("idempotency_key"):
                tx = (
                    db.query(PaymentTransaction)
                    .filter(PaymentTransaction.idempotency_key == payload["idempotency_key"])
                    .first()
                )

            if tx and target_status_str:
                try:
                    from app.modules.payments.service import PaymentService
                    target_status = TransactionStatus(target_status_str.upper())
                    PaymentService.transition_status(
                        db=db,
                        transaction_id=tx.id,
                        to_status=target_status,
                        reason=f"Inbound webhook update ({provider_event_id}): {event_type}",
                    )
                except Exception as exc:
                    inbound_record.status = WebhookInboundStatus.FAILED
                    inbound_record.error_message = str(exc)
                    db.commit()
                    raise

            inbound_record.status = WebhookInboundStatus.PROCESSED
            inbound_record.processed_at = datetime.now(timezone.utc)
            db.commit()

            return InboundWebhookResponse(
                status="processed",
                event_id=provider_event_id,
                transaction_id=str(tx.id) if tx else None,
                message="Inbound webhook processed successfully",
            )

        finally:
            if redis_client is not None:
                try:
                    redis_client.delete(lock_key)
                except Exception:
                    pass

    # --------------------------------------------------------------------------
    # Outbound Webhooks (to merchant endpoints)
    # --------------------------------------------------------------------------

    @staticmethod
    def create_subscription(
        db: Session,
        merchant_id: uuid.UUID,
        data: WebhookSubscriptionCreate,
    ) -> WebhookSubscription:
        """Registers a new outbound webhook subscription for a merchant."""
        secret_key = data.secret_key or secrets.token_hex(24)
        sub = WebhookSubscription(
            merchant_id=merchant_id,
            target_url=str(data.target_url),
            secret_key=secret_key,
            subscribed_events=data.subscribed_events,
            is_active=data.is_active,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub

    @staticmethod
    def list_subscriptions(
        db: Session,
        merchant_id: uuid.UUID,
    ) -> List[WebhookSubscription]:
        """Lists all webhook subscriptions for a merchant."""
        return (
            db.query(WebhookSubscription)
            .filter(WebhookSubscription.merchant_id == merchant_id)
            .order_by(WebhookSubscription.created_at.desc())
            .all()
        )

    @staticmethod
    def _matches_event(subscription_events: List[str], event_type: str) -> bool:
        """Determines if subscription receives event_type (exact or wildcard match)."""
        for subscribed in subscription_events:
            if subscribed == "*" or subscribed == event_type:
                return True
            if subscribed.endswith(".*"):
                prefix = subscribed[:-2]
                if event_type.startswith(prefix):
                    return True
        return False

    @classmethod
    def dispatch_event(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        event_type: str,
        payload: Dict[str, Any],
    ) -> List[WebhookDelivery]:
        """Dispatches an outbound event to all active subscriptions matching event_type,

        enqueueing Celery delivery tasks.
        """
        subscriptions = (
            db.query(WebhookSubscription)
            .filter(
                WebhookSubscription.merchant_id == merchant_id,
                WebhookSubscription.is_active == True,
            )
            .all()
        )

        deliveries = []
        for sub in subscriptions:
            if cls._matches_event(sub.subscribed_events, event_type):
                delivery = WebhookDelivery(
                    subscription_id=sub.id,
                    event_type=event_type,
                    payload=payload,
                    status=WebhookDeliveryStatus.PENDING,
                    attempt_count=0,
                )
                db.add(delivery)
                deliveries.append(delivery)

        db.commit()

        for d in deliveries:
            db.refresh(d)
            # Enqueue delivery task after DB commit
            try:
                deliver_webhook_outbound.delay(str(d.id))
            except Exception:
                pass

        return deliveries

    @classmethod
    def send_test_event(
        cls,
        db: Session,
        subscription_id: uuid.UUID,
    ) -> WebhookDelivery:
        """Dispatches a synthetic test ping event to verify subscription connectivity."""
        sub = db.query(WebhookSubscription).filter(WebhookSubscription.id == subscription_id).first()
        if not sub:
            raise EntityNotFoundException("WebhookSubscription", subscription_id)

        now = datetime.now(timezone.utc)
        payload = {
            "event": "test.ping",
            "message": "PayFlow webhook connectivity test",
            "subscription_id": str(sub.id),
            "merchant_id": str(sub.merchant_id),
            "timestamp": now.isoformat(),
        }

        delivery = WebhookDelivery(
            subscription_id=sub.id,
            event_type="test.ping",
            payload=payload,
            status=WebhookDeliveryStatus.PENDING,
            attempt_count=0,
        )
        db.add(delivery)
        db.commit()
        db.refresh(delivery)

        try:
            deliver_webhook_outbound.delay(str(delivery.id))
        except Exception:
            pass

        return delivery
