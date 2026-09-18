import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.duplicate_detection.models import DuplicateTransactionFlag
from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.mock_upi_provider.service import MockUPIProvider
from app.modules.mock_upi_provider.tasks import resolve_simulated_payment_async
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
)
from app.modules.webhooks.models import WebhookEventInbound


@pytest.fixture
def merchant_and_transaction(client: TestClient, db: Session):
    """Provisions owner, merchant, and an active payment transaction."""
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Simulator Test Owner",
            "phone": owner_phone,
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]

    merchant_email = f"merchant_{uuid.uuid4().hex[:8]}@test.com"
    merchant_phone = f"+9197{uuid.uuid4().int % 100000000:08d}"
    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Nova Gadgets",
            "legal_name": "Nova Gadgets India Pvt Ltd",
            "email": merchant_email,
            "phone": merchant_phone,
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5732",
            "initial_upi_vpa": "novagadgets@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    # Seed an active transaction
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        amount=Decimal("500.00"),
        currency="INR",
        status=TransactionStatus.INITIATED,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"idemp_{uuid.uuid4().hex}",
        payer_vpa="customer@okaxis",
        payee_vpa="novagadgets@icici",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return {
        "owner_token": owner_token,
        "merchant_id": merchant_id,
        "transaction_id": tx.id,
        "idempotency_key": tx.idempotency_key,
    }


def test_scenario_success(db: Session):
    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("450.00"),
        vpa="payer@okaxis",
        idempotency_key="key-success-1",
        scenario=MockScenario.SUCCESS,
    )
    assert res.scenario == MockScenario.SUCCESS
    assert res.status == TransactionStatus.SUCCESS
    assert res.settled_amount == Decimal("450.00")
    assert res.provider_ref_id.startswith("MOCK-UPI-")
    assert res.failure_reason is None
    assert res.is_async is False


def test_scenario_failed(db: Session):
    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("200.00"),
        vpa="payer@okaxis",
        idempotency_key="key-failed-1",
        scenario=MockScenario.FAILED,
    )
    assert res.scenario == MockScenario.FAILED
    assert res.status == TransactionStatus.FAILED
    assert res.settled_amount == Decimal("0.00")
    assert res.failure_reason is not None
    assert "PSP_DECLINED" in res.failure_reason
    assert res.is_async is False


def test_scenario_pending_and_async_resolution(
    db: Session, merchant_and_transaction
):
    tx_id = merchant_and_transaction["transaction_id"]
    m_id = merchant_and_transaction["merchant_id"]
    idemp = merchant_and_transaction["idempotency_key"]

    # 1. Initiate with PENDING
    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("500.00"),
        vpa="customer@okaxis",
        idempotency_key=idemp,
        scenario=MockScenario.PENDING,
        transaction_id=tx_id,
        merchant_id=m_id,
    )
    assert res.scenario == MockScenario.PENDING
    assert res.status == TransactionStatus.PENDING
    assert res.is_async is True

    # 2. Synchronously resolve async settlement
    updated_tx = MockUPIProvider.resolve_async_settlement(
        db=db,
        transaction_id=tx_id,
        target_status=TransactionStatus.SUCCESS,
    )
    assert updated_tx.status == TransactionStatus.SUCCESS
    assert updated_tx.completed_at is not None

    # Verify inbound webhook was recorded
    webhook = (
        db.query(WebhookEventInbound)
        .filter(
            WebhookEventInbound.provider == "MOCK_UPI_PROVIDER",
            WebhookEventInbound.event_type == "payment.success",
        )
        .order_by(WebhookEventInbound.created_at.desc())
        .first()
    )
    assert webhook is not None
    assert webhook.payload["transaction_id"] == str(tx_id)
    assert webhook.payload["status"] == "SUCCESS"

    # 3. Test Celery task execution via .apply()
    celery_res = resolve_simulated_payment_async.apply(
        args=[str(tx_id), TransactionStatus.SUCCESS.value]
    )
    assert celery_res.result["status"] == "resolved"


def test_scenario_timeout_and_async_resolution(
    db: Session, merchant_and_transaction
):
    tx_id = merchant_and_transaction["transaction_id"]
    m_id = merchant_and_transaction["merchant_id"]
    idemp = merchant_and_transaction["idempotency_key"]

    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("500.00"),
        vpa="customer@okaxis",
        idempotency_key=idemp,
        scenario=MockScenario.TIMEOUT,
        transaction_id=tx_id,
        merchant_id=m_id,
    )
    assert res.scenario == MockScenario.TIMEOUT
    assert res.status == TransactionStatus.TIMEOUT
    assert res.is_async is True

    # Resolve timeout to FAILED
    updated_tx = MockUPIProvider.resolve_async_settlement(
        db=db,
        transaction_id=tx_id,
        target_status=TransactionStatus.FAILED,
        reason="Gateway Timeout during provider settlement",
    )
    assert updated_tx.status == TransactionStatus.FAILED
    assert updated_tx.failure_reason is not None

    # Verify inbound webhook for failure
    webhook = (
        db.query(WebhookEventInbound)
        .filter(
            WebhookEventInbound.provider == "MOCK_UPI_PROVIDER",
            WebhookEventInbound.event_type == "payment.failed",
        )
        .order_by(WebhookEventInbound.created_at.desc())
        .first()
    )
    assert webhook is not None
    assert webhook.payload["status"] == "FAILED"


def test_scenario_duplicate(db: Session, merchant_and_transaction):
    tx1_id = merchant_and_transaction["transaction_id"]
    m_id = merchant_and_transaction["merchant_id"]
    idemp = merchant_and_transaction["idempotency_key"]

    # Create second transaction to simulate replay
    tx2 = PaymentTransaction(
        merchant_id=m_id,
        amount=Decimal("500.00"),
        currency="INR",
        status=TransactionStatus.INITIATED,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"idemp_replay_{uuid.uuid4().hex}",
        payer_vpa="customer@okaxis",
    )
    db.add(tx2)
    db.commit()

    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("500.00"),
        vpa="customer@okaxis",
        idempotency_key=idemp,  # replay same key
        scenario=MockScenario.DUPLICATE,
        transaction_id=tx2.id,
        merchant_id=m_id,
    )
    assert res.scenario == MockScenario.DUPLICATE
    assert res.duplicate_of_transaction_id is not None
    assert "DUPLICATE_PAYMENT_DETECTED" in res.failure_reason

    # Verify DuplicateTransactionFlag entry created in DB
    flag = (
        db.query(DuplicateTransactionFlag)
        .filter(DuplicateTransactionFlag.duplicate_transaction_id == tx2.id)
        .first()
    )
    assert flag is not None
    assert flag.merchant_id == m_id
    assert flag.original_transaction_id == tx1_id


def test_scenario_partial_payment(db: Session):
    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("1000.00"),
        vpa="payer@oksbi",
        idempotency_key="key-partial-1",
        scenario=MockScenario.PARTIAL_PAYMENT,
    )
    assert res.scenario == MockScenario.PARTIAL_PAYMENT
    assert res.status == TransactionStatus.SUCCESS
    assert res.settled_amount == Decimal("500.00")
    assert res.settled_amount < res.amount


def test_scenario_refund(db: Session):
    res = MockUPIProvider.initiate_payment(
        db=db,
        amount=Decimal("350.00"),
        vpa="payer@oksbi",
        idempotency_key="key-refund-1",
        scenario=MockScenario.REFUND,
    )
    assert res.scenario == MockScenario.REFUND
    assert res.status == TransactionStatus.REFUNDED
    assert res.settled_amount == Decimal("350.00")
    assert res.provider_ref_id.startswith("MOCK-REFUND-")


def test_weighted_distribution_bias_toward_success():
    """Validates that unforced scenario selection yields ~80% SUCCESS over large sample."""
    sample_size = 500
    counts = {s: 0 for s in MockScenario}

    for _ in range(sample_size):
        chosen = MockUPIProvider.select_scenario(override=None)
        counts[chosen] += 1

    success_ratio = counts[MockScenario.SUCCESS] / sample_size
    # Expect 80% ± 8% (between 72% and 88%)
    assert 0.70 <= success_ratio <= 0.90, f"Success ratio was {success_ratio:.2f}, expected ~0.80"


def test_simulate_dev_endpoint(client: TestClient, merchant_and_transaction):
    token = merchant_and_transaction["owner_token"]
    tx_id = merchant_and_transaction["transaction_id"]

    # 1. Simulate SUCCESS
    resp_success = client.post(
        f"/api/v1/payments/{tx_id}/simulate",
        headers={"Authorization": f"Bearer {token}"},
        json={"scenario": "SUCCESS"},
    )
    assert resp_success.status_code == 200, resp_success.text
    assert resp_success.json()["status"] == "SUCCESS"
    assert resp_success.json()["scenario"] == "SUCCESS"

    # 2. Simulate FAILED
    resp_fail = client.post(
        f"/api/v1/payments/{tx_id}/simulate",
        headers={"Authorization": f"Bearer {token}"},
        json={"scenario": "FAILED"},
    )
    assert resp_fail.status_code == 200
    assert resp_fail.json()["status"] == "FAILED"
    assert "PSP_DECLINED" in resp_fail.json()["failure_reason"]

    # 3. Direct initiate simulation
    direct_resp = client.post(
        "/api/v1/mock-upi/initiate",
        json={
            "amount": 299.00,
            "vpa": "direct@mockupi",
            "idempotency_key": f"key_{uuid.uuid4().hex}",
            "scenario": "PARTIAL_PAYMENT",
        },
    )
    assert direct_resp.status_code == 200
    assert direct_resp.json()["settled_amount"] == "149.50"
