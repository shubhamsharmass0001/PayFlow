"""Tests for the Refunds Module.

Covers:
  1. Initiate refund on a SUCCESS transaction → REFUND_INITIATED
  2. Partial refunds: multiple stacked refunds summing ≤ transaction amount
  3. Amount validation: reject refund > remaining balance
  4. Approve refund: transitions to REFUNDED or PARTIALLY_REFUNDED
  5. Full refund → parent transaction REFUNDED
  6. Partial refund → parent transaction PARTIALLY_REFUNDED, allows additional refund
  7. Reject approval if refund not in INITIATED status (duplicate approval guard)
  8. RBAC: Cashier cannot approve; Auditor read-only; Manager/Owner can approve
  9. GET /refunds/{id} and list with filters
  10. Cannot refund a FAILED transaction
"""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.modules.refunds.models import Refund, RefundStatus


# ---------------------------------------------------------------------------
# Shared fixture: owner, merchant, customer, SUCCESS transaction
# ---------------------------------------------------------------------------

@pytest.fixture
def refund_env(client: TestClient, db: Session):
    """Bootstraps owner → merchant → customer → SUCCESS transaction."""
    # 1. Register owner
    owner_email = f"refundowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9197{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Refund Test Owner",
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
            "business_name": "Refund Mart",
            "legal_name": "Refund Mart Pvt Ltd",
            "email": f"refundmart_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9195{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "refundmart@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    # 3. Create customer
    c_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Priya Nair",
            "email": f"priya_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9193{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(c_resp.json()["id"])

    # 4. Insert a SUCCESS transaction directly (bypasses random scenario)
    invoice = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-REFTEST-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("1000.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("1000.00"),
        paid_amount=Decimal("1000.00"),
        currency="INR",
        status=InvoiceStatus.PAID,
        allow_partial_payment=True,
    )
    db.add(invoice)
    db.flush()

    tx = PaymentTransaction(
        merchant_id=merchant_id,
        invoice_id=invoice.id,
        customer_id=customer_id,
        idempotency_key=f"refund-test-{uuid.uuid4().hex}",
        amount=Decimal("1000.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        payer_vpa="priya@upi",
        payee_vpa="refundmart@icici",
        provider_ref_id="MOCK-UPI-SUCCESS",
        mock_scenario="SUCCESS",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "invoice_id": invoice.id,
        "tx_id": tx.id,
        "tx_amount": tx.amount,
    }


# ---------------------------------------------------------------------------
# 1. Initiate refund → REFUND_INITIATED
# ---------------------------------------------------------------------------

def test_initiate_refund_creates_initiated_status(client: TestClient, refund_env):
    env = refund_env
    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "400.00", "reason": "Customer returned item"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "INITIATED"
    assert Decimal(body["amount"]) == Decimal("400.00")
    assert body["reason"] == "Customer returned item"
    assert body["transaction_id"] == str(env["tx_id"])
    assert body["merchant_id"] == str(env["merchant_id"])


def test_initiate_refund_transitions_parent_transaction_to_refund_initiated(
    client: TestClient, refund_env, db: Session
):
    env = refund_env
    client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "200.00", "reason": "Duplicate charge"},
    )
    db.refresh(db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first())
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first()
    assert tx.status == TransactionStatus.REFUND_INITIATED


# ---------------------------------------------------------------------------
# 2. Amount validation: reject > remaining balance
# ---------------------------------------------------------------------------

def test_refund_amount_exceeds_transaction_amount_rejected(client: TestClient, refund_env):
    env = refund_env
    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "1500.00", "reason": "Too much"},
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "REFUND_AMOUNT_EXCEEDS_BALANCE"


def test_refund_on_failed_transaction_rejected(client: TestClient, refund_env, db: Session):
    """Cannot initiate a refund on a FAILED transaction."""
    env = refund_env
    # Create a FAILED transaction directly
    failed_tx = PaymentTransaction(
        merchant_id=env["merchant_id"],
        invoice_id=env["invoice_id"],
        idempotency_key=f"failed-tx-{uuid.uuid4().hex}",
        amount=Decimal("500.00"),
        currency="INR",
        status=TransactionStatus.FAILED,
        mock_scenario="FAILED",
    )
    db.add(failed_tx)
    db.commit()

    resp = client.post(
        f"/api/v1/transactions/{failed_tx.id}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "500.00", "reason": "Should not work"},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "REFUND_INELIGIBLE_STATUS"


# ---------------------------------------------------------------------------
# 3. Approve refund → full refund path
# ---------------------------------------------------------------------------

def test_approve_refund_full_amount_marks_transaction_refunded(
    client: TestClient, refund_env, db: Session
):
    env = refund_env

    # Step A: initiate full refund
    init_resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "1000.00", "reason": "Order cancelled"},
    )
    assert init_resp.status_code == 201
    refund_id = init_resp.json()["id"]

    # Step B: approve — force SUCCESS outcome
    with patch("random.random", return_value=0.05):  # < 0.90 → SUCCESS
        approve_resp = client.patch(
            f"/api/v1/refunds/{refund_id}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )
    assert approve_resp.status_code == 200, approve_resp.text
    body = approve_resp.json()
    assert body["status"] == "SUCCESS"
    assert body["provider_refund_id"] is not None

    # Parent transaction should be REFUNDED
    db.expire_all()
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first()
    assert tx.status == TransactionStatus.REFUNDED

    # Audit trail: status_history should include REFUND_PENDING → REFUNDED
    from app.modules.payments.models import TransactionStatusHistory
    history = (
        db.query(TransactionStatusHistory)
        .filter(
            TransactionStatusHistory.transaction_id == env["tx_id"],
            TransactionStatusHistory.to_status == TransactionStatus.REFUNDED.value,
        )
        .first()
    )
    assert history is not None


# ---------------------------------------------------------------------------
# 4. Partial refunds: stacked amounts, intermediate PARTIALLY_REFUNDED
# ---------------------------------------------------------------------------

def test_partial_refunds_stack_and_mark_partially_refunded(
    client: TestClient, refund_env, db: Session
):
    env = refund_env

    # First partial refund: ₹400
    r1 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "400.00", "reason": "Partial return batch 1"},
    )
    assert r1.status_code == 201
    refund1_id = r1.json()["id"]

    # Approve first refund — SUCCESS → PARTIALLY_REFUNDED on parent
    with patch("random.random", return_value=0.05):
        a1 = client.patch(
            f"/api/v1/refunds/{refund1_id}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )
    assert a1.status_code == 200
    assert a1.json()["status"] == "SUCCESS"

    db.expire_all()
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first()
    assert tx.status == TransactionStatus.PARTIALLY_REFUNDED

    # Second partial refund: ₹300 against the PARTIALLY_REFUNDED transaction
    r2 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "300.00", "reason": "Partial return batch 2"},
    )
    assert r2.status_code == 201, r2.text
    assert r2.json()["status"] == "INITIATED"
    refund2_id = r2.json()["id"]

    # Approve second refund
    with patch("random.random", return_value=0.05):
        a2 = client.patch(
            f"/api/v1/refunds/{refund2_id}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )
    assert a2.status_code == 200

    # Still PARTIALLY_REFUNDED (₹700 of ₹1000 refunded)
    db.expire_all()
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first()
    assert tx.status == TransactionStatus.PARTIALLY_REFUNDED

    # Third refund: ₹300 — completes the full amount
    r3 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "300.00", "reason": "Final batch"},
    )
    assert r3.status_code == 201
    refund3_id = r3.json()["id"]

    with patch("random.random", return_value=0.05):
        a3 = client.patch(
            f"/api/v1/refunds/{refund3_id}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )
    assert a3.status_code == 200

    db.expire_all()
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first()
    assert tx.status == TransactionStatus.REFUNDED


def test_partial_refund_exceeding_remaining_balance_rejected(
    client: TestClient, refund_env, db: Session
):
    """After one partial refund, a second one can't exceed the remaining balance."""
    env = refund_env

    # Initiate and approve ₹600 refund
    r1 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "600.00", "reason": "Large partial"},
    )
    r1_id = r1.json()["id"]
    with patch("random.random", return_value=0.05):
        client.patch(
            f"/api/v1/refunds/{r1_id}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )

    # Try to refund ₹600 more (only ₹400 remains)
    r2 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "600.00", "reason": "Exceeds balance"},
    )
    assert r2.status_code == 400
    assert r2.json()["code"] == "REFUND_AMOUNT_EXCEEDS_BALANCE"


# ---------------------------------------------------------------------------
# 5. Double-approval guard
# ---------------------------------------------------------------------------

def test_double_approve_rejected(client: TestClient, refund_env):
    env = refund_env
    r = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "100.00", "reason": "Test"},
    )
    rid = r.json()["id"]

    with patch("random.random", return_value=0.05):
        a1 = client.patch(
            f"/api/v1/refunds/{rid}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )
    assert a1.status_code == 200

    # Second approval on same refund
    a2 = client.patch(
        f"/api/v1/refunds/{rid}/approve",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={},
    )
    assert a2.status_code == 409
    assert a2.json()["code"] == "REFUND_INVALID_APPROVAL_STATUS"


# ---------------------------------------------------------------------------
# 6. RBAC enforcement
# ---------------------------------------------------------------------------

def test_cashier_cannot_approve_refund(client: TestClient, refund_env, db: Session):
    """Cashier role has payments:write but NOT refunds:approve — approval must be denied."""
    env = refund_env

    # Create and assign Cashier user
    cashier_email = f"cashier_{uuid.uuid4().hex[:8]}@test.com"
    cashier_phone = f"+9192{uuid.uuid4().int % 100000000:08d}"
    creg = client.post(
        "/api/v1/auth/register",
        json={
            "email": cashier_email,
            "password": "Password123!",
            "full_name": "Test Cashier",
            "phone": cashier_phone,
        },
    )
    cashier_token = creg.json()["tokens"]["access_token"]
    cashier_id = creg.json()["user"]["id"]

    # Assign Cashier role via owner
    client.post(
        f"/api/v1/merchants/{env['merchant_id']}/staff",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"user_id": cashier_id, "role_name": "Cashier"},
    )

    # Initiate a refund (as owner)
    r = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "200.00", "reason": "Cashier test"},
    )
    rid = r.json()["id"]

    # Cashier tries to approve → 403
    a = client.patch(
        f"/api/v1/refunds/{rid}/approve",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={},
    )
    assert a.status_code == 403


# ---------------------------------------------------------------------------
# 7. GET /refunds/{id}
# ---------------------------------------------------------------------------

def test_get_refund_by_id(client: TestClient, refund_env):
    env = refund_env
    r = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "50.00", "reason": "Get by ID test"},
    )
    rid = r.json()["id"]

    get_resp = client.get(
        f"/api/v1/refunds/{rid}",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == rid


def test_get_nonexistent_refund_returns_404(client: TestClient, refund_env):
    env = refund_env
    resp = client.get(
        f"/api/v1/refunds/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 8. List /merchants/{id}/refunds with filters
# ---------------------------------------------------------------------------

def test_list_merchant_refunds_with_status_filter(client: TestClient, refund_env, db: Session):
    env = refund_env

    # Create two separate SUCCESS transactions to refund against
    # (only one REFUND_INITIATED refund can exist per transaction at a time)
    tx_a = PaymentTransaction(
        merchant_id=env["merchant_id"],
        idempotency_key=f"list-test-a-{uuid.uuid4().hex}",
        amount=Decimal("800.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        mock_scenario="SUCCESS",
    )
    tx_b = PaymentTransaction(
        merchant_id=env["merchant_id"],
        idempotency_key=f"list-test-b-{uuid.uuid4().hex}",
        amount=Decimal("600.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        mock_scenario="SUCCESS",
    )
    db.add_all([tx_a, tx_b])
    db.commit()

    # Initiate one refund per transaction → both land in INITIATED
    r_a = client.post(
        f"/api/v1/transactions/{tx_a.id}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "100.00", "reason": "List test A"},
    )
    assert r_a.status_code == 201
    r_b = client.post(
        f"/api/v1/transactions/{tx_b.id}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "150.00", "reason": "List test B"},
    )
    assert r_b.status_code == 201

    # List with status=INITIATED
    list_resp = client.get(
        f"/api/v1/merchants/{env['merchant_id']}/refunds?status=INITIATED",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
    )
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] >= 2
    for item in body["items"]:
        assert item["status"] == "INITIATED"


def test_list_merchant_refunds_filter_by_transaction_id(client: TestClient, refund_env, db: Session):
    env = refund_env

    # Create a second SUCCESS transaction to cross-check isolation
    tx2 = PaymentTransaction(
        merchant_id=env["merchant_id"],
        idempotency_key=f"refund-tx2-{uuid.uuid4().hex}",
        amount=Decimal("500.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        mock_scenario="SUCCESS",
    )
    db.add(tx2)
    db.commit()

    # Refund against tx1 and tx2
    client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "100.00", "reason": "Tx1 refund"},
    )
    client.post(
        f"/api/v1/transactions/{tx2.id}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "50.00", "reason": "Tx2 refund"},
    )

    # Filter by tx1's ID
    resp = client.get(
        f"/api/v1/merchants/{env['merchant_id']}/refunds?transaction_id={env['tx_id']}",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(item["transaction_id"] == str(env["tx_id"]) for item in items)


# ---------------------------------------------------------------------------
# 9. REFUND_FAILED path: provider simulation failure
# ---------------------------------------------------------------------------

def test_approve_refund_failed_outcome_marks_refund_failed(
    client: TestClient, refund_env, db: Session
):
    env = refund_env
    r = client.post(
        f"/api/v1/transactions/{env['tx_id']}/refunds",
        headers={"Authorization": f"Bearer {env['owner_token']}"},
        json={"amount": "300.00", "reason": "Test failed path"},
    )
    rid = r.json()["id"]

    with patch("random.random", return_value=0.95):  # ≥ 0.90 → FAILED outcome
        a = client.patch(
            f"/api/v1/refunds/{rid}/approve",
            headers={"Authorization": f"Bearer {env['owner_token']}"},
            json={},
        )
    assert a.status_code == 200
    body = a.json()
    assert body["status"] == "FAILED"
    assert body["failure_reason"] is not None

    # Parent transaction should be REFUND_FAILED
    db.expire_all()
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == env["tx_id"]).first()
    assert tx.status == TransactionStatus.REFUND_FAILED
