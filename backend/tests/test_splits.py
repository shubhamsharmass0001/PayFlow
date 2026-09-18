import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.risk.models import RiskSignal, RiskLevel, RiskAction
from app.modules.splits.models import (
    InstallmentStatus,
    PaymentPlan,
    PaymentPlanInstallment,
    PaymentPlanStatus,
    PlanType,
)


@pytest.fixture
def setup_splits_env(client: TestClient, db: Session):
    """Sets up an owner, merchant, customer, and invoices for splits testing."""
    # Register owner
    owner_email = f"splitsowner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Splits Test Owner",
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
            "business_name": "Splits Emporium",
            "legal_name": "Splits Emporium Pvt Ltd",
            "email": f"splits_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9195{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5732",
            "initial_upi_vpa": "splitsemporium@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])

    # Create customer
    c_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Kavita Rao",
            "email": f"kavita_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9192{uuid.uuid4().int % 100000000:08d}",
        },
    )
    customer_id = uuid.UUID(c_resp.json()["id"])

    # Create standard invoice of 1000.00
    inv = Invoice(
        merchant_id=merchant_id,
        customer_id=customer_id,
        invoice_number=f"INV-SPLIT-{uuid.uuid4().hex[:6].upper()}",
        subtotal=Decimal("1000.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("1000.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        allow_split_payment=True,
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


def test_create_payment_plan_exact_reconciliation_success(client: TestClient, setup_splits_env):
    token = setup_splits_env["owner_token"]
    invoice_id = setup_splits_env["invoice_id"]
    now = datetime.now(timezone.utc)

    # 2 installments summing exactly to 1000.00
    payload = {
        "plan_type": "INSTALLMENT",
        "installments": [
            {
                "label": "First Installment",
                "amount": 600.00,
                "due_date": (now + timedelta(days=7)).isoformat(),
            },
            {
                "label": "Second Installment",
                "amount": 400.00,
                "due_date": (now + timedelta(days=14)).isoformat(),
            },
        ],
    }

    resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["plan_type"] == "INSTALLMENT"
    assert data["total_amount"] == "1000.00"
    assert data["status"] == "ACTIVE"
    assert len(data["installments"]) == 2
    assert data["installments"][0]["label"] == "First Installment"
    assert data["installments"][0]["status"] == "PENDING"


def test_create_payment_plan_reconciliation_mismatch_rejected(client: TestClient, setup_splits_env):
    token = setup_splits_env["owner_token"]
    invoice_id = setup_splits_env["invoice_id"]
    now = datetime.now(timezone.utc)

    # Sum is 800.00 != invoice total 1000.00
    payload = {
        "plan_type": "INSTALLMENT",
        "installments": [
            {
                "label": "Installment 1",
                "amount": 500.00,
                "due_date": (now + timedelta(days=7)).isoformat(),
            },
            {
                "label": "Installment 2",
                "amount": 300.00,
                "due_date": (now + timedelta(days=14)).isoformat(),
            },
        ],
    }

    resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "PLAN_RECONCILIATION_FAILED"


def test_deposit_plan_reconciliation_with_collected_deposit(
    client: TestClient, db: Session, setup_splits_env
):
    token = setup_splits_env["owner_token"]
    merchant_id = setup_splits_env["merchant_id"]
    now = datetime.now(timezone.utc)

    # Create invoice with 3000.00 total and 1000.00 already collected
    inv = Invoice(
        merchant_id=merchant_id,
        invoice_number=f"INV-DEP-{uuid.uuid4().hex[:6].upper()}",
        total_amount=Decimal("3000.00"),
        paid_amount=Decimal("1000.00"),
        currency="INR",
        status=InvoiceStatus.PARTIALLY_PAID,
        allow_split_payment=True,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # For DEPOSIT, target is 3000 - 1000 = 2000.00
    payload = {
        "plan_type": "DEPOSIT",
        "installments": [
            {
                "label": "Final Settlement Balance",
                "amount": 2000.00,
                "due_date": (now + timedelta(days=30)).isoformat(),
            }
        ],
    }
    resp = client.post(
        f"/api/v1/invoices/{inv.id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201
    assert resp.json()["total_amount"] == "2000.00"


def test_anti_structuring_heuristic_triggers_risk_signal(
    client: TestClient, db: Session, setup_splits_env
):
    token = setup_splits_env["owner_token"]
    merchant_id = setup_splits_env["merchant_id"]

    # Invoice with 7600.00
    inv = Invoice(
        merchant_id=merchant_id,
        invoice_number=f"INV-STRUC-{uuid.uuid4().hex[:6].upper()}",
        total_amount=Decimal("7600.00"),
        paid_amount=Decimal("0.00"),
        currency="INR",
        status=InvoiceStatus.SENT,
        allow_split_payment=True,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # 4 installments of 1900.00 each on the exact same date (no date spread)
    same_due_date = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    payload = {
        "plan_type": "CUSTOM_SPLIT",
        "installments": [
            {"label": "Part 1", "amount": 1900.00, "due_date": same_due_date.isoformat()},
            {"label": "Part 2", "amount": 1900.00, "due_date": same_due_date.isoformat()},
            {"label": "Part 3", "amount": 1900.00, "due_date": same_due_date.isoformat()},
            {"label": "Part 4", "amount": 1900.00, "due_date": same_due_date.isoformat()},
        ],
    }

    # Plan creation must succeed (not blocked outright)
    resp = client.post(
        f"/api/v1/invoices/{inv.id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201

    # But an auditable RiskSignal must be created
    signal = (
        db.query(RiskSignal)
        .filter(
            RiskSignal.merchant_id == merchant_id,
            RiskSignal.rule_triggered == "STRUCTURING_PATTERN",
        )
        .order_by(RiskSignal.created_at.desc())
        .first()
    )
    assert signal is not None
    assert signal.risk_level == RiskLevel.HIGH
    assert signal.action_taken == RiskAction.FLAG_FOR_REVIEW
    assert signal.metadata_json["signal_type"] == "STRUCTURING_PATTERN"
    assert signal.metadata_json["installment_count"] == 4


def test_initiate_installment_payment_reuses_phase8_and_settles(
    client: TestClient, db: Session, setup_splits_env
):
    token = setup_splits_env["owner_token"]
    invoice_id = setup_splits_env["invoice_id"]
    now = datetime.now(timezone.utc)

    # 1. Create plan: 600.00 and 400.00
    plan_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "plan_type": "INSTALLMENT",
            "installments": [
                {"label": "Slice 1", "amount": 600.00, "due_date": (now + timedelta(days=1)).isoformat()},
                {"label": "Slice 2", "amount": 400.00, "due_date": (now + timedelta(days=2)).isoformat()},
            ],
        },
    )
    assert plan_resp.status_code == 201
    plan_data = plan_resp.json()
    plan_id = plan_data["id"]
    inst1_id = plan_data["installments"][0]["id"]
    inst2_id = plan_data["installments"][1]["id"]

    # 2. Settle Installment 1 (600.00) with SUCCESS
    pay1_resp = client.post(
        f"/api/v1/payment-plans/{plan_id}/installments/{inst1_id}/initiate",
        headers={"Idempotency-Key": f"idemp_inst_1_{uuid.uuid4().hex}"},
        json={"scenario": "SUCCESS"},
    )
    assert pay1_resp.status_code == 201
    assert pay1_resp.json()["status"] == "SUCCESS"
    assert pay1_resp.json()["installment_id"] == inst1_id

    # Verify Installment 1 is marked PAID
    inst1 = db.query(PaymentPlanInstallment).filter(PaymentPlanInstallment.id == inst1_id).first()
    db.refresh(inst1)
    assert inst1.status == InstallmentStatus.PAID
    assert inst1.paid_amount == Decimal("600.00")

    # Verify Invoice is now PARTIALLY_PAID (600/1000)
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    db.refresh(inv)
    assert inv.status == InvoiceStatus.PARTIALLY_PAID
    assert inv.paid_amount == Decimal("600.00")

    # Verify Plan is still ACTIVE (slice 2 remaining)
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == plan_id).first()
    db.refresh(plan)
    assert plan.status == PaymentPlanStatus.ACTIVE

    # 3. Settle Installment 2 (400.00) with SUCCESS
    pay2_resp = client.post(
        f"/api/v1/payment-plans/{plan_id}/installments/{inst2_id}/initiate",
        headers={"Idempotency-Key": f"idemp_inst_2_{uuid.uuid4().hex}"},
        json={"scenario": "SUCCESS"},
    )
    assert pay2_resp.status_code == 201

    # Verify Installment 2 is PAID
    inst2 = db.query(PaymentPlanInstallment).filter(PaymentPlanInstallment.id == inst2_id).first()
    db.refresh(inst2)
    assert inst2.status == InstallmentStatus.PAID

    # Verify Plan is COMPLETED
    db.refresh(plan)
    assert plan.status == PaymentPlanStatus.COMPLETED

    # Verify Invoice is fully PAID (1000/1000)
    db.refresh(inv)
    assert inv.status == InvoiceStatus.PAID
    assert inv.paid_amount == Decimal("1000.00")

    # 4. Attempting to initiate payment on already PAID installment is rejected
    pay_again = client.post(
        f"/api/v1/payment-plans/{plan_id}/installments/{inst1_id}/initiate",
        headers={"Idempotency-Key": f"idemp_inst_again_{uuid.uuid4().hex}"},
        json={"scenario": "SUCCESS"},
    )
    assert pay_again.status_code == 400
    assert pay_again.json()["code"] == "INSTALLMENT_ALREADY_PAID"


def test_get_invoice_payment_plans(client: TestClient, setup_splits_env):
    token = setup_splits_env["owner_token"]
    invoice_id = setup_splits_env["invoice_id"]
    now = datetime.now(timezone.utc)

    # Create plan
    client.post(
        f"/api/v1/invoices/{invoice_id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "plan_type": "MILESTONE",
            "installments": [
                {"label": "Phase 1 Delivery", "amount": 500.00, "due_date": (now + timedelta(days=10)).isoformat()},
                {"label": "Final Handover", "amount": 500.00, "due_date": (now + timedelta(days=20)).isoformat()},
            ],
        },
    )

    # Get plans
    resp = client.get(
        f"/api/v1/invoices/{invoice_id}/payment-plans",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    plans = resp.json()
    assert len(plans) >= 1
    assert plans[0]["plan_type"] == "MILESTONE"
    assert len(plans[0]["installments"]) == 2
