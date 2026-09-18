"""Tests for Duplicate Detection module: Celery task, API endpoints, flag resolution, and summary."""
import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.customers.models import Customer
from app.modules.duplicate_detection.models import (
    DuplicateFlagStatus,
    DuplicateTransactionFlag,
)
from app.modules.duplicate_detection.service import DuplicateDetectionService
from app.modules.duplicate_detection.tasks import detect_duplicate_transaction
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
)


@pytest.fixture
def setup_dup_env(client: TestClient, db: Session):
    """Sets up an owner, merchant, customer, and invoices for duplicate detection tests."""
    owner_email = f"dupowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Duplicate Test Owner",
            "phone": owner_phone,
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]
    owner_id = uuid.UUID(reg.json()["user"]["id"])

    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Duplicate Retail",
            "legal_name": "Duplicate Retail Pvt Ltd",
            "email": f"dup_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "dupretail@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    c_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Kavita Rao",
            "email": f"kavita_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9191{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(c_resp.json()["id"])

    inv1 = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-DUP-1-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("2000.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("2000.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        allow_partial_payment=True,
    )
    inv2 = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-DUP-2-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("1500.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("1500.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        allow_partial_payment=True,
    )
    db.add_all([inv1, inv2])
    db.commit()
    db.refresh(inv1)
    db.refresh(inv2)

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "invoice_1_id": inv1.id,
        "invoice_2_id": inv2.id,
    }


def test_duplicate_detection_same_invoice_and_amount(client: TestClient, db: Session, setup_dup_env):
    """Two transactions on same invoice with identical amount within 15 mins are flagged."""
    headers = {
        "Authorization": f"Bearer {setup_dup_env['owner_token']}",
    }
    inv_id = str(setup_dup_env["invoice_1_id"])
    merchant_id = setup_dup_env["merchant_id"]

    # 1. First transaction
    tx1_resp = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"dup-tx1-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "500.00",
            "payment_method": "UPI_INTENT",
            "payer_vpa": "kavita@upi",
            "scenario": "SUCCESS",
        },
    )
    assert tx1_resp.status_code == 201, tx1_resp.text
    tx1_id = uuid.UUID(tx1_resp.json()["id"])

    # 2. Second transaction with matching amount and method
    tx2_resp = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"dup-tx2-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "500.00",
            "payment_method": "UPI_INTENT",
            "payer_vpa": "kavita@upi",
            "scenario": "SUCCESS",
        },
    )
    assert tx2_resp.status_code == 201, tx2_resp.text
    tx2_id = uuid.UUID(tx2_resp.json()["id"])

    # In eager mode, Celery task ran synchronously. Verify flag was created in DB.
    flag = (
        db.query(DuplicateTransactionFlag)
        .filter(
            DuplicateTransactionFlag.merchant_id == merchant_id,
            DuplicateTransactionFlag.original_transaction_id.in_([tx1_id, tx2_id]),
            DuplicateTransactionFlag.duplicate_transaction_id.in_([tx1_id, tx2_id]),
        )
        .first()
    )
    assert flag is not None
    assert flag.status == DuplicateFlagStatus.SUSPECTED
    assert "same invoice" in flag.match_reason.lower()
    assert "500.00" in flag.match_reason


def test_duplicate_detection_provider_duplicate_scenario(client: TestClient, db: Session, setup_dup_env):
    """A transaction returning provider DUPLICATE scenario is flagged."""
    headers = {
        "Authorization": f"Bearer {setup_dup_env['owner_token']}",
    }
    inv_id = str(setup_dup_env["invoice_1_id"])
    merchant_id = setup_dup_env["merchant_id"]

    resp = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"prov-dup-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "300.00",
            "payment_method": "UPI_INTENT",
            "scenario": "DUPLICATE",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "DUPLICATE"
    tx_id = uuid.UUID(resp.json()["id"])

    flag = (
        db.query(DuplicateTransactionFlag)
        .filter(
            DuplicateTransactionFlag.merchant_id == merchant_id,
            DuplicateTransactionFlag.duplicate_transaction_id == tx_id,
        )
        .first()
    )
    assert flag is not None
    assert "Provider reported DUPLICATE scenario" in flag.match_reason


def test_duplicate_detection_same_customer_different_invoice(client: TestClient, db: Session, setup_dup_env):
    """Two transactions for the same customer on different invoices with identical amount are flagged."""
    headers = {
        "Authorization": f"Bearer {setup_dup_env['owner_token']}",
    }
    inv1_id = str(setup_dup_env["invoice_1_id"])
    inv2_id = str(setup_dup_env["invoice_2_id"])
    merchant_id = setup_dup_env["merchant_id"]
    customer_id = str(setup_dup_env["customer_id"])

    tx1 = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"cust-dup1-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv1_id,
            "customer_id": customer_id,
            "amount": "777.00",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    assert tx1.status_code == 201, tx1.text
    tx1_id = uuid.UUID(tx1.json()["id"])

    tx2 = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"cust-dup2-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv2_id,
            "customer_id": customer_id,
            "amount": "777.00",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    assert tx2.status_code == 201, tx2.text
    tx2_id = uuid.UUID(tx2.json()["id"])

    flag = (
        db.query(DuplicateTransactionFlag)
        .filter(
            DuplicateTransactionFlag.merchant_id == merchant_id,
            DuplicateTransactionFlag.original_transaction_id.in_([tx1_id, tx2_id]),
            DuplicateTransactionFlag.duplicate_transaction_id.in_([tx1_id, tx2_id]),
        )
        .first()
    )
    assert flag is not None
    assert "same customer" in flag.match_reason.lower()


def test_list_merchant_transactions_flag_filter(client: TestClient, db: Session, setup_dup_env):
    """GET /merchants/{id}/transactions?flag=duplicate filters to flagged transactions only."""
    headers = {"Authorization": f"Bearer {setup_dup_env['owner_token']}"}
    merchant_id = setup_dup_env["merchant_id"]
    inv_id = str(setup_dup_env["invoice_1_id"])

    # Create a non-duplicate transaction (unique amount)
    unique_tx = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"unique-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "123.45",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    assert unique_tx.status_code == 201, unique_tx.text
    unique_id = unique_tx.json()["id"]

    # Create two duplicate transactions
    d1 = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"filt-dup1-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "888.00",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    d2 = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"filt-dup2-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "888.00",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    assert d1.status_code == 201, d1.text
    assert d2.status_code == 201, d2.text
    d1_id = d1.json()["id"]
    d2_id = d2.json()["id"]

    # Query without flag filter
    all_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/transactions",
        headers=headers,
    )
    assert all_resp.status_code == 200
    all_ids = [tx["id"] for tx in all_resp.json()["items"]]
    assert unique_id in all_ids
    assert d1_id in all_ids
    assert d2_id in all_ids

    # Query with flag=duplicate filter
    dup_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/transactions?flag=duplicate",
        headers=headers,
    )
    assert dup_resp.status_code == 200
    dup_ids = [tx["id"] for tx in dup_resp.json()["items"]]
    assert unique_id not in dup_ids
    assert d1_id in dup_ids or d2_id in dup_ids


def test_resolve_duplicate_flag_and_audit(client: TestClient, db: Session, setup_dup_env):
    """PATCH /duplicate-flags/{id}/resolve marks flag resolved and creates an audit log."""
    headers = {"Authorization": f"Bearer {setup_dup_env['owner_token']}"}
    merchant_id = setup_dup_env["merchant_id"]
    owner_id = setup_dup_env["owner_id"]
    inv_id = str(setup_dup_env["invoice_1_id"])

    # Create duplicate pair
    r1 = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"res-tx1-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "444.00",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    assert r1.status_code == 201, r1.text
    r2 = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"res-tx2-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "444.00",
            "payment_method": "UPI_INTENT",
            "scenario": "SUCCESS",
        },
    )
    assert r2.status_code == 201, r2.text

    # List flags to get flag ID
    list_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/duplicate-flags",
        headers=headers,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    flag_item = next(f for f in items if "444.00" in f["match_reason"])
    flag_id = flag_item["id"]

    # Resolve flag
    resolve_resp = client.patch(
        f"/duplicate-flags/{flag_id}/resolve",
        headers=headers,
        json={
            "reason": "Confirmed customer made two intentional payments.",
            "resolved_by": str(owner_id),
        },
    )
    assert resolve_resp.status_code == 200, resolve_resp.text
    resolved_data = resolve_resp.json()
    assert resolved_data["status"] == "RESOLVED"
    assert resolved_data["resolution_reason"] == "Confirmed customer made two intentional payments."
    assert resolved_data["resolved_by"] == str(owner_id)
    assert resolved_data["resolved_at"] is not None

    # Check Audit Log in DB
    audit_entry = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "duplicate_transaction_flags",
            AuditLog.entity_id == uuid.UUID(flag_id),
            AuditLog.action == "UPDATE",
        )
        .first()
    )
    assert audit_entry is not None
    assert audit_entry.changes["after"]["status"] == "RESOLVED"


def test_duplicate_flags_summary_endpoint(client: TestClient, setup_dup_env):
    """GET /merchants/{id}/duplicate-flags/summary surfaces unresolved count accurately."""
    headers = {"Authorization": f"Bearer {setup_dup_env['owner_token']}"}
    merchant_id = setup_dup_env["merchant_id"]

    # Initial summary
    summary1 = client.get(
        f"/api/v1/merchants/{merchant_id}/duplicate-flags/summary",
        headers=headers,
    )
    assert summary1.status_code == 200
    init_count = summary1.json()["unresolved_count"]

    # Trigger a new duplicate via provider DUPLICATE scenario
    inv_id = str(setup_dup_env["invoice_1_id"])
    p_resp = client.post(
        "/api/v1/payments/initiate",
        headers={**headers, "Idempotency-Key": f"summary-dup-{uuid.uuid4().hex}"},
        json={
            "merchant_id": str(merchant_id),
            "invoice_id": inv_id,
            "amount": "999.00",
            "payment_method": "UPI_INTENT",
            "scenario": "DUPLICATE",
        },
    )
    assert p_resp.status_code == 201, p_resp.text

    summary2 = client.get(
        f"/api/v1/merchants/{merchant_id}/duplicate-flags/summary",
        headers=headers,
    )
    assert summary2.status_code == 200
    assert summary2.json()["unresolved_count"] == init_count + 1

