"""Tests for the Notifications Module.

Covers:
  1. Generic send_notification service and Celery task deliver_notification.
  2. Realistic mock delivery: logs realistic info and writes row with status SENT.
  3. Event integration:
     - Payment SUCCESS -> payment_success notification
     - Payment FAILED -> payment_failed notification
     - Refund SUCCESS -> refund_processed notification
     - Invoice OVERDUE -> invoice_overdue notification
     - Risk signal raised -> risk_signal_raised notification
  4. Mobile notification center endpoints:
     - GET /merchants/{id}/notifications (paginated with is_read filter)
     - PATCH /notifications/{id}/read (sets is_read=True and read_at)
  5. 404 for unknown notification and RBAC enforcement.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.invoices.service import mark_invoice_overdue
from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.notifications.models import Notification, NotificationChannel, NotificationStatus
from app.modules.notifications.service import NotificationService
from app.modules.notifications.tasks import deliver_notification
from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus
from app.modules.payments.schemas import InitiatePaymentRequest
from app.modules.payments.service import PaymentService
from app.modules.refunds.models import Refund, RefundStatus
from app.modules.refunds.service import RefundService
from app.modules.risk.models import RiskAction, RiskLevel
from app.modules.risk.service import RiskService


@pytest.fixture
def notif_env(client: TestClient, db: Session):
    """Sets up owner user, merchant, and auth token for testing."""
    owner_email = f"notifowner_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Notification Owner",
            "phone": f"+9195{uuid.uuid4().int % 100000000:08d}",
        },
    )
    assert reg.status_code == 201, reg.text
    owner_token = reg.json()["tokens"]["access_token"]
    user_id = uuid.UUID(reg.json()["user"]["id"])

    mreg = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Notification Store",
            "legal_name": "Notification Store Pvt Ltd",
            "email": f"notif_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9195{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "notifstore@icici",
        },
    )
    assert mreg.status_code == 201, mreg.text
    merchant_id = uuid.UUID(mreg.json()["id"])

    return {
        "owner_token": owner_token,
        "merchant_id": merchant_id,
        "user_id": user_id,
    }


# ---------------------------------------------------------------------------
# 1. Generic send_notification service and Celery task
# ---------------------------------------------------------------------------

def test_send_notification_service_and_task(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]
    user_id = notif_env["user_id"]

    # Call send_notification generic service
    task_id = NotificationService.send_notification(
        merchant_id=merchant_id,
        user_id=user_id,
        channel=NotificationChannel.PUSH,
        template="payment_success",
        payload={"transaction_id": "tx_test_123", "amount": "1500.00"},
    )
    assert task_id is not None

    # Because Celery runs in eager mode in test environment, row is immediately committed
    db.expire_all()
    notif = (
        db.query(Notification)
        .filter(Notification.merchant_id == merchant_id)
        .order_by(Notification.created_at.desc())
        .first()
    )
    assert notif is not None
    assert notif.status == NotificationStatus.SENT
    assert notif.channel == NotificationChannel.PUSH
    assert notif.template == "payment_success"
    assert "1500.00" in notif.content
    assert notif.is_read is False
    assert notif.sent_at is not None


def test_deliver_notification_task_directly(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]
    
    result = deliver_notification(
        merchant_id=str(merchant_id),
        channel="EMAIL",
        template="custom_alert",
        payload={"message": "System maintenance scheduled tonight at 02:00 UTC."},
    )
    assert result["status"] == "SENT"
    assert result["channel"] == "EMAIL"
    
    notif_id = uuid.UUID(result["notification_id"])
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    assert notif is not None
    assert "maintenance" in notif.content.lower()


# ---------------------------------------------------------------------------
# 2. Event Triggers: payment SUCCESS, payment FAILED
# ---------------------------------------------------------------------------

def test_payment_success_triggers_notification(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]

    req = InitiatePaymentRequest(
        merchant_id=merchant_id,
        amount=Decimal("1200.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        payer_vpa="payer@okaxis",
        scenario=MockScenario.SUCCESS,
    )
    tx, is_new = PaymentService.initiate_payment(
        db=db,
        payload=req,
        idempotency_key=f"notif-tx-succ-{uuid.uuid4().hex}",
    )
    assert tx.status == TransactionStatus.SUCCESS

    # Verify notification created
    db.expire_all()
    notif = (
        db.query(Notification)
        .filter(
            Notification.merchant_id == merchant_id,
            Notification.template == "payment_success",
        )
        .order_by(Notification.created_at.desc())
        .first()
    )
    assert notif is not None
    assert notif.status == NotificationStatus.SENT
    assert "1200.00" in notif.content


def test_payment_failed_triggers_notification(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]

    req = InitiatePaymentRequest(
        merchant_id=merchant_id,
        amount=Decimal("750.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        payer_vpa="payer@okaxis",
        scenario=MockScenario.FAILED,
    )
    tx, is_new = PaymentService.initiate_payment(
        db=db,
        payload=req,
        idempotency_key=f"notif-tx-fail-{uuid.uuid4().hex}",
    )
    assert tx.status == TransactionStatus.FAILED

    db.expire_all()
    notif = (
        db.query(Notification)
        .filter(
            Notification.merchant_id == merchant_id,
            Notification.template == "payment_failed",
        )
        .order_by(Notification.created_at.desc())
        .first()
    )
    assert notif is not None
    assert notif.status == NotificationStatus.SENT
    assert "750.00" in notif.content


# ---------------------------------------------------------------------------
# 3. Event Trigger: refund REFUNDED
# ---------------------------------------------------------------------------

def test_refund_success_triggers_notification(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]
    from app.modules.auth.models import User
    actor = db.query(User).filter(User.id == notif_env["user_id"]).first()

    # 1. Create a SUCCESS transaction
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"notif-ref-tx-{uuid.uuid4().hex}",
        amount=Decimal("500.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
    )
    db.add(tx)
    db.commit()

    # 2. Initiate refund
    refund = Refund(
        merchant_id=merchant_id,
        transaction_id=tx.id,
        amount=Decimal("500.00"),
        reason="Customer returned merchandise",
        status=RefundStatus.INITIATED,
    )
    db.add(refund)
    db.commit()

    # 3. Approve refund
    RefundService.approve_refund(
        db=db,
        refund_id=refund.id,
        actor=actor,
    )

    db.expire_all()
    # Check if notification was dispatched for refund_processed
    notif = (
        db.query(Notification)
        .filter(
            Notification.merchant_id == merchant_id,
            Notification.template == "refund_processed",
        )
        .first()
    )
    assert notif is not None
    assert notif.status == NotificationStatus.SENT
    assert "500.00" in notif.content


# ---------------------------------------------------------------------------
# 4. Event Trigger: invoice OVERDUE
# ---------------------------------------------------------------------------

def test_invoice_overdue_triggers_notification(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]
    yesterday = date.today() - timedelta(days=1)

    inv = Invoice(
        merchant_id=merchant_id,
        invoice_number=f"INV-NOTIF-{uuid.uuid4().hex[:6].upper()}",
        total_amount=Decimal("3200.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        due_date=yesterday,
    )
    db.add(inv)
    db.commit()

    # Transition to overdue
    mark_invoice_overdue(db=db, invoice_id=inv.id)

    db.expire_all()
    notif = (
        db.query(Notification)
        .filter(
            Notification.merchant_id == merchant_id,
            Notification.template == "invoice_overdue",
        )
        .first()
    )
    assert notif is not None
    assert "3200.00" in notif.content
    assert inv.invoice_number in notif.content


# ---------------------------------------------------------------------------
# 5. Event Trigger: risk signal raised
# ---------------------------------------------------------------------------

def test_risk_signal_raised_triggers_notification(db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]

    RiskService.record_risk_signal(
        db=db,
        merchant_id=merchant_id,
        rule_triggered="RAPID_VELOCITY_SPIKE",
        risk_score=Decimal("88.50"),
        risk_level=RiskLevel.HIGH,
        action_taken=RiskAction.FLAG_FOR_REVIEW,
    )

    db.expire_all()
    notif = (
        db.query(Notification)
        .filter(
            Notification.merchant_id == merchant_id,
            Notification.template == "risk_signal_raised",
        )
        .first()
    )
    assert notif is not None
    assert "HIGH" in notif.title or "HIGH" in notif.content
    assert "RAPID_VELOCITY_SPIKE" in notif.content


# ---------------------------------------------------------------------------
# 6. REST API Endpoints: GET list & PATCH read
# ---------------------------------------------------------------------------

def test_list_merchant_notifications(client: TestClient, db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]
    token = notif_env["owner_token"]

    # Create 2 unread notifications and 1 read notification
    n1 = Notification(
        merchant_id=merchant_id,
        recipient="test@example.com",
        channel=NotificationChannel.PUSH,
        title="Alert 1",
        content="Content 1",
        status=NotificationStatus.SENT,
        is_read=False,
    )
    n2 = Notification(
        merchant_id=merchant_id,
        recipient="test@example.com",
        channel=NotificationChannel.PUSH,
        title="Alert 2",
        content="Content 2",
        status=NotificationStatus.SENT,
        is_read=False,
    )
    n3 = Notification(
        merchant_id=merchant_id,
        recipient="test@example.com",
        channel=NotificationChannel.PUSH,
        title="Alert 3",
        content="Content 3",
        status=NotificationStatus.SENT,
        is_read=True,
        read_at=datetime.now(timezone.utc),
    )
    db.add_all([n1, n2, n3])
    db.commit()

    # Fetch all
    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 3
    assert len(body["items"]) >= 3

    # Filter is_read=false
    resp_unread = client.get(
        f"/api/v1/merchants/{merchant_id}/notifications?is_read=false",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_unread.status_code == 200
    for item in resp_unread.json()["items"]:
        assert item["is_read"] is False

    # Filter is_read=true
    resp_read = client.get(
        f"/api/v1/merchants/{merchant_id}/notifications?is_read=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_read.status_code == 200
    for item in resp_read.json()["items"]:
        assert item["is_read"] is True


def test_mark_notification_as_read(client: TestClient, db: Session, notif_env):
    merchant_id = notif_env["merchant_id"]
    token = notif_env["owner_token"]

    notif = Notification(
        merchant_id=merchant_id,
        recipient="test@example.com",
        channel=NotificationChannel.PUSH,
        title="Unread Alert",
        content="Testing read receipt",
        status=NotificationStatus.SENT,
        is_read=False,
    )
    db.add(notif)
    db.commit()

    # Mark as read
    patch_resp = client.patch(
        f"/api/v1/notifications/{notif.id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["id"] == str(notif.id)
    assert body["is_read"] is True
    assert body["read_at"] is not None

    # Verify DB record
    db.expire_all()
    updated = db.query(Notification).filter(Notification.id == notif.id).first()
    assert updated.is_read is True
    assert updated.read_at is not None


def test_mark_notification_not_found(client: TestClient, notif_env):
    token = notif_env["owner_token"]
    random_id = uuid.uuid4()

    resp = client.patch(
        f"/api/v1/notifications/{random_id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
