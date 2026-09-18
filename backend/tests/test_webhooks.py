import hashlib
import hmac
import json
import uuid
from decimal import Decimal
import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.webhooks.models import (
    WebhookDelivery,
    WebhookDeliveryStatus,
    WebhookEventInbound,
    WebhookInboundStatus,
    WebhookSubscription,
)
from app.modules.webhooks.service import WebhookService
from app.modules.webhooks.tasks import deliver_webhook_outbound


def _calc_signature(secret: str, payload_bytes: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


@pytest.fixture
def setup_webhook_env(client: TestClient, db: Session):
    """Sets up an owner, merchant, customer, invoice, and payment transaction."""
    # Register owner
    owner_email = f"webhookowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Webhook Test Owner",
            "phone": owner_phone,
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]
    owner_id = uuid.UUID(reg.json()["user"]["id"])

    # Create merchant
    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Webhook Labs",
            "legal_name": "Webhook Labs Pvt Ltd",
            "email": f"webhooks_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9195{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5732",
            "initial_upi_vpa": "webhooklabs@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    # Create customer
    c_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Ananya Sen",
            "email": f"ananya_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9194{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(c_resp.json()["id"])

    # Create invoice directly
    inv = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-WH-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("1000.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        allow_partial_payment=True,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Create payment transaction in PENDING status
    idemp_key = f"idemp_{uuid.uuid4().hex}"
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=inv.id,
        customer_id=customer_id,
        amount=Decimal("500.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        idempotency_key=idemp_key,
        status=TransactionStatus.PENDING,
        provider_ref_id=f"ref_{uuid.uuid4().hex[:10]}",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "invoice_id": inv.id,
        "transaction_id": tx.id,
        "idempotency_key": idemp_key,
    }


# ==============================================================================
# INBOUND WEBHOOK TESTS
# ==============================================================================

def test_inbound_webhook_missing_signature(client: TestClient):
    """Inbound webhook without signature header must be rejected with 401."""
    body = json.dumps({"event_id": "evt_1", "status": "SUCCESS"}).encode("utf-8")
    resp = client.post(
        "/webhooks/upi-mock/inbound",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "MISSING_WEBHOOK_SIGNATURE"


def test_inbound_webhook_invalid_signature(client: TestClient):
    """Inbound webhook with tampered or incorrect signature must be rejected with 401."""
    body = json.dumps({"event_id": "evt_2", "status": "SUCCESS"}).encode("utf-8")
    resp = client.post(
        "/webhooks/upi-mock/inbound",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": "invalid_hex_digest_value",
        },
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "INVALID_WEBHOOK_SIGNATURE"


def test_inbound_webhook_valid_signature_updates_transaction(client: TestClient, db: Session, setup_webhook_env):
    """Valid inbound webhook resolves transaction, updates status to SUCCESS, and records history."""
    env = setup_webhook_env
    tx_id = env["transaction_id"]

    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    payload = {
        "event_id": event_id,
        "event_type": "payment.success",
        "transaction_id": str(tx_id),
        "status": "SUCCESS",
        "provider_ref_id": f"ref_{uuid.uuid4().hex[:10]}",
    }
    body = json.dumps(payload).encode("utf-8")
    sig = _calc_signature(settings.WEBHOOK_SECRET, body)

    resp = client.post(
        "/webhooks/upi-mock/inbound",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": sig,
        },
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["status"] == "processed"
    assert res_data["event_id"] == event_id
    assert res_data["transaction_id"] == str(tx_id)

    # Verify transaction status changed to SUCCESS
    db.expire_all()
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == tx_id).first()
    assert tx.status == TransactionStatus.SUCCESS

    # Verify status history recorded
    history = (
        db.query(TransactionStatusHistory)
        .filter(TransactionStatusHistory.transaction_id == tx_id)
        .order_by(TransactionStatusHistory.created_at.desc())
        .first()
    )
    assert history.to_status == TransactionStatus.SUCCESS
    assert "Inbound webhook update" in history.reason

    # Verify webhook_events_inbound record
    inbound_event = (
        db.query(WebhookEventInbound)
        .filter(WebhookEventInbound.provider_event_id == event_id)
        .first()
    )
    assert inbound_event is not None
    assert inbound_event.status == WebhookInboundStatus.PROCESSED
    assert inbound_event.payload["status"] == "SUCCESS"


def test_inbound_webhook_replay_prevention(client: TestClient, db: Session, setup_webhook_env):
    """Sending the same event_id twice must be ignored on second arrival without error."""
    env = setup_webhook_env
    tx_id = env["transaction_id"]

    event_id = f"evt_replay_{uuid.uuid4().hex[:10]}"
    payload = {
        "event_id": event_id,
        "event_type": "payment.success",
        "transaction_id": str(tx_id),
        "status": "SUCCESS",
    }
    body = json.dumps(payload).encode("utf-8")
    sig = _calc_signature(settings.WEBHOOK_SECRET, body)

    # First receipt
    resp1 = client.post(
        "/webhooks/upi-mock/inbound",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": sig,
        },
    )
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "processed"

    # Second receipt (replay)
    resp2 = client.post(
        "/webhooks/upi-mock/inbound",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": sig,
        },
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "ignored"
    assert "replay ignored" in resp2.json()["message"]


def test_inbound_webhook_redis_concurrency_lock(client: TestClient, fake_redis, setup_webhook_env):
    """If a duplicate delivery arrives while a lock is held, 409 Conflict is returned."""
    env = setup_webhook_env
    event_id = f"evt_lock_{uuid.uuid4().hex[:10]}"
    lock_key = f"payflow:lock:webhook:{event_id}"

    # Simulate that another process holds the Redis lock
    fake_redis.set(lock_key, "locked", ex=30)

    payload = {
        "event_id": event_id,
        "event_type": "payment.success",
        "transaction_id": str(env["transaction_id"]),
        "status": "SUCCESS",
    }
    body = json.dumps(payload).encode("utf-8")
    sig = _calc_signature(settings.WEBHOOK_SECRET, body)

    resp = client.post(
        "/webhooks/upi-mock/inbound",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": sig,
        },
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "CONCURRENT_WEBHOOK_DELIVERY"


# ==============================================================================
# OUTBOUND WEBHOOK TESTS
# ==============================================================================

def test_create_and_list_webhook_subscriptions(client: TestClient, setup_webhook_env):
    """Merchants can create and list webhook subscriptions."""
    env = setup_webhook_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    # 1. Create subscription
    create_resp = client.post(
        f"/api/v1/merchants/{m_id}/webhook-subscriptions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "target_url": "https://merchant.example.com/webhooks",
            "subscribed_events": ["payment.success", "payment.failed", "refund.*"],
        },
    )
    assert create_resp.status_code == 201
    sub_data = create_resp.json()
    assert sub_data["merchant_id"] == str(m_id)
    assert sub_data["target_url"] == "https://merchant.example.com/webhooks"
    assert "payment.success" in sub_data["subscribed_events"]
    assert len(sub_data["secret_key"]) > 0

    # 2. List subscriptions
    list_resp = client.get(
        f"/api/v1/merchants/{m_id}/webhook-subscriptions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    subs = list_resp.json()
    assert len(subs) >= 1
    assert any(s["id"] == sub_data["id"] for s in subs)


def test_send_synthetic_test_event(client: TestClient, db: Session, setup_webhook_env, monkeypatch):
    """POST /webhook-subscriptions/{id}/test dispatches a synthetic test ping."""
    env = setup_webhook_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    # Create subscription
    create_resp = client.post(
        f"/api/v1/merchants/{m_id}/webhook-subscriptions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "target_url": "https://merchant.example.com/payflow-webhook",
            "subscribed_events": ["*"],
        },
    )
    sub_id = create_resp.json()["id"]

    # Intercept httpx.Client.post to return 200 OK for outbound webhook URLs
    received_requests = []
    original_post = httpx.Client.post

    def mock_post(self, url, content=None, headers=None, **kwargs):
        url_str = str(url)
        if url_str.startswith("/") or "testserver" in url_str:
            return original_post(self, url, content=content, headers=headers, **kwargs)
        received_requests.append({"url": url_str, "content": content, "headers": headers})
        return httpx.Response(
            status_code=200,
            text='{"status": "ok"}',
            request=httpx.Request("POST", url_str),
        )

    monkeypatch.setattr(httpx.Client, "post", mock_post)

    # Trigger synthetic test event
    test_resp = client.post(
        f"/api/v1/webhook-subscriptions/{sub_id}/test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert test_resp.status_code == 200
    delivery_data = test_resp.json()
    assert delivery_data["subscription_id"] == sub_id
    assert delivery_data["event_type"] == "test.ping"

    # Verify HTTP request was sent and signed
    assert len(received_requests) >= 1
    sent_req = received_requests[0]
    assert sent_req["headers"]["X-PayFlow-Event"] == "test.ping"
    assert "X-PayFlow-Signature" in sent_req["headers"]

    # Verify delivery record in DB was updated to DELIVERED
    db.expire_all()
    delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == uuid.UUID(delivery_data["id"])).first()
    assert delivery.status == WebhookDeliveryStatus.DELIVERED
    assert delivery.response_status_code == 200


def test_outbound_webhook_retry_and_max_retries_fail(db: Session, setup_webhook_env, monkeypatch):
    """When target endpoint fails consecutively, delivery is retried and marked FAILED after max retries."""
    env = setup_webhook_env
    m_id = env["merchant_id"]

    sub = WebhookSubscription(
        merchant_id=m_id,
        target_url="https://merchant.failing.com/webhook",
        secret_key="secret123",
        subscribed_events=["payment.success"],
        is_active=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    delivery = WebhookDelivery(
        subscription_id=sub.id,
        event_type="payment.success",
        payload={"event": "payment.success", "amount": 1000},
        status=WebhookDeliveryStatus.PENDING,
        attempt_count=0,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    # Mock httpx.Client.post to always raise a network error or return 500
    class Mock500Response:
        status_code = 500
        text = "Internal Server Error"

    def mock_failing_post(self, url, **kwargs):
        return Mock500Response()

    monkeypatch.setattr(httpx.Client, "post", mock_failing_post)

    # Run delivery task directly simulating attempt 1
    # Note: deliver_webhook_outbound is a celery task
    try:
        deliver_webhook_outbound(str(delivery.id))
    except Exception:
        pass

    db.expire_all()
    delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery.id).first()
    assert delivery.attempt_count >= 1

    # Simulate attempt count reaching 3 (max retries)
    delivery.attempt_count = 2
    db.commit()

    try:
        deliver_webhook_outbound(str(delivery.id))
    except Exception:
        pass

    db.expire_all()
    delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery.id).first()
    assert delivery.attempt_count == 3
    assert delivery.status == WebhookDeliveryStatus.FAILED
    assert delivery.next_retry_at is None
    assert "500" in delivery.response_body


def test_outbound_webhook_dispatched_on_payment_success(client: TestClient, db: Session, setup_webhook_env, monkeypatch):
    """When a payment succeeds, outbound webhook is enqueued and dispatched with valid HMAC signature."""
    env = setup_webhook_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    secret = "merchant_signing_key_456"
    sub = WebhookSubscription(
        merchant_id=m_id,
        target_url="https://merchant.api.io/listen",
        secret_key=secret,
        subscribed_events=["payment.success", "refund.*"],
        is_active=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    received_dispatches = []
    original_post = httpx.Client.post

    def mock_post(self, url, content=None, headers=None, **kwargs):
        url_str = str(url)
        if url_str.startswith("/") or "testserver" in url_str:
            return original_post(self, url, content=content, headers=headers, **kwargs)
        received_dispatches.append({"url": url_str, "content": content, "headers": headers})
        return httpx.Response(
            status_code=200,
            text='{"acknowledged": true}',
            request=httpx.Request("POST", url_str),
        )

    monkeypatch.setattr(httpx.Client, "post", mock_post)

    # Initiate payment directly resulting in SUCCESS
    idemp_key = f"idemp_dispatch_{uuid.uuid4().hex}"
    client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idemp_key,
        },
        json={
            "merchant_id": str(m_id),
            "amount": 2500.0,
            "currency": "INR",
            "scenario": "SUCCESS",
        },
    )

    # Verify webhook dispatch occurred
    assert len(received_dispatches) >= 1
    sent = received_dispatches[-1]
    assert sent["url"] == "https://merchant.api.io/listen"
    assert sent["headers"]["X-PayFlow-Event"] == "payment.success"

    # Verify HMAC signature is correct
    signature = sent["headers"]["X-PayFlow-Signature"]
    expected_sig = hmac.new(
        secret.encode("utf-8"),
        sent["content"].encode("utf-8") if isinstance(sent["content"], str) else sent["content"],
        hashlib.sha256,
    ).hexdigest()
    assert signature == expected_sig


def test_wildcard_webhook_subscription_matching():
    """WebhookService._matches_event correctly matches wildcard patterns."""
    assert WebhookService._matches_event(["*"], "payment.success") is True
    assert WebhookService._matches_event(["payment.*"], "payment.success") is True
    assert WebhookService._matches_event(["payment.*"], "payment.failed") is True
    assert WebhookService._matches_event(["payment.*"], "refund.processed") is False
    assert WebhookService._matches_event(["refund.*"], "refund.initiated") is True
    assert WebhookService._matches_event(["payment.success"], "payment.success") is True
    assert WebhookService._matches_event(["payment.success"], "payment.failed") is False
