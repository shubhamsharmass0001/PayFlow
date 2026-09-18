"""Tests for the Settlements Module.

Covers:
  1.  create_from_matched_batch: creates Settlement + SettlementLineItems from a MATCHED batch
  2.  Idempotency: calling create_from_matched_batch twice returns the same Settlement
  3.  Skips non-MATCHED batches (DISCREPANCIES_FOUND, COMPLETED)
  4.  Skips batches with no MATCHED entries
  5.  MDR / tax / net computation correctness (illustrative mock values)
  6.  Mock UTR reference format
  7.  GET /merchants/{id}/settlements: list with date-range + status filters
  8.  GET /merchants/{id}/settlements: chart series pre-aggregation
  9.  GET /merchants/{id}/settlements: window totals
  10. GET /settlements/{id}: detail with line items
  11. GET /settlements/{id}: 404 for unknown settlement
  12. RBAC: settlements:read required for both endpoints
  13. Nightly Celery sweep sentinel creates settlements for unsettled MATCHED batches
  14. Settlement created inline after reconciliation run (integration path)
"""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus
from app.modules.reconciliation.models import (
    MatchStatus,
    ReconciliationBatch,
    ReconciliationEntry,
    ReconciliationEntryStatus,
    ReconciliationStatus,
)
from app.modules.settlements.models import Settlement, SettlementCycle, SettlementLineItem, SettlementStatus
from app.modules.settlements.service import SettlementService
from app.modules.settlements.tasks import create_settlement_from_batch


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_matched_batch(
    db: Session,
    merchant_id: uuid.UUID,
    tx_amounts: list[Decimal],
    batch_date: date | None = None,
) -> tuple[ReconciliationBatch, list[PaymentTransaction]]:
    """Creates a MATCHED ReconciliationBatch with child entries backed by real transactions."""
    if batch_date is None:
        batch_date = date.today()

    now = datetime.now(timezone.utc)
    txs = []
    for amt in tx_amounts:
        tx = PaymentTransaction(
            merchant_id=merchant_id,
            idempotency_key=f"sett-tx-{uuid.uuid4().hex}",
            amount=amt,
            currency="INR",
            status=TransactionStatus.SUCCESS,
            mock_scenario="SUCCESS",
        )
        db.add(tx)
        db.flush()
        txs.append(tx)

    mdr_rate = Decimal("0.015")
    batch = ReconciliationBatch(
        merchant_id=merchant_id,
        batch_date=batch_date,
        period_start=now - timedelta(hours=24),
        period_end=now,
        mdr_rate=mdr_rate,
        status=ReconciliationStatus.MATCHED,
        total_records=len(txs),
        matched_records=len(txs),
        mismatched_records=0,
        discrepancy_count=0,
    )
    db.add(batch)
    db.flush()

    for tx in txs:
        expected_net = (tx.amount * (Decimal("1") - mdr_rate)).quantize(Decimal("0.01"))
        entry = ReconciliationEntry(
            batch_id=batch.id,
            transaction_id=tx.id,
            provider_ref_id="MOCK-REF",
            expected_amount=expected_net,
            actual_amount=expected_net,
            match_status=MatchStatus.MATCHED,
            status=ReconciliationEntryStatus.MATCHED,
        )
        db.add(entry)

    db.commit()
    db.refresh(batch)
    return batch, txs


# ---------------------------------------------------------------------------
# Shared fixture: owner, merchant
# ---------------------------------------------------------------------------

@pytest.fixture
def sett_env(client: TestClient, db: Session):
    owner_email = f"settowner_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Settlement Owner",
            "phone": f"+9197{uuid.uuid4().int % 100000000:08d}",
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]

    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Settlement Store",
            "legal_name": "Settlement Store Pvt Ltd",
            "email": f"sett_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "settstore@icici",
        },
    )
    merchant_id = uuid.UUID(m_resp.json()["id"])
    return {"owner_token": owner_token, "merchant_id": merchant_id}


# ---------------------------------------------------------------------------
# 1. create_from_matched_batch: basic creation
# ---------------------------------------------------------------------------

def test_create_from_matched_batch_creates_settlement_and_line_items(db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    tx_amounts = [Decimal("1000.00"), Decimal("500.00"), Decimal("250.00")]
    batch, txs = _make_matched_batch(db, merchant_id, tx_amounts)

    settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)

    assert settlement is not None
    assert settlement.merchant_id == merchant_id
    assert settlement.reconciliation_batch_id == batch.id
    assert settlement.status == SettlementStatus.SETTLED
    assert settlement.transaction_count == 3

    # Verify gross = sum of transaction amounts
    expected_gross = sum(tx_amounts)
    assert settlement.gross_amount == expected_gross

    # Verify net = gross - mdr - tax
    mdr_rate = Decimal("0.015")
    gst_rate = Decimal("0.18")
    expected_mdr = sum(
        (amt * mdr_rate).quantize(Decimal("0.01")) for amt in tx_amounts
    )
    expected_tax = sum(
        ((amt * mdr_rate).quantize(Decimal("0.01")) * gst_rate).quantize(Decimal("0.01"))
        for amt in tx_amounts
    )
    expected_net = expected_gross - expected_mdr - expected_tax
    assert settlement.net_amount == expected_net.quantize(Decimal("0.01"))

    # Line items exist
    db.refresh(settlement)
    assert len(settlement.line_items) == 3


# ---------------------------------------------------------------------------
# 2. Idempotency: calling twice returns same settlement
# ---------------------------------------------------------------------------

def test_create_from_matched_batch_is_idempotent(db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("800.00")])

    s1 = SettlementService.create_from_matched_batch(db=db, batch=batch)
    s2 = SettlementService.create_from_matched_batch(db=db, batch=batch)

    assert s1 is not None
    assert s2 is not None
    assert s1.id == s2.id  # Same row returned


# ---------------------------------------------------------------------------
# 3. Skips non-MATCHED batches
# ---------------------------------------------------------------------------

def test_create_from_matched_batch_skips_discrepancy_batch(db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("300.00")])

    # Force non-MATCHED status
    batch.status = ReconciliationStatus.DISCREPANCIES_FOUND
    db.commit()

    result = SettlementService.create_from_matched_batch(db=db, batch=batch)
    assert result is None


def test_create_from_matched_batch_skips_completed_batch(db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("200.00")])
    batch.status = ReconciliationStatus.COMPLETED
    db.commit()

    result = SettlementService.create_from_matched_batch(db=db, batch=batch)
    assert result is None


# ---------------------------------------------------------------------------
# 4. Skips batch with no MATCHED entries
# ---------------------------------------------------------------------------

def test_create_from_matched_batch_skips_empty_entries(db: Session, sett_env):
    """A MATCHED batch with no MATCHED child entries produces no settlement."""
    merchant_id = sett_env["merchant_id"]
    now = datetime.now(timezone.utc)

    batch = ReconciliationBatch(
        merchant_id=merchant_id,
        batch_date=date.today(),
        period_start=now - timedelta(hours=24),
        period_end=now,
        mdr_rate=Decimal("0.015"),
        status=ReconciliationStatus.MATCHED,
        total_records=0,
        matched_records=0,
        mismatched_records=0,
        discrepancy_count=0,
    )
    db.add(batch)
    db.commit()

    result = SettlementService.create_from_matched_batch(db=db, batch=batch)
    assert result is None


# ---------------------------------------------------------------------------
# 5. MDR / tax computation
# ---------------------------------------------------------------------------

def test_mdr_and_tax_per_transaction_computed_correctly(db: Session, sett_env):
    """Per-line-item fee / tax must match the illustrative mock formula."""
    merchant_id = sett_env["merchant_id"]
    batch, txs = _make_matched_batch(db, merchant_id, [Decimal("2000.00")])
    settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)
    db.refresh(settlement)

    # For amount = 2000, mdr=1.5%, gst=18% on mdr
    mdr = (Decimal("2000") * Decimal("0.015")).quantize(Decimal("0.01"))  # 30.00
    tax = (mdr * Decimal("0.18")).quantize(Decimal("0.01"))               # 5.40
    net = Decimal("2000") - mdr - tax                                     # 1964.60

    li = settlement.line_items[0]
    assert li.fee_amount == mdr
    assert li.tax_amount == tax
    assert li.net_amount == net


# ---------------------------------------------------------------------------
# 6. Mock UTR format
# ---------------------------------------------------------------------------

def test_utr_reference_format(db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("500.00")])
    settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)

    assert settlement.utr_reference is not None
    # Format: UTR{YYYYMMDD}-{8 hex chars uppercase}
    assert settlement.utr_reference.startswith("UTR")
    parts = settlement.utr_reference.split("-")
    assert len(parts) == 2
    assert len(parts[1]) == 8
    assert parts[1] == parts[1].upper()


# ---------------------------------------------------------------------------
# 7. GET /merchants/{id}/settlements: list with filters
# ---------------------------------------------------------------------------

def test_list_settlements_returns_correct_merchant_data(client: TestClient, db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    # Create two settlements on different dates
    batch1, _ = _make_matched_batch(db, merchant_id, [Decimal("1000.00")], date(2026, 9, 1))
    batch2, _ = _make_matched_batch(db, merchant_id, [Decimal("2000.00")], date(2026, 9, 2))
    SettlementService.create_from_matched_batch(db=db, batch=batch1)
    SettlementService.create_from_matched_batch(db=db, batch=batch2)

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/settlements",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 2

    # All items belong to the correct merchant
    for item in body["items"]:
        assert item["merchant_id"] == str(merchant_id)


def test_list_settlements_date_range_filter(client: TestClient, db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    batch_in, _ = _make_matched_batch(db, merchant_id, [Decimal("600.00")], date(2026, 8, 15))
    batch_out, _ = _make_matched_batch(db, merchant_id, [Decimal("400.00")], date(2026, 7, 1))
    SettlementService.create_from_matched_batch(db=db, batch=batch_in)
    SettlementService.create_from_matched_batch(db=db, batch=batch_out)

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/settlements?from_date=2026-08-01&to_date=2026-08-31",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert item["settlement_date"] >= "2026-08-01"
        assert item["settlement_date"] <= "2026-08-31"


def test_list_settlements_status_filter(client: TestClient, db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("300.00")])
    SettlementService.create_from_matched_batch(db=db, batch=batch)

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/settlements?status=SETTLED",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["status"] == "SETTLED"


# ---------------------------------------------------------------------------
# 8. Chart series pre-aggregation
# ---------------------------------------------------------------------------

def test_list_settlements_chart_series_pre_aggregated(client: TestClient, db: Session, sett_env):
    """The `series` field must contain one entry per settlement_date with correct sums."""
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    target_date = date(2026, 9, 10)
    # Two settlements on the same date
    batch_a, _ = _make_matched_batch(db, merchant_id, [Decimal("1000.00")], target_date)
    batch_b, _ = _make_matched_batch(db, merchant_id, [Decimal("500.00")], target_date)
    s_a = SettlementService.create_from_matched_batch(db=db, batch=batch_a)
    s_b = SettlementService.create_from_matched_batch(db=db, batch=batch_b)

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/settlements?from_date=2026-09-10&to_date=2026-09-10",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    body = resp.json()
    series = body["series"]

    # Should have exactly one point for 2026-09-10
    date_points = [p for p in series if p["settlement_date"] == "2026-09-10"]
    assert len(date_points) == 1

    pt = date_points[0]
    expected_gross = s_a.gross_amount + s_b.gross_amount
    assert Decimal(pt["gross_amount"]) == expected_gross
    assert pt["transaction_count"] == 2


# ---------------------------------------------------------------------------
# 9. Window totals
# ---------------------------------------------------------------------------

def test_list_settlements_window_totals(client: TestClient, db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("1000.00"), Decimal("2000.00")])
    settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/settlements",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    body = resp.json()
    # window_gross must be ≥ settlement's gross_amount
    assert Decimal(body["window_gross"]) >= settlement.gross_amount
    assert Decimal(body["window_net"]) >= settlement.net_amount
    assert body["window_transaction_count"] >= 2


# ---------------------------------------------------------------------------
# 10. GET /settlements/{id}: detail with line items
# ---------------------------------------------------------------------------

def test_get_settlement_detail_includes_line_items(client: TestClient, db: Session, sett_env):
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("500.00"), Decimal("300.00")])
    settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)

    resp = client.get(
        f"/api/v1/settlements/{settlement.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(settlement.id)
    assert len(body["line_items"]) == 2

    # Each line item has correct fields
    for li in body["line_items"]:
        assert "amount" in li
        assert "fee_amount" in li
        assert "tax_amount" in li
        assert "net_amount" in li
        # net_amount = amount - fee_amount - tax_amount
        computed_net = Decimal(li["amount"]) - Decimal(li["fee_amount"]) - Decimal(li["tax_amount"])
        assert Decimal(li["net_amount"]) == computed_net


# ---------------------------------------------------------------------------
# 11. 404 for unknown settlement
# ---------------------------------------------------------------------------

def test_get_settlement_not_found(client: TestClient, sett_env):
    resp = client.get(
        f"/api/v1/settlements/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {sett_env['owner_token']}"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 12. RBAC enforcement
# ---------------------------------------------------------------------------

def test_settlements_require_authentication(client: TestClient, sett_env):
    resp = client.get(f"/api/v1/merchants/{sett_env['merchant_id']}/settlements")
    assert resp.status_code in (401, 403)


def test_settlements_cashier_can_read(client: TestClient, db: Session, sett_env):
    """Cashier has settlements:read so they can view — but not write."""
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    # Register cashier
    creg = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"cashier_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Password123!",
            "full_name": "Sett Cashier",
            "phone": f"+9191{uuid.uuid4().int % 100000000:08d}",
        },
    )
    cashier_token = creg.json()["tokens"]["access_token"]
    cashier_id = creg.json()["user"]["id"]

    client.post(
        f"/api/v1/merchants/{merchant_id}/staff",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"user_id": cashier_id, "role_name": "Cashier"},
    )

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/settlements",
        headers={"Authorization": f"Bearer {cashier_token}"},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 13. Celery task: nightly sweep sentinel
# ---------------------------------------------------------------------------

def test_nightly_sweep_creates_settlement_for_unsettled_matched_batch(db: Session, sett_env):
    """The __nightly_sweep__ sentinel fans out to all unsettled MATCHED batches."""
    merchant_id = sett_env["merchant_id"]
    batch, _ = _make_matched_batch(db, merchant_id, [Decimal("750.00")])

    # Confirm no settlement exists yet
    existing = db.query(Settlement).filter(
        Settlement.reconciliation_batch_id == batch.id
    ).first()
    assert existing is None

    # Run nightly sweep
    result = create_settlement_from_batch("__nightly_sweep__")
    assert result["status"] == "nightly_sweep_complete"

    # Settlement should now exist
    db.expire_all()
    settlement = db.query(Settlement).filter(
        Settlement.reconciliation_batch_id == batch.id
    ).first()
    assert settlement is not None
    assert settlement.status == SettlementStatus.SETTLED


# ---------------------------------------------------------------------------
# 14. Integration: reconciliation run triggers settlement inline
# ---------------------------------------------------------------------------

def test_reconciliation_matched_batch_triggers_settlement(
    client: TestClient, db: Session, sett_env
):
    """When reconciliation produces a MATCHED batch, a settlement is created
    automatically via the inline task dispatch in ReconciliationService."""
    merchant_id = sett_env["merchant_id"]
    owner_token = sett_env["owner_token"]

    # Create a SUCCESS transaction in the reconciliation window
    now = datetime.now(timezone.utc)
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"recon-inline-{uuid.uuid4().hex}",
        amount=Decimal("1200.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        status=TransactionStatus.SUCCESS,
        mock_scenario="SUCCESS",
        created_at=now,
    )
    db.add(tx)
    db.commit()

    # Pre-existing settlement record matching 1.5% MDR: 1200 - 18 = 1182
    settlement_init = Settlement(
        merchant_id=merchant_id,
        settlement_cycle=SettlementCycle.T_PLUS_1,
        gross_amount=Decimal("1200.00"),
        deduction_amount=Decimal("18.00"),
        net_amount=Decimal("1182.00"),
        status=SettlementStatus.SETTLED,
        bank_account_ref="ACC_INIT",
    )
    db.add(settlement_init)
    db.flush()

    line_item = SettlementLineItem(
        settlement_id=settlement_init.id,
        transaction_id=tx.id,
        amount=Decimal("1200.00"),
        fee_amount=Decimal("18.00"),
        tax_amount=Decimal("0.00"),
        net_amount=Decimal("1182.00"),
    )
    db.add(line_item)
    db.commit()

    # Run reconciliation via API — uses the same window so tx is included
    recon_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/reconciliation/run",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "period_start": (now - timedelta(minutes=5)).isoformat(),
            "period_end": (now + timedelta(minutes=5)).isoformat(),
            "mdr_rate": 0.015,
            "tolerance": 0.05,
        },
    )
    assert recon_resp.status_code == 201
    batch_id = recon_resp.json()["id"]
    batch_status = recon_resp.json()["status"]

    assert batch_status == "MATCHED"
    db.expire_all()
    settlement = db.query(Settlement).filter(
        Settlement.reconciliation_batch_id == uuid.UUID(batch_id)
    ).first()
    assert settlement is not None, "Settlement should be created automatically after MATCHED batch"
    assert settlement.gross_amount >= Decimal("1200.00")
