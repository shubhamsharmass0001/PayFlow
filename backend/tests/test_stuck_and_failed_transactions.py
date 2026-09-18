"""Tests for handling FAILED, PENDING, and TIMEOUT transactions:
- Celery polling of stuck transactions past threshold & max wait escalation to FAILED with 'provider_timeout'.
- Provider re-query resolution.
- Operational notification alerts on FAILED/TIMEOUT.
- Convenience filter GET /merchants/{id}/transactions?status=pending&stuck=true.
- Regenerating a new payment_request for a FAILED transaction without mutating historical record.
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.notifications.models import Notification, NotificationChannel, NotificationStatus
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.payments.tasks import poll_stuck_transactions


@pytest.fixture
def setup_stuck_env(client: TestClient, db: Session):
    """Sets up an owner, merchant, customer, and invoice for stuck transaction testing."""
    owner_email = f"stuckowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Stuck Tx Test Owner",
            "phone": owner_phone,
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]
    owner_id = uuid.UUID(reg.json()["user"]["id"])

    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Stuck Recovery Electronics",
            "legal_name": "Stuck Recovery Electronics Pvt Ltd",
            "email": f"stuck_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "stuckrecovery@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    c_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Devendra Kumar",
            "email": f"devendra_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9191{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(c_resp.json()["id"])

    inv = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-STUCK-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("3000.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("3000.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        allow_partial_payment=True,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "invoice_id": inv.id,
    }


def test_poll_stuck_transactions_escalates_to_failed_past_max_wait(db: Session, setup_stuck_env):
    """Transactions stuck in PENDING past max wait are escalated to FAILED with reason 'provider_timeout'."""
    merchant_id = setup_stuck_env["merchant_id"]
    invoice_id = setup_stuck_env["invoice_id"]
    customer_id = setup_stuck_env["customer_id"]

    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice_id,
        customer_id=customer_id,
        amount=Decimal("500.00"),
        currency="INR",
        status=TransactionStatus.PENDING,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"stuck-maxwait-{uuid.uuid4().hex}",
        created_at=past_time,
        updated_at=past_time,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # Run the polling task with threshold=60s, max_wait=300s (5m)
    result = poll_stuck_transactions(stuck_threshold_seconds=60, max_wait_seconds=300)
    assert result["status"] == "success"
    assert result["failed_count"] >= 1

    db.refresh(tx)
    assert tx.status == TransactionStatus.FAILED
    assert tx.failure_reason == "provider_timeout"

    # Verify status history recorded provider_timeout
    history = (
        db.query(TransactionStatusHistory)
        .filter(TransactionStatusHistory.transaction_id == tx.id)
        .order_by(TransactionStatusHistory.created_at.desc())
        .first()
    )
    assert history is not None
    assert history.to_status == "FAILED"
    assert "provider_timeout" in history.reason

    # Verify merchant alert notification was generated
    notif = (
        db.query(Notification)
        .filter(
            Notification.merchant_id == merchant_id,
            Notification.title.contains("Timed Out"),
        )
        .first()
    )
    assert notif is not None
    assert "provider_timeout" in notif.content


def test_poll_stuck_transactions_resolves_via_mock_provider(db: Session, setup_stuck_env):
    """Transactions stuck past threshold but within max wait re-query MockUPIProvider and resolve."""
    merchant_id = setup_stuck_env["merchant_id"]
    invoice_id = setup_stuck_env["invoice_id"]
    customer_id = setup_stuck_env["customer_id"]

    # 3 minutes old (stuck past 60s, but within 300s max wait)
    past_time = datetime.now(timezone.utc) - timedelta(minutes=3)
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice_id,
        customer_id=customer_id,
        amount=Decimal("250.00"),
        currency="INR",
        status=TransactionStatus.PENDING,
        mock_scenario="PENDING",
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"stuck-resolve-{uuid.uuid4().hex}",
        created_at=past_time,
        updated_at=past_time,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    result = poll_stuck_transactions(stuck_threshold_seconds=60, max_wait_seconds=300)
    assert result["status"] == "success"

    db.refresh(tx)
    assert tx.status == TransactionStatus.SUCCESS


def test_get_merchants_transactions_stuck_filter(client: TestClient, db: Session, setup_stuck_env):
    """GET /merchants/{id}/transactions?status=pending&stuck=true returns stuck transactions only."""
    headers = {"Authorization": f"Bearer {setup_stuck_env['owner_token']}"}
    merchant_id = setup_stuck_env["merchant_id"]
    invoice_id = setup_stuck_env["invoice_id"]
    customer_id = setup_stuck_env["customer_id"]

    # 1. Stuck transaction (created 5 minutes ago)
    stuck_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    tx_stuck = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice_id,
        customer_id=customer_id,
        amount=Decimal("111.00"),
        currency="INR",
        status=TransactionStatus.PENDING,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"stuck-query-old-{uuid.uuid4().hex}",
        created_at=stuck_time,
        updated_at=stuck_time,
    )

    # 2. Fresh pending transaction (created right now)
    tx_fresh = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice_id,
        customer_id=customer_id,
        amount=Decimal("222.00"),
        currency="INR",
        status=TransactionStatus.PENDING,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"stuck-query-new-{uuid.uuid4().hex}",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add_all([tx_stuck, tx_fresh])
    db.commit()
    db.refresh(tx_stuck)
    db.refresh(tx_fresh)

    # Query with status=pending&stuck=true
    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/transactions?status=pending&stuck=true",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    item_ids = [item["id"] for item in items]

    assert str(tx_stuck.id) in item_ids
    assert str(tx_fresh.id) not in item_ids


def test_regenerate_payment_request_for_failed_transaction(client: TestClient, db: Session, setup_stuck_env):
    """On FAILED, merchant can regenerate a new payment_request for the same invoice without mutating failed tx."""
    headers = {"Authorization": f"Bearer {setup_stuck_env['owner_token']}"}
    merchant_id = setup_stuck_env["merchant_id"]
    invoice_id = setup_stuck_env["invoice_id"]
    customer_id = setup_stuck_env["customer_id"]

    # Create a failed transaction
    failed_tx = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice_id,
        customer_id=customer_id,
        amount=Decimal("450.00"),
        currency="INR",
        status=TransactionStatus.FAILED,
        failure_reason="provider_timeout",
        payment_method=PaymentMethod.UPI_INTENT,
        payer_vpa="buyer@okhdfcbank",
        idempotency_key=f"fail-regen-{uuid.uuid4().hex}",
    )
    db.add(failed_tx)
    db.commit()
    db.refresh(failed_tx)

    # Regenerate request via POST /payments/{id}/regenerate-request
    regen_resp = client.post(
        f"/api/v1/payments/{failed_tx.id}/regenerate-request",
        headers=headers,
    )
    assert regen_resp.status_code == 201, regen_resp.text
    regen_data = regen_resp.json()

    assert regen_data["invoice_id"] == str(invoice_id)
    assert Decimal(regen_data["amount"]) == Decimal("450.00")
    assert regen_data["payer_vpa"] == "buyer@okhdfcbank"
    assert regen_data["status"] == "PENDING"

    # Ensure the failed transaction is untouched
    db.refresh(failed_tx)
    assert failed_tx.status == TransactionStatus.FAILED
    assert failed_tx.failure_reason == "provider_timeout"


def test_regenerate_payment_request_rejects_non_failed_transaction(client: TestClient, db: Session, setup_stuck_env):
    """Regenerating a payment request for a SUCCESS transaction is rejected with 400 Bad Request."""
    headers = {"Authorization": f"Bearer {setup_stuck_env['owner_token']}"}
    merchant_id = setup_stuck_env["merchant_id"]
    invoice_id = setup_stuck_env["invoice_id"]

    success_tx = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice_id,
        amount=Decimal("300.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"success-regen-{uuid.uuid4().hex}",
    )
    db.add(success_tx)
    db.commit()
    db.refresh(success_tx)

    resp = client.post(
        f"/api/v1/payments/{success_tx.id}/regenerate-request",
        headers=headers,
    )
    assert resp.status_code == 400
    assert "INVALID_TRANSACTION_STATUS" in resp.json()["code"]
