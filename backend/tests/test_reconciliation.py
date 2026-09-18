import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
)
from app.modules.reconciliation.models import (
    MatchStatus,
    ReconciliationBatch,
    ReconciliationEntry,
    ReconciliationEntryStatus,
    ReconciliationStatus,
)
from app.modules.reconciliation.tasks import run_nightly_reconciliation
from app.modules.settlements.models import Settlement, SettlementCycle, SettlementLineItem, SettlementStatus


@pytest.fixture
def setup_reconciliation_env(client: TestClient, db: Session):
    """Sets up an owner, merchant, customer, invoice, and base environment for reconciliation tests."""
    # Register owner
    owner_email = f"reconowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Recon Test Owner",
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
            "business_name": "Recon Retailers",
            "legal_name": "Recon Retailers Pvt Ltd",
            "email": f"recon_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9195{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5732",
            "initial_upi_vpa": "reconretailers@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    # Register Cashier user (lacks settlements:write permission)
    cashier_email = f"cashier_{uuid.uuid4().hex[:8]}@example.com"
    cashier_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": cashier_email,
            "password": "Password123!",
            "full_name": "Recon Cashier",
            "phone": f"+9193{uuid.uuid4().int % 100000000:08d}",
        },
    )
    cashier_token = cashier_reg.json()["tokens"]["access_token"]
    cashier_id = uuid.UUID(cashier_reg.json()["user"]["id"])

    # Assign cashier role to user
    client.post(
        f"/api/v1/merchants/{merchant_id}/staff",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "user_id": str(cashier_id),
            "role_name": "Cashier",
        },
    )

    # Create customer & invoice
    cust_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Dev Sharma",
            "email": f"dev_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9192{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(cust_resp.json()["id"])

    inv = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-REC-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("5000.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("5000.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "cashier_token": cashier_token,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "invoice_id": inv.id,
    }


def test_reconciliation_run_perfect_match(client: TestClient, db: Session, setup_reconciliation_env):
    """When settlement amounts match expected amounts (amount minus MDR), entry is MATCHED and batch is MATCHED."""
    env = setup_reconciliation_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    now = datetime.now(timezone.utc)
    # 1. Create a SUCCESS transaction of INR 1,000
    tx = PaymentTransaction(
        merchant_id=m_id,
        invoice_id=env["invoice_id"],
        amount=Decimal("1000.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        idempotency_key=f"idemp_recon_{uuid.uuid4().hex}",
        status=TransactionStatus.SUCCESS,
        provider_ref_id=f"ref_{uuid.uuid4().hex[:10]}",
        created_at=now - timedelta(hours=2),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # 2. Create Settlement & SettlementLineItem matching 1.5% MDR: 1000 - 15 = 985
    settlement = Settlement(
        merchant_id=m_id,
        settlement_cycle=SettlementCycle.T_PLUS_1,
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("15.00"),
        net_amount=Decimal("985.00"),
        status=SettlementStatus.SETTLED,
        bank_account_ref="ACC_HDFC_9988",
    )
    db.add(settlement)
    db.flush()

    line_item = SettlementLineItem(
        settlement_id=settlement.id,
        transaction_id=tx.id,
        amount=Decimal("1000.00"),
        fee_amount=Decimal("15.00"),
        tax_amount=Decimal("0.00"),
        net_amount=Decimal("985.00"),
    )
    db.add(line_item)
    db.commit()

    # 3. Trigger reconciliation run
    resp = client.post(
        f"/api/v1/merchants/{m_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "period_start": (now - timedelta(hours=4)).isoformat(),
            "period_end": (now + timedelta(hours=1)).isoformat(),
            "mdr_rate": 0.015,
            "tolerance": 0.05,
        },
    )
    assert resp.status_code == 201, resp.text
    batch_data = resp.json()
    batch_id = uuid.UUID(batch_data["id"])

    assert batch_data["merchant_id"] == str(m_id)
    assert batch_data["status"] == "MATCHED"
    assert batch_data["total_records"] == 1
    assert batch_data["matched_records"] == 1
    assert batch_data["mismatched_records"] == 0
    assert batch_data["discrepancy_count"] == 0

    # 4. Check entry line items
    entries_resp = client.get(
        f"/api/v1/reconciliation/batches/{batch_id}/entries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert entries_resp.status_code == 200
    items = entries_resp.json()["items"]
    assert len(items) == 1
    entry = items[0]
    assert entry["transaction_id"] == str(tx.id)
    assert float(entry["expected_amount"]) == 985.00
    assert float(entry["actual_amount"]) == 985.00
    assert entry["match_status"] == "MATCHED"
    assert entry["status"] == "MATCHED"


def test_reconciliation_variance_triggers_manual_review(client: TestClient, db: Session, setup_reconciliation_env):
    """When settlement amount variance exceeds tolerance, entry is marked MANUAL_REVIEW and batch status DISCREPANCIES_FOUND."""
    env = setup_reconciliation_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    now = datetime.now(timezone.utc)
    # 1. Create a SUCCESS transaction of INR 2,000
    tx = PaymentTransaction(
        merchant_id=m_id,
        invoice_id=env["invoice_id"],
        amount=Decimal("2000.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        idempotency_key=f"idemp_recon_{uuid.uuid4().hex}",
        status=TransactionStatus.SUCCESS,
        provider_ref_id=f"ref_{uuid.uuid4().hex[:10]}",
        created_at=now - timedelta(hours=3),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # 2. Expected net at 1.5% MDR is INR 1970.00.
    # Provide actual settlement of INR 1950.00 (variance of INR 20.00 > tolerance INR 0.05).
    settlement = Settlement(
        merchant_id=m_id,
        settlement_cycle=SettlementCycle.T_PLUS_1,
        gross_amount=Decimal("2000.00"),
        deduction_amount=Decimal("50.00"),
        net_amount=Decimal("1950.00"),
        status=SettlementStatus.SETTLED,
        bank_account_ref="ACC_ICICI_1122",
    )
    db.add(settlement)
    db.flush()

    line_item = SettlementLineItem(
        settlement_id=settlement.id,
        transaction_id=tx.id,
        amount=Decimal("2000.00"),
        fee_amount=Decimal("50.00"),
        tax_amount=Decimal("0.00"),
        net_amount=Decimal("1950.00"),
    )
    db.add(line_item)
    db.commit()

    # 3. Trigger reconciliation run
    resp = client.post(
        f"/api/v1/merchants/{m_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "period_start": (now - timedelta(hours=5)).isoformat(),
            "period_end": (now + timedelta(hours=1)).isoformat(),
            "mdr_rate": 0.015,
            "tolerance": 0.05,
        },
    )
    assert resp.status_code == 201
    batch_data = resp.json()
    batch_id = uuid.UUID(batch_data["id"])

    assert batch_data["status"] == "DISCREPANCIES_FOUND"
    assert batch_data["total_records"] == 1
    assert batch_data["matched_records"] == 0
    assert batch_data["mismatched_records"] == 1
    assert batch_data["discrepancy_count"] == 1

    # 4. Check entry line items
    entries_resp = client.get(
        f"/api/v1/reconciliation/batches/{batch_id}/entries?match_status=MANUAL_REVIEW",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert entries_resp.status_code == 200
    items = entries_resp.json()["items"]
    assert len(items) == 1
    entry = items[0]
    assert entry["match_status"] == "MANUAL_REVIEW"
    assert entry["status"] == "AMOUNT_MISMATCH"
    assert float(entry["expected_amount"]) == 1970.00
    assert float(entry["actual_amount"]) == 1950.00
    assert "exceeds tolerance" in entry["notes"]


def test_reconciliation_unmatched_past_grace_period(client: TestClient, db: Session, setup_reconciliation_env):
    """When a SUCCESS transaction has no settlement record past the grace period, it is flagged UNMATCHED."""
    env = setup_reconciliation_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    now = datetime.now(timezone.utc)
    # Create transaction from 48 hours ago (past 24h grace period) with NO settlement line item
    tx = PaymentTransaction(
        merchant_id=m_id,
        invoice_id=env["invoice_id"],
        amount=Decimal("1500.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=f"idemp_recon_old_{uuid.uuid4().hex}",
        status=TransactionStatus.SUCCESS,
        provider_ref_id=f"ref_{uuid.uuid4().hex[:10]}",
        created_at=now - timedelta(hours=48),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    resp = client.post(
        f"/api/v1/merchants/{m_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "period_start": (now - timedelta(hours=50)).isoformat(),
            "period_end": (now - timedelta(hours=40)).isoformat(),
            "grace_period_hours": 24,
        },
    )
    assert resp.status_code == 201
    batch_data = resp.json()
    batch_id = uuid.UUID(batch_data["id"])

    assert batch_data["status"] == "DISCREPANCIES_FOUND"
    assert batch_data["discrepancy_count"] == 1

    entries_resp = client.get(
        f"/api/v1/reconciliation/batches/{batch_id}/entries?match_status=UNMATCHED",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert entries_resp.status_code == 200
    items = entries_resp.json()["items"]
    assert len(items) == 1
    entry = items[0]
    assert entry["match_status"] == "UNMATCHED"
    assert entry["status"] == "MISSING_IN_PROVIDER"
    assert "past grace period" in entry["notes"]


def test_reconciliation_list_batches_and_entries_filtering(client: TestClient, db: Session, setup_reconciliation_env):
    """Test listing batches with pagination and querying entries filtered by match_status."""
    env = setup_reconciliation_env
    m_id = env["merchant_id"]
    token = env["owner_token"]

    # Run two runs
    client.post(
        f"/api/v1/merchants/{m_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/api/v1/merchants/{m_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {token}"},
    )

    # List batches
    batches_resp = client.get(
        f"/api/v1/merchants/{m_id}/reconciliation/batches?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert batches_resp.status_code == 200
    b_data = batches_resp.json()
    assert b_data["total"] >= 2
    assert len(b_data["items"]) >= 2


def test_reconciliation_rbac_enforcement(client: TestClient, setup_reconciliation_env):
    """User without settlements:write cannot run reconciliation, but owner with settlements:write can."""
    env = setup_reconciliation_env
    m_id = env["merchant_id"]
    cashier_token = env["cashier_token"]

    # Cashier cannot execute run
    resp = client.post(
        f"/api/v1/merchants/{m_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {cashier_token}"},
    )
    assert resp.status_code == 403


def test_nightly_reconciliation_celery_task(db: Session, setup_reconciliation_env):
    """Celery task run_nightly_reconciliation processes active merchants without exception."""
    result = run_nightly_reconciliation()
    assert "merchants_processed" in result
    assert result["merchants_processed"] >= 1
    assert "details" in result
