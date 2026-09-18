import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session

from app.core.rate_limit import rate_limit_dependency
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission
from app.modules.webhooks.schemas import (
    InboundWebhookResponse,
    WebhookDeliveryResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)
from app.modules.webhooks.service import WebhookService

router = APIRouter(tags=["Webhooks"])


@router.post(
    "/webhooks/upi-mock/inbound",
    response_model=InboundWebhookResponse,
    summary="Process inbound webhook from UPI simulator",
    dependencies=[Depends(rate_limit_dependency(max_requests=120, window_seconds=60, key_prefix="webhook_inbound"))],
)
async def inbound_upi_mock_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
    db: Session = Depends(get_db),
):
    """Inbound webhook callback receiver for UPI simulator payments.

    Validates HMAC-SHA256 signature in X-Webhook-Signature header, guards against
    concurrency with Redis SETNX lock, detects replays via unique provider_event_id,
    and transitions payment_transaction status with immutable audit logging.
    """
    raw_body = await request.body()
    WebhookService.verify_inbound_signature(raw_body, x_webhook_signature)

    headers_dict = {k.lower(): v for k, v in request.headers.items()}
    return WebhookService.process_inbound_webhook(
        db=db,
        raw_body=raw_body,
        headers=headers_dict,
    )


@router.get(
    "/merchants/{id}/webhook-subscriptions",
    response_model=List[WebhookSubscriptionResponse],
    summary="List merchant outbound webhook subscriptions",
)
def list_merchant_webhook_subscriptions(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff:read")),
):
    """Retrieves all outbound webhook subscriptions configured for a merchant."""
    return WebhookService.list_subscriptions(db=db, merchant_id=id)


@router.post(
    "/merchants/{id}/webhook-subscriptions",
    response_model=WebhookSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new outbound webhook subscription",
)
def create_merchant_webhook_subscription(
    id: uuid.UUID,
    payload: WebhookSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff:write")),
):
    """Registers a new outbound webhook subscription for a merchant.

    Signs events with secret_key via HMAC-SHA256.
    """
    return WebhookService.create_subscription(
        db=db,
        merchant_id=id,
        data=payload,
    )


@router.post(
    "/webhook-subscriptions/{id}/test",
    response_model=WebhookDeliveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a synthetic test event to a webhook subscription",
)
def test_webhook_subscription(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Dispatches a synthetic test.ping event to test merchant endpoint connectivity."""
    return WebhookService.send_test_event(db=db, subscription_id=id)
