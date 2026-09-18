"""Tests for the Analytics Module.

Covers:
  1. GET /merchants/{id}/analytics/overview:
     - Today, this-week, this-month collections and counts
     - Success rate %
     - Pending count
     - Average transaction value (ATV)
     - Unresolved duplicate flags count
  2. GET /merchants/{id}/analytics/revenue-trend:
     - Day granularity (fl_chart format with continuous dates, index, label, amount)
     - Week granularity
     - Month granularity
     - from & to date filters
  3. GET /merchants/{id}/analytics/payment-methods:
     - Breakdown by method and status
     - Method-level summary rollups
  4. Redis caching & invalidation:
     - 60s TTL cache on responses
     - Cache hit returns cached payload
     - Invalidated on new SUCCESS transaction
  5. RBAC & merchant scoping.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus
from app.modules.duplicate_detection.models import DuplicateFlagReason, DuplicateFlagStatus, DuplicateTransactionFlag
from app.modules.analytics.service import AnalyticsService


@pytest.fixture
def analytics_env(client: TestClient, db: Session):
    """Sets up owner, merchant, and auth token for testing."""
    owner_email = f"owner_analytics_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Analytics Owner",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
        },
    )
    assert reg.status_code == 201, reg.text
    owner_token = reg.json()["tokens"]["access_token"]

    mreg = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Analytics Store",
            "legal_name": "Analytics Store Pvt Ltd",
            "email": f"analytics_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "analyticsstore@icici",
        },
    )
    assert mreg.status_code == 201, mreg.text
    merchant_id = uuid.UUID(mreg.json()["id"])

    return {
        "owner_token": owner_token,
        "merchant_id": merchant_id,
    }


# ---------------------------------------------------------------------------
# 1. Analytics Overview Tests
# ---------------------------------------------------------------------------

def test_get_analytics_overview_empty(client: TestClient, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["merchant_id"] == str(merchant_id)
    assert Decimal(data["today_collections"]) == Decimal("0.00")
    assert Decimal(data["this_week_collections"]) == Decimal("0.00")
    assert Decimal(data["this_month_collections"]) == Decimal("0.00")
    assert data["today_transaction_count"] == 0
    assert data["success_rate"] == 100.0
    assert data["pending_count"] == 0
    assert Decimal(data["average_transaction_value"]) == Decimal("0.00")
    assert data["unresolved_duplicate_flags_count"] == 0


def test_get_analytics_overview_with_transactions(client: TestClient, db: Session, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]
    now = datetime.now(timezone.utc)

    # 1. Today SUCCESS transaction: 1000.00
    tx1 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"an-1-{uuid.uuid4().hex}",
        amount=Decimal("1000.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
        mock_scenario="SUCCESS",
        created_at=now,
    )
    # 2. Today SUCCESS transaction: 500.00
    tx2 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"an-2-{uuid.uuid4().hex}",
        amount=Decimal("500.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        status=TransactionStatus.SUCCESS,
        mock_scenario="SUCCESS",
        created_at=now - timedelta(minutes=30),
    )
    # 3. Today FAILED transaction
    tx3 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"an-3-{uuid.uuid4().hex}",
        amount=Decimal("300.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.FAILED,
        mock_scenario="FAIL",
        created_at=now - timedelta(hours=1),
    )
    # 4. PENDING transaction
    tx4 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"an-4-{uuid.uuid4().hex}",
        amount=Decimal("200.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        status=TransactionStatus.PENDING,
        created_at=now - timedelta(minutes=10),
    )
    db.add_all([tx1, tx2, tx3, tx4])
    db.flush()

    # 5. Add an open duplicate flag
    flag = DuplicateTransactionFlag(
        merchant_id=merchant_id,
        original_transaction_id=tx1.id,
        duplicate_transaction_id=tx2.id,
        flag_reason=DuplicateFlagReason.IDENTICAL_AMOUNT_AND_VPA,
        match_reason="Simulated duplicate test",
        status=DuplicateFlagStatus.SUSPECTED,
    )
    db.add(flag)
    db.commit()

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()

    # Total success amount = 1000 + 500 = 1500.00
    assert Decimal(data["today_collections"]) == Decimal("1500.00")
    assert Decimal(data["this_week_collections"]) >= Decimal("1500.00")
    assert Decimal(data["this_month_collections"]) >= Decimal("1500.00")
    assert data["today_transaction_count"] == 2
    # Success rate: 2 success / 3 terminal (2 success + 1 failed) = 66.67%
    assert abs(data["success_rate"] - 66.67) < 0.1
    # Pending count: 1
    assert data["pending_count"] == 1
    # ATV: 1500 / 2 = 750.00
    assert Decimal(data["average_transaction_value"]) == Decimal("750.00")
    # Duplicate flags: 1
    assert data["unresolved_duplicate_flags_count"] == 1


# ---------------------------------------------------------------------------
# 2. Revenue Trend Tests (fl_chart ready)
# ---------------------------------------------------------------------------

def test_get_revenue_trend_day_granularity(client: TestClient, db: Session, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]
    now = datetime.now(timezone.utc)
    today = now.date()

    # Add transactions on today and yesterday
    tx_today = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"rt-today-{uuid.uuid4().hex}",
        amount=Decimal("1250.50"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
        created_at=now,
    )
    tx_yesterday = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"rt-yest-{uuid.uuid4().hex}",
        amount=Decimal("800.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        status=TransactionStatus.SUCCESS,
        created_at=now - timedelta(days=1),
    )
    db.add_all([tx_today, tx_yesterday])
    db.commit()

    from_date = today - timedelta(days=6)
    to_date = today

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/revenue-trend",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "granularity": "day",
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["granularity"] == "day"
    assert data["from_date"] == from_date.isoformat()
    assert data["to_date"] == to_date.isoformat()
    assert Decimal(data["total_revenue"]) == Decimal("2050.50")
    assert data["total_transactions"] == 2

    # Should have 7 continuous points (from_date to to_date inclusive)
    points = data["points"]
    assert len(points) == 7

    # Verify points structure suitable for fl_chart
    for i, pt in enumerate(points):
        assert pt["index"] == i
        assert "period" in pt
        assert "label" in pt
        assert "amount" in pt
        assert "transaction_count" in pt

    # Last point (today) has 1250.50
    assert Decimal(points[-1]["amount"]) == Decimal("1250.50")
    assert points[-1]["transaction_count"] == 1

    # Second to last point (yesterday) has 800.00
    assert Decimal(points[-2]["amount"]) == Decimal("800.00")
    assert points[-2]["transaction_count"] == 1


def test_get_revenue_trend_week_and_month_granularity(client: TestClient, db: Session, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]

    # Week test
    resp_week = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/revenue-trend",
        headers={"Authorization": f"Bearer {token}"},
        params={"granularity": "week"},
    )
    assert resp_week.status_code == 200
    assert resp_week.json()["granularity"] == "week"
    assert len(resp_week.json()["points"]) > 0

    # Month test
    resp_month = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/revenue-trend",
        headers={"Authorization": f"Bearer {token}"},
        params={"granularity": "month"},
    )
    assert resp_month.status_code == 200
    assert resp_month.json()["granularity"] == "month"
    assert len(resp_month.json()["points"]) > 0


# ---------------------------------------------------------------------------
# 3. Payment Methods Breakdown Tests
# ---------------------------------------------------------------------------

def test_get_payment_methods_breakdown(client: TestClient, db: Session, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]
    now = datetime.now(timezone.utc)

    # 2 UPI_QR SUCCESS
    t1 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"pm-1-{uuid.uuid4().hex}",
        amount=Decimal("600.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
        created_at=now,
    )
    t2 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"pm-2-{uuid.uuid4().hex}",
        amount=Decimal("400.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
        created_at=now,
    )
    # 1 UPI_COLLECT FAILED
    t3 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"pm-3-{uuid.uuid4().hex}",
        amount=Decimal("200.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        status=TransactionStatus.FAILED,
        created_at=now,
    )
    db.add_all([t1, t2, t3])
    db.commit()

    resp = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/payment-methods",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_transactions"] == 3
    assert Decimal(data["total_volume"]) == Decimal("1200.00")

    # Check breakdown items
    breakdown = data["breakdown"]
    assert len(breakdown) >= 2

    # UPI_QR SUCCESS should be present
    qr_success = next(
        b for b in breakdown if b["payment_method"] == "UPI_QR" and b["status"] == "SUCCESS"
    )
    assert qr_success["count"] == 2
    assert Decimal(qr_success["total_amount"]) == Decimal("1000.00")

    # Check method summary
    summaries = data["methods_summary"]
    qr_sum = next(s for s in summaries if s["payment_method"] == "UPI_QR")
    assert qr_sum["total_count"] == 2
    assert Decimal(qr_sum["total_amount"]) == Decimal("1000.00")
    assert qr_sum["success_count"] == 2

    collect_sum = next(s for s in summaries if s["payment_method"] == "UPI_COLLECT")
    assert collect_sum["total_count"] == 1
    assert collect_sum["failed_count"] == 1


# ---------------------------------------------------------------------------
# 4. Redis Caching & Invalidation Tests
# ---------------------------------------------------------------------------

def test_analytics_redis_caching_and_invalidation(client: TestClient, db: Session, fake_redis, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]
    now = datetime.now(timezone.utc)

    # Initial transaction: 500.00
    tx1 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"cache-init-{uuid.uuid4().hex}",
        amount=Decimal("500.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
        created_at=now,
    )
    db.add(tx1)
    db.commit()

    # 1. First GET: populates cache
    resp1 = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 200
    assert Decimal(resp1.json()["today_collections"]) == Decimal("500.00")

    # Verify Redis has keys for this merchant
    cached_keys = list(fake_redis.keys(f"payflow:analytics:{merchant_id}:*"))
    assert len(cached_keys) > 0, "Analytics response should be stored in Redis"

    # 2. Add another transaction directly in DB without invalidating yet
    tx2 = PaymentTransaction(
        merchant_id=merchant_id,
        idempotency_key=f"cache-second-{uuid.uuid4().hex}",
        amount=Decimal("300.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_QR,
        status=TransactionStatus.SUCCESS,
        created_at=now,
    )
    db.add(tx2)
    db.commit()

    # GET again: should return CACHED value (500.00, not 800.00)
    resp2 = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200
    assert Decimal(resp2.json()["today_collections"]) == Decimal("500.00"), "Cache hit should return previous 500.00"

    # 3. Call invalidate_cache (or simulate new transaction via PaymentService)
    AnalyticsService.invalidate_cache(merchant_id=merchant_id)

    # Verify Redis keys cleared
    post_invalidation_keys = list(fake_redis.keys(f"payflow:analytics:{merchant_id}:*"))
    assert len(post_invalidation_keys) == 0, "Cache keys should be purged upon invalidation"

    # 4. Third GET: fresh data (500 + 300 = 800.00)
    resp3 = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp3.status_code == 200
    assert Decimal(resp3.json()["today_collections"]) == Decimal("800.00"), "Fresh fetch after invalidation should return 800.00"


# ---------------------------------------------------------------------------
# 5. RBAC Enforcement Tests
# ---------------------------------------------------------------------------

def test_analytics_requires_authentication(client: TestClient, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    resp = client.get(f"/api/v1/merchants/{merchant_id}/analytics/overview")
    assert resp.status_code in (401, 403)


def test_cache_invalidation_triggered_by_payment_service_on_success(client: TestClient, db: Session, fake_redis, analytics_env):
    merchant_id = analytics_env["merchant_id"]
    token = analytics_env["owner_token"]

    # 1. First fetch overview -> populates cache
    resp1 = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 200
    assert Decimal(resp1.json()["today_collections"]) == Decimal("0.00")
    assert len(list(fake_redis.keys(f"payflow:analytics:{merchant_id}:*"))) > 0

    # 2. Initiate payment that reaches SUCCESS via PaymentService
    from app.modules.payments.service import PaymentService
    from app.modules.payments.schemas import InitiatePaymentRequest
    from app.modules.mock_upi_provider.schemas import MockScenario

    req = InitiatePaymentRequest(
        merchant_id=merchant_id,
        amount=Decimal("450.00"),
        currency="INR",
        payment_method=PaymentMethod.UPI_COLLECT,
        payer_vpa="testpayer@upi",
        scenario=MockScenario.SUCCESS,
    )
    PaymentService.initiate_payment(
        db=db,
        payload=req,
        idempotency_key=f"inv-test-{uuid.uuid4().hex}",
    )

    # 3. Cache keys must be automatically purged by PaymentService
    remaining_keys = list(fake_redis.keys(f"payflow:analytics:{merchant_id}:*"))
    assert len(remaining_keys) == 0, "PaymentService should automatically invalidate analytics cache on SUCCESS"

    # 4. Next fetch returns fresh updated data (450.00)
    resp2 = client.get(
        f"/api/v1/merchants/{merchant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200
    assert Decimal(resp2.json()["today_collections"]) == Decimal("450.00")

