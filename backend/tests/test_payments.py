import uuid
from datetime import datetime, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.payments.service import PaymentService
from app.shared.exceptions import ConflictException


@pytest.fixture
def setup_payment_env(client: TestClient, db: Session):
    """Sets up an owner, merchant, customer, and invoice for payment ledger testing."""
    # 1. Register owner
    owner_email = f"payowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Ledger Test Owner",
            "phone": owner_phone,
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]
    owner_id = uuid.UUID(reg.json()["user"]["id"])

    # 2. Create merchant
    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Ledger Superstore",
            "legal_name": "Ledger Superstore Pvt Ltd",
            "email": f"ledger_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "superstore@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    # 3. Create customer
    c_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Ananya Sharma",
            "email": f"ananya_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9191{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(c_resp.json()["id"])

    # 4. Create invoice with total 1000.00
    inv = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-TEST-{uuid.uuid4().hex[:6].upper()}",
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

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "invoice_id": inv.id,
    }


def test_initiate_payment_requires_idempotency_key_header(client: TestClient, setup_payment_env):
    merchant_id = setup_payment_env["merchant_id"]
    token = setup_payment_env["owner_token"]

    # Missing Idempotency-Key header
    resp = client.post(
        "/api/v1/payments/initiate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": str(merchant_id),
            "amount": 500.00,
            "currency": "INR",
        },
    )
    assert resp.status_code == 422


def test_initiate_payment_idempotent_replay(client: TestClient, setup_payment_env):
    merchant_id = setup_payment_env["merchant_id"]
    token = setup_payment_env["owner_token"]
    idemp_key = f"idemp_test_{uuid.uuid4().hex}"

    payload = {
        "merchant_id": str(merchant_id),
        "amount": 500.00,
        "currency": "INR",
        "scenario": "SUCCESS",
    }

    # 1. First initiation: 201 Created
    resp1 = client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idemp_key,
        },
        json=payload,
    )
    assert resp1.status_code == 201, resp1.text
    data1 = resp1.json()
    tx_id_1 = data1["id"]
    assert data1["status"] == "SUCCESS"
    assert data1["idempotency_key"] == idemp_key

    # 2. Replay with identical Idempotency-Key: returns existing transaction (200 OK)
    resp2 = client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idemp_key,
        },
        json=payload,
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["id"] == tx_id_1
    assert data2["idempotency_key"] == idemp_key


def test_initiate_payment_state_transitions_history(
    client: TestClient, db: Session, setup_payment_env
):
    merchant_id = setup_payment_env["merchant_id"]
    token = setup_payment_env["owner_token"]
    idemp_key = f"idemp_history_{uuid.uuid4().hex}"

    resp = client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idemp_key,
        },
        json={
            "merchant_id": str(merchant_id),
            "amount": 250.00,
            "currency": "INR",
            "scenario": "FAILED",
        },
    )
    assert resp.status_code == 201
    tx_id = uuid.UUID(resp.json()["id"])

    # Verify status history rows in DB
    history = (
        db.query(TransactionStatusHistory)
        .filter(TransactionStatusHistory.transaction_id == tx_id)
        .order_by(TransactionStatusHistory.created_at.asc())
        .all()
    )
    # Expected transitions:
    # 1. None -> CREATED
    # 2. CREATED -> INITIATED
    # 3. INITIATED -> FAILED
    assert len(history) == 3
    assert history[0].from_status is None
    assert history[0].to_status == "CREATED"
    assert history[1].from_status == "CREATED"
    assert history[1].to_status == "INITIATED"
    assert history[2].from_status == "INITIATED"
    assert history[2].to_status == "FAILED"


def test_state_machine_invalid_transitions_rejected(db: Session, setup_payment_env):
    merchant_id = setup_payment_env["merchant_id"]

    # Create transaction in FAILED status
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        amount=Decimal("100.00"),
        currency="INR",
        status=TransactionStatus.FAILED,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"key_sm_{uuid.uuid4().hex}",
    )
    db.add(tx)
    db.commit()

    # Transition from FAILED -> SUCCESS is invalid and must be rejected with 409 Conflict
    with pytest.raises(ConflictException) as exc_info:
        PaymentService.transition_status(
            db=db,
            transaction_id=tx.id,
            to_status=TransactionStatus.SUCCESS,
        )
    assert exc_info.value.code == "INVALID_STATUS_TRANSITION"
    assert exc_info.value.status_code == 409


def test_state_machine_valid_refund_path(db: Session, setup_payment_env):
    merchant_id = setup_payment_env["merchant_id"]

    tx = PaymentTransaction(
        merchant_id=merchant_id,
        amount=Decimal("300.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"key_refund_{uuid.uuid4().hex}",
    )
    db.add(tx)
    db.commit()

    # 1. SUCCESS -> REFUND_INITIATED
    tx = PaymentService.transition_status(
        db=db,
        transaction_id=tx.id,
        to_status=TransactionStatus.REFUND_INITIATED,
    )
    assert tx.status == TransactionStatus.REFUND_INITIATED

    # 2. REFUND_INITIATED -> REFUND_PENDING
    tx = PaymentService.transition_status(
        db=db,
        transaction_id=tx.id,
        to_status=TransactionStatus.REFUND_PENDING,
    )
    assert tx.status == TransactionStatus.REFUND_PENDING

    # 3. REFUND_PENDING -> REFUNDED
    tx = PaymentService.transition_status(
        db=db,
        transaction_id=tx.id,
        to_status=TransactionStatus.REFUNDED,
    )
    assert tx.status == TransactionStatus.REFUNDED


def test_invoice_aggregate_status_derived_on_success(
    client: TestClient, db: Session, setup_payment_env
):
    merchant_id = setup_payment_env["merchant_id"]
    invoice_id = setup_payment_env["invoice_id"]
    token = setup_payment_env["owner_token"]

    # Initial invoice state: total 1000.00, paid 0.00, status SENT
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    assert inv.status == InvoiceStatus.SENT
    assert inv.paid_amount == Decimal("0.00")

    # Payment 1: 400.00 with SUCCESS -> Invoice becomes PARTIALLY_PAID
    resp1 = client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": f"idemp_part_{uuid.uuid4().hex}",
        },
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": str(invoice_id),
            "amount": 400.00,
            "currency": "INR",
            "scenario": "SUCCESS",
        },
    )
    assert resp1.status_code == 201

    db.refresh(inv)
    assert inv.paid_amount == Decimal("400.00")
    assert inv.status == InvoiceStatus.PARTIALLY_PAID

    # Payment 2: 600.00 with SUCCESS -> Invoice becomes PAID
    resp2 = client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": f"idemp_full_{uuid.uuid4().hex}",
        },
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": str(invoice_id),
            "amount": 600.00,
            "currency": "INR",
            "scenario": "SUCCESS",
        },
    )
    assert resp2.status_code == 201

    db.refresh(inv)
    assert inv.paid_amount == Decimal("1000.00")
    assert inv.status == InvoiceStatus.PAID


def test_get_payment_transaction_by_id(client: TestClient, setup_payment_env):
    merchant_id = setup_payment_env["merchant_id"]
    token = setup_payment_env["owner_token"]

    init_resp = client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": f"idemp_get_{uuid.uuid4().hex}",
        },
        json={
            "merchant_id": str(merchant_id),
            "amount": 150.00,
            "currency": "INR",
            "scenario": "SUCCESS",
        },
    )
    tx_id = init_resp.json()["id"]

    # Fetch transaction via GET /payments/{id}
    get_resp = client.get(
        f"/api/v1/payments/{tx_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == tx_id
    assert data["amount"] == "150.00"
    assert len(data["status_history"]) > 0


def test_list_merchant_transactions_filters_search_and_pagination(
    client: TestClient, setup_payment_env
):
    merchant_id = setup_payment_env["merchant_id"]
    customer_id = setup_payment_env["customer_id"]
    invoice_id = setup_payment_env["invoice_id"]
    token = setup_payment_env["owner_token"]

    # Create transaction with specific customer and invoice
    client.post(
        "/api/v1/payments/initiate",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": f"idemp_search_{uuid.uuid4().hex}",
        },
        json={
            "merchant_id": str(merchant_id),
            "customer_id": str(customer_id),
            "invoice_id": str(invoice_id),
            "amount": 777.00,
            "currency": "INR",
            "scenario": "SUCCESS",
        },
    )

    # 1. Filter by status=SUCCESS
    resp_status = client.get(
        f"/api/v1/merchants/{merchant_id}/transactions?status=SUCCESS",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_status.status_code == 200
    assert resp_status.json()["total"] >= 1

    # 2. Search by customer name ("Ananya")
    resp_search_customer = client.get(
        f"/api/v1/merchants/{merchant_id}/transactions?search=Ananya",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_search_customer.status_code == 200
    items = resp_search_customer.json()["items"]
    assert any(Decimal(str(item["amount"])) == Decimal("777.00") for item in items)

    # 3. RBAC check: Unauthorized access without token
    unauth_resp = client.get(f"/api/v1/merchants/{merchant_id}/transactions")
    assert unauth_resp.status_code == 401
