"""Tests for the Risk Engine Module.

Covers:
  - Explicit rule evaluations:
    - VELOCITY_SPIKE (count and amount spikes)
    - ODD_HOUR (IST off-hours transaction detection)
    - STRUCTURING_PATTERN (sub-₹2,000 threshold avoidance & split structuring)
  - Celery task asynchronous evaluation
  - GET /merchants/{id}/risk/signals with severity and reviewed filters
  - PATCH /risk/signals/{id}/review with resolution notes and audit logging
  - GET /risk/rules explainable documentation endpoint
  - RBAC authorization checks
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction, AuditLog
from app.modules.customers.models import Customer
from app.modules.merchants.models import StaffRole
from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus
from app.modules.rbac.seed import seed_rbac_data
from app.modules.risk.models import RiskAction, RiskLevel, RiskSignal
from app.modules.risk.service import RiskService
from app.modules.risk.tasks import evaluate_risk_rules


@pytest.fixture
def risk_env(client: TestClient, db: Session):
    """Sets up merchant, owner, manager, and cashier for risk testing."""
    seed_rbac_data(db)

    # 1. Owner
    owner_email = f"risk_owner_{uuid.uuid4().hex[:8]}@example.com"
    r_owner = client.post(
        "/api/v1/auth/register",
        json={"email": owner_email, "password": "Password123!", "full_name": "Risk Owner"},
    )
    assert r_owner.status_code == 201
    owner_token = r_owner.json()["tokens"]["access_token"]
    owner_user_id = uuid.UUID(r_owner.json()["user"]["id"])

    # 2. Merchant
    r_merch = client.post(
        "/api/v1/merchants",
        json={
            "business_name": f"Risk Test Store {uuid.uuid4().hex[:6]}",
            "legal_name": "Risk Test Store Pvt Ltd",
            "email": f"riskstore_{uuid.uuid4().hex[:8]}@example.com",
            "phone": f"+9199{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "mcc_code": "5411",
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert r_merch.status_code == 201
    merchant_id = uuid.UUID(r_merch.json()["id"])

    # 3. Manager
    mgr_email = f"risk_mgr_{uuid.uuid4().hex[:8]}@example.com"
    r_mgr = client.post(
        "/api/v1/auth/register",
        json={"email": mgr_email, "password": "Password123!", "full_name": "Risk Manager"},
    )
    mgr_token = r_mgr.json()["tokens"]["access_token"]
    mgr_user_id = uuid.UUID(r_mgr.json()["user"]["id"])
    client.post(
        f"/api/v1/merchants/{merchant_id}/staff",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"user_id": str(mgr_user_id), "role": StaffRole.MANAGER.value},
    )

    # 4. Cashier
    csh_email = f"risk_csh_{uuid.uuid4().hex[:8]}@example.com"
    r_csh = client.post(
        "/api/v1/auth/register",
        json={"email": csh_email, "password": "Password123!", "full_name": "Risk Cashier"},
    )
    csh_token = r_csh.json()["tokens"]["access_token"]
    csh_user_id = uuid.UUID(r_csh.json()["user"]["id"])
    client.post(
        f"/api/v1/merchants/{merchant_id}/staff",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"user_id": str(csh_user_id), "role": StaffRole.CASHIER.value},
    )

    return {
        "merchant_id": merchant_id,
        "owner": {"token": owner_token, "user_id": owner_user_id},
        "manager": {"token": mgr_token, "user_id": mgr_user_id},
        "cashier": {"token": csh_token, "user_id": csh_user_id},
    }


def test_velocity_spike_rule_evaluation(db: Session, risk_env):
    """Verifies that VELOCITY_SPIKE detects count bursts and high-value spikes."""
    merchant_id = risk_env["merchant_id"]
    now = datetime.now(timezone.utc)

    # 1. Count spike: 5 transactions within the last 10 minutes
    txs = []
    for i in range(5):
        tx = PaymentTransaction(
            merchant_id=merchant_id,
            idempotency_key=f"vel-tx-{uuid.uuid4().hex}",
            amount=Decimal("150.00"),
            currency="INR",
            payment_method=PaymentMethod.UPI_QR,
            status=TransactionStatus.SUCCESS,
            created_at=now - timedelta(minutes=10 - i),
        )
        db.add(tx)
        txs.append(tx)
    db.commit()

    # Evaluate on the 5th transaction
    signals = RiskService.evaluate_transaction_rules(db=db, transaction_id=txs[-1].id)
    assert any(s.rule_triggered == "VELOCITY_SPIKE" for s in signals)
    vel_signal = next(s for s in signals if s.rule_triggered == "VELOCITY_SPIKE")
    assert vel_signal.risk_level == RiskLevel.HIGH
    assert vel_signal.action_taken == RiskAction.FLAG_FOR_REVIEW
    assert vel_signal.metadata_json["is_count_spike"] is True


def test_odd_hour_rule_evaluation(db: Session, risk_env):
    """Verifies that ODD_HOUR flags transactions occurring at e.g. 02:30 IST."""
    merchant_id = risk_env["merchant_id"]

    # Construct UTC timestamp that corresponds to 02:30 IST
    # 02:30 IST is 21:00 UTC previous day (02:30 - 05:30)
    odd_hour_utc = datetime(2026, 9, 17, 21, 0, 0, tzinfo=timezone.utc)

    tx = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"odd-tx-{uuid.uuid4().hex}",
        amount=Decimal("500.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        status=TransactionStatus.SUCCESS,
        created_at=odd_hour_utc,
    )
    db.add(tx)
    db.commit()

    signals = RiskService.evaluate_transaction_rules(db=db, transaction_id=tx.id)
    assert any(s.rule_triggered == "ODD_HOUR" for s in signals)
    odd_signal = next(s for s in signals if s.rule_triggered == "ODD_HOUR")
    assert odd_signal.risk_level == RiskLevel.MEDIUM
    assert odd_signal.metadata_json["hour_ist"] == 2


def test_structuring_pattern_rule_evaluation(db: Session, risk_env):
    """Verifies STRUCTURING_PATTERN detects >= 3 transactions clustering below ₹2,000."""
    merchant_id = risk_env["merchant_id"]
    cust = Customer(
        merchant_id=merchant_id,
        name="Structuring Customer",
        phone=f"+9198{uuid.uuid4().int % 100000000:08d}",
    )
    db.add(cust)
    db.commit()
    customer_id = cust.id
    now = datetime.now(timezone.utc)

    # 3 transactions just below ₹2,000 threshold (e.g. ₹1,950, ₹1,980, ₹1,990)
    tx1 = PaymentTransaction(
        merchant_id=merchant_id,
        customer_id=customer_id,
        idempotency_key=f"struct-tx-1-{uuid.uuid4().hex}",
        amount=Decimal("1950.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_INTENT,
        status=TransactionStatus.SUCCESS,
        created_at=now - timedelta(minutes=40),
    )
    tx2 = PaymentTransaction(
        merchant_id=merchant_id,
        customer_id=customer_id,
        idempotency_key=f"struct-tx-2-{uuid.uuid4().hex}",
        amount=Decimal("1980.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_INTENT,
        status=TransactionStatus.SUCCESS,
        created_at=now - timedelta(minutes=20),
    )
    tx3 = PaymentTransaction(
        merchant_id=merchant_id,
        customer_id=customer_id,
        idempotency_key=f"struct-tx-3-{uuid.uuid4().hex}",
        amount=Decimal("1990.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_INTENT,
        status=TransactionStatus.SUCCESS,
        created_at=now,
    )
    db.add_all([tx1, tx2, tx3])
    db.commit()

    signals = RiskService.evaluate_transaction_rules(db=db, transaction_id=tx3.id)
    assert any(s.rule_triggered == "STRUCTURING_PATTERN" for s in signals)
    struct_signal = next(s for s in signals if s.rule_triggered == "STRUCTURING_PATTERN")
    assert struct_signal.risk_level == RiskLevel.HIGH
    assert struct_signal.metadata_json["reason"] == "sub_2000_threshold_clustering"
    assert struct_signal.metadata_json["cluster_count"] >= 3


def test_evaluate_risk_rules_celery_task(db: Session, risk_env):
    """Verifies that the Celery task runs asynchronously and creates RiskSignals."""
    merchant_id = risk_env["merchant_id"]
    cust = Customer(
        merchant_id=merchant_id,
        name="Celery Risk Customer",
        phone=f"+9197{uuid.uuid4().int % 100000000:08d}",
    )
    db.add(cust)
    db.commit()
    customer_id = cust.id
    now = datetime.now(timezone.utc)

    # Trigger sub-2000 structuring
    for amt in ["1900.00", "1950.00", "1999.00"]:
        t = PaymentTransaction(
            merchant_id=merchant_id,
            customer_id=customer_id,
            idempotency_key=f"celery-risk-{uuid.uuid4().hex}",
            amount=Decimal(amt),
            currency="INR",
            payment_method=PaymentMethod.UPI_QR,
            status=TransactionStatus.SUCCESS,
            created_at=now,
        )
        db.add(t)
    db.commit()

    # Call task synchronously
    signal_ids = evaluate_risk_rules(transaction_id=str(t.id))
    assert len(signal_ids) >= 1
    assert any(
        db.query(RiskSignal).filter(RiskSignal.id == uuid.UUID(sid)).first() is not None
        for sid in signal_ids
    )


def test_list_merchant_risk_signals_and_filters(client: TestClient, db: Session, risk_env):
    """Verifies GET /merchants/{id}/risk/signals with severity & reviewed filters."""
    merchant_id = risk_env["merchant_id"]

    # Clear existing signals for clean test counts
    db.query(RiskSignal).filter(RiskSignal.merchant_id == merchant_id).delete()
    db.commit()

    # Seed 3 signals: 1 HIGH unreviewed, 1 MEDIUM unreviewed, 1 HIGH reviewed
    s1 = RiskSignal(
        merchant_id=merchant_id,
        risk_score=Decimal("80.00"),
        risk_level=RiskLevel.HIGH,
        rule_triggered="VELOCITY_SPIKE",
        action_taken=RiskAction.FLAG_FOR_REVIEW,
        is_reviewed=False,
    )
    s2 = RiskSignal(
        merchant_id=merchant_id,
        risk_score=Decimal("50.00"),
        risk_level=RiskLevel.MEDIUM,
        rule_triggered="ODD_HOUR",
        action_taken=RiskAction.FLAG_FOR_REVIEW,
        is_reviewed=False,
    )
    s3 = RiskSignal(
        merchant_id=merchant_id,
        risk_score=Decimal("85.00"),
        risk_level=RiskLevel.HIGH,
        rule_triggered="STRUCTURING_PATTERN",
        action_taken=RiskAction.ALLOW,
        is_reviewed=True,
        resolution_note="Legitimate customer volume verified",
    )
    db.add_all([s1, s2, s3])
    db.commit()

    headers = {"Authorization": f"Bearer {risk_env['owner']['token']}"}
    base_url = f"/api/v1/merchants/{merchant_id}/risk/signals"

    # 1. No filters: returns all 3
    r = client.get(base_url, headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 3

    # 2. Filter severity=HIGH: returns 2
    r_high = client.get(f"{base_url}?severity=HIGH", headers=headers)
    assert r_high.status_code == 200
    assert r_high.json()["total"] == 2
    assert all(item["risk_level"] == "HIGH" for item in r_high.json()["items"])

    # 3. Filter reviewed=false: returns 2
    r_unreviewed = client.get(f"{base_url}?reviewed=false", headers=headers)
    assert r_unreviewed.status_code == 200
    assert r_unreviewed.json()["total"] == 2
    assert all(item["is_reviewed"] is False for item in r_unreviewed.json()["items"])

    # 4. Filter reviewed=true: returns 1
    r_reviewed = client.get(f"{base_url}?reviewed=true", headers=headers)
    assert r_reviewed.status_code == 200
    assert r_reviewed.json()["total"] == 1
    assert r_reviewed.json()["items"][0]["is_reviewed"] is True

    # 5. Filter rule_triggered=ODD_HOUR: returns 1
    r_rule = client.get(f"{base_url}?rule_triggered=ODD_HOUR", headers=headers)
    assert r_rule.status_code == 200
    assert r_rule.json()["total"] == 1
    assert r_rule.json()["items"][0]["rule_triggered"] == "ODD_HOUR"

    # 6. Pagination check
    r_pag = client.get(f"{base_url}?page=1&page_size=2", headers=headers)
    assert r_pag.status_code == 200
    assert len(r_pag.json()["items"]) == 2
    assert r_pag.json()["total_pages"] == 2


def test_review_risk_signal_and_audit(client: TestClient, db: Session, risk_env):
    """Verifies PATCH /risk/signals/{id}/review records resolution and creates audit entry."""
    merchant_id = risk_env["merchant_id"]
    mgr_id = risk_env["manager"]["user_id"]

    signal = RiskSignal(
        merchant_id=merchant_id,
        risk_score=Decimal("85.00"),
        risk_level=RiskLevel.HIGH,
        rule_triggered="STRUCTURING_PATTERN",
        action_taken=RiskAction.FLAG_FOR_REVIEW,
        is_reviewed=False,
    )
    db.add(signal)
    db.commit()

    # Manager reviews signal
    res = client.patch(
        f"/api/v1/risk/signals/{signal.id}/review",
        headers={"Authorization": f"Bearer {risk_env['manager']['token']}"},
        json={
            "resolution_note": "Spoke with merchant: customer making separate bill payments for group dinner.",
            "action_taken": "ALLOW",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_reviewed"] is True
    assert data["resolution_note"] == "Spoke with merchant: customer making separate bill payments for group dinner."
    assert data["action_taken"] == "ALLOW"
    assert data["reviewed_by"] == str(mgr_id)
    assert data["reviewed_at"] is not None

    # Verify audit log entry was written
    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "risk_signals",
            AuditLog.entity_id == signal.id,
            AuditLog.action == AuditAction.STATUS_CHANGE,
        )
        .first()
    )
    assert audit is not None
    assert audit.user_id == mgr_id
    assert audit.changes["after"]["is_reviewed"] is True
    assert audit.changes["after"]["action_taken"] == "ALLOW"


def test_risk_rules_documentation_endpoint(client: TestClient):
    """Verifies GET /risk/rules returns auditable documentation for all active rules."""
    res = client.get("/api/v1/risk/rules")
    assert res.status_code == 200
    data = res.json()
    assert data["auditable"] is True
    rule_names = [r["rule_name"] for r in data["rules"]]
    assert "VELOCITY_SPIKE" in rule_names
    assert "ODD_HOUR" in rule_names
    assert "STRUCTURING_PATTERN" in rule_names
    assert "GEO_MISMATCH" in rule_names

    # Check GEO_MISMATCH omission rationale
    geo_rule = next(r for r in data["rules"] if r["rule_name"] == "GEO_MISMATCH")
    assert "Omitted" in geo_rule["description"]


def test_risk_signal_not_found_and_rbac_rejection(client: TestClient, db: Session, risk_env):
    """Verifies 404 for missing signal and 403 for unauthorized cashier review."""
    merchant_id = risk_env["merchant_id"]
    fake_id = uuid.uuid4()

    # 1. 404 Not Found
    res_404 = client.patch(
        f"/api/v1/risk/signals/{fake_id}/review",
        headers={"Authorization": f"Bearer {risk_env['owner']['token']}"},
        json={"resolution_note": "Testing not found"},
    )
    assert res_404.status_code == 404

    # 2. Seed a real signal
    signal = RiskSignal(
        merchant_id=merchant_id,
        risk_score=Decimal("80.00"),
        risk_level=RiskLevel.HIGH,
        rule_triggered="VELOCITY_SPIKE",
        action_taken=RiskAction.FLAG_FOR_REVIEW,
        is_reviewed=False,
    )
    db.add(signal)
    db.commit()

    # 3. Cashier CANNOT review (403 Forbidden)
    res_csh = client.patch(
        f"/api/v1/risk/signals/{signal.id}/review",
        headers={"Authorization": f"Bearer {risk_env['cashier']['token']}"},
        json={"resolution_note": "Cashier attempting to dismiss signal"},
    )
    assert res_csh.status_code == 403

    # 4. Unauthenticated request CANNOT review (401 Unauthorized)
    res_unauth = client.patch(
        f"/api/v1/risk/signals/{signal.id}/review",
        json={"resolution_note": "Unauthenticated note"},
    )
    assert res_unauth.status_code == 401

