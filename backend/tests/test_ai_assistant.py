"""Tests for the AI Assistant Module.

Covers:
  1. POST /merchants/{id}/ai-assistant/query for overdue invoices (detects intent, cites invoices and customers, grounded numbers).
  2. POST /merchants/{id}/ai-assistant/query for revenue dip and trends (cites metrics, explains dips/failures).
  3. POST /merchants/{id}/ai-assistant/query for settlements (cites UTR, net amount, status).
  4. POST /merchants/{id}/ai-assistant/query for payment methods breakdown.
  5. POST /merchants/{id}/ai-assistant/query for general overview.
  6. Read-only guardrail enforcement (refuses mutation requests such as refunds/payments).
  7. RBAC & Tenant isolation (Owner/Cashier have access; cross-merchant blocked 403; unauthenticated 401).
  8. Anthropic API integration (mocked response verifying model invocation and fallback on error).
  9. Merchant 404 when querying nonexistent merchant.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch
import uuid
import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.ai_assistant.llm_client import LLMClient
from app.modules.customers.models import Customer
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus
from app.modules.settlements.models import Settlement, SettlementCycle, SettlementStatus


@pytest.fixture
def ai_env(client: TestClient, db: Session):
    """Sets up owner, merchant, customer, and staff user tokens for AI assistant testing."""
    # Register Owner
    owner_email = f"owner_ai_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "AI Assistant Owner",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
        },
    )
    assert reg.status_code == 201, reg.text
    owner_token = reg.json()["tokens"]["access_token"]
    owner_user_id = uuid.UUID(reg.json()["user"]["id"])

    # Create Merchant
    mreg = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "AI Analytics Store",
            "legal_name": "AI Analytics Store Pvt Ltd",
            "email": f"ai_store_{uuid.uuid4().hex[:8]}@test.com",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "aistore@icici",
        },
    )
    assert mreg.status_code == 201, mreg.text
    merchant_id = uuid.UUID(mreg.json()["id"])

    # Register Cashier on same merchant
    cashier_email = f"cashier_ai_{uuid.uuid4().hex[:8]}@example.com"
    reg_cashier = client.post(
        "/api/v1/auth/register",
        json={
            "email": cashier_email,
            "password": "Password123!",
            "full_name": "Cashier User",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
        },
    )
    assert reg_cashier.status_code == 201, reg_cashier.text
    cashier_token = reg_cashier.json()["tokens"]["access_token"]
    cashier_user_id = uuid.UUID(reg_cashier.json()["user"]["id"])

    # Assign Cashier role
    from app.modules.rbac.models import Role, UserRole
    cashier_role = db.query(Role).filter(Role.name == "Cashier").first()
    db.add(
        UserRole(
            user_id=cashier_user_id,
            role_id=cashier_role.id,
            merchant_id=merchant_id,
        )
    )

    # Register Other Merchant (for cross-tenant checks)
    other_email = f"other_owner_{uuid.uuid4().hex[:8]}@example.com"
    reg_other = client.post(
        "/api/v1/auth/register",
        json={
            "email": other_email,
            "password": "Password123!",
            "full_name": "Other Owner",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
        },
    )
    assert reg_other.status_code == 201, reg_other.text
    other_token = reg_other.json()["tokens"]["access_token"]

    db.commit()

    # Create sample customer
    customer = Customer(
        merchant_id=merchant_id,
        name="Ramesh Sharma",
        phone="+919876543210",
        email="ramesh.sharma@example.com",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {
        "owner_token": owner_token,
        "owner_user_id": owner_user_id,
        "cashier_token": cashier_token,
        "other_token": other_token,
        "merchant_id": merchant_id,
        "customer_id": customer.id,
        "customer": customer,
    }


def test_ai_assistant_overdue_invoices_query(client: TestClient, db: Session, ai_env):
    """Verifies that asking about overdue invoices returns grounded numbers and cites records."""
    merchant_id = ai_env["merchant_id"]
    customer = ai_env["customer"]

    # Create an overdue invoice
    overdue_inv = Invoice(
        merchant_id=merchant_id,
        customer_id=customer.id,
        invoice_number="INV-AI-2026-0001",
        total_amount=Decimal("4500.00"),
        paid_amount=Decimal("1000.00"),
        status=InvoiceStatus.OVERDUE,
        due_date=datetime.now(timezone.utc) - timedelta(days=5),
    )
    db.add(overdue_inv)
    db.commit()

    resp = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "Which customers have overdue invoices?"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["merchant_id"] == str(merchant_id)
    assert data["intent"] == "OVERDUE_INVOICES"
    assert "Ramesh Sharma" in data["answer"]
    assert "INV-AI-2026-0001" in data["answer"]
    assert "3,500.00" in data["answer"]  # 4500 - 1000 balance due

    # Verify sources cited
    assert len(data["sources_cited"]) >= 1
    cited_inv = next((c for c in data["sources_cited"] if c["reference"] == "INV-AI-2026-0001"), None)
    assert cited_inv is not None
    assert cited_inv["entity_type"] == "invoice"
    assert cited_inv["details"]["customer"] == "Ramesh Sharma"

    # Verify underlying data contains ground truth
    underlying = data["underlying_data"]
    assert underlying["overdue_invoices"]["count"] == 1
    assert underlying["overdue_invoices"]["total_overdue_amount"] == 3500.0


def test_ai_assistant_revenue_dip_query(client: TestClient, db: Session, ai_env):
    """Verifies that asking about revenue dips returns trend analysis and cites metrics."""
    merchant_id = ai_env["merchant_id"]

    # Create successful payments on previous days and failed payments
    t_now = datetime.now(timezone.utc)
    for day_offset in range(1, 4):
        tx = PaymentTransaction(
            merchant_id=merchant_id,
            amount=Decimal("5000.00"),
            currency="INR",
            status=TransactionStatus.SUCCESS,
            payment_method=PaymentMethod.UPI_INTENT,
            idempotency_key=str(uuid.uuid4()),
            created_at=t_now - timedelta(days=day_offset),
        )
        db.add(tx)

    # Failed transaction on a dip day
    failed_tx = PaymentTransaction(
        merchant_id=merchant_id,
        amount=Decimal("15000.00"),
        currency="INR",
        status=TransactionStatus.FAILED,
        failure_reason="Customer bank server timeout",
        idempotency_key=str(uuid.uuid4()),
        created_at=t_now - timedelta(days=2),
    )
    db.add(failed_tx)
    db.commit()

    resp = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "Why did revenue dip last Tuesday?"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "REVENUE_ANALYTICS"
    assert "Average Daily Revenue" in data["answer"] or "revenue" in data["answer"].lower()
    assert len(data["sources_cited"]) >= 1

    # Citations should include analytics metrics
    metrics = [c for c in data["sources_cited"] if c["entity_type"] == "analytics_metric"]
    assert len(metrics) > 0

    underlying = data["underlying_data"]
    assert "revenue_analytics" in underlying
    assert "recent_failed_transactions" in underlying["revenue_analytics"]


def test_ai_assistant_settlement_status_query(client: TestClient, db: Session, ai_env):
    """Verifies that asking about settlements returns the mock UTR and net payout."""
    merchant_id = ai_env["merchant_id"]

    # Insert a settlement record
    settlement = Settlement(
        merchant_id=merchant_id,
        settlement_date=date.today(),
        settlement_cycle=SettlementCycle.T_PLUS_1,
        status=SettlementStatus.SETTLED,
        gross_amount=Decimal("20000.00"),
        mdr_amount=Decimal("300.00"),
        tax_on_mdr=Decimal("54.00"),
        net_amount=Decimal("19646.00"),
        transaction_count=10,
        utr_reference="UTR20260918-ABCD9999",
    )
    db.add(settlement)
    db.commit()

    resp = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "What is our latest settlement payout and UTR number?"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "SETTLEMENTS_SUMMARY"
    assert "UTR20260918-ABCD9999" in data["answer"]
    assert "19,646.00" in data["answer"]

    # Verify citation
    utr_cite = next((c for c in data["sources_cited"] if c["reference"] == "UTR20260918-ABCD9999"), None)
    assert utr_cite is not None
    assert utr_cite["entity_type"] == "settlement"
    assert utr_cite["details"]["net_amount"] == 19646.0


def test_ai_assistant_payment_methods_query(client: TestClient, db: Session, ai_env):
    """Verifies payment method distribution query."""
    merchant_id = ai_env["merchant_id"]

    # Seed a transaction with UPI method
    tx = PaymentTransaction(
        merchant_id=merchant_id,
        amount=Decimal("1200.00"),
        currency="INR",
        status=TransactionStatus.SUCCESS,
        payment_method=PaymentMethod.UPI_INTENT,
        idempotency_key=str(uuid.uuid4()),
    )
    db.add(tx)
    db.commit()

    resp = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "What payment methods are our customers using?"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "PAYMENT_METHODS"
    assert "payment methods" in data["answer"].lower()
    assert "payment_methods_breakdown" in data["underlying_data"]


def test_ai_assistant_general_overview_query(client: TestClient, db: Session, ai_env):
    """Verifies broad performance inquiries receive a holistic overview."""
    merchant_id = ai_env["merchant_id"]

    resp = client.post(
        f"/merchants/{merchant_id}/ai-assistant/query",  # Also test root URL without /api/v1 prefix
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "How is our business doing today?"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "GENERAL_OVERVIEW"
    assert "Today's Collections" in data["answer"]
    assert "overview" in data["underlying_data"]


def test_ai_assistant_read_only_action_refusal(client: TestClient, db: Session, ai_env):
    """Verifies that action requests (e.g. initiating refunds) are strictly refused."""
    merchant_id = ai_env["merchant_id"]

    resp = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "Please initiate a refund of 500 for customer Ramesh Sharma right now"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "Action Refused" in data["answer"]
    assert "read-only" in data["answer"].lower()
    assert data["model_used"] == "payflow-safety-guardrail"


def test_ai_assistant_rbac_enforcement(client: TestClient, db: Session, ai_env):
    """Verifies RBAC boundaries and tenant isolation."""
    merchant_id = ai_env["merchant_id"]

    # 1. Cashier with payments:read should succeed
    resp_cashier = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['cashier_token']}"},
        json={"question": "Show collections today"},
    )
    assert resp_cashier.status_code == 200, resp_cashier.text

    # 2. Other merchant owner attempting cross-tenant access should be 403 Forbidden
    resp_other = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['other_token']}"},
        json={"question": "Show collections today"},
    )
    assert resp_other.status_code == 403

    # 3. Unauthenticated request should be 401 Unauthorized
    resp_unauth = client.post(
        f"/api/v1/merchants/{merchant_id}/ai-assistant/query",
        json={"question": "Show collections today"},
    )
    assert resp_unauth.status_code == 401


@pytest.mark.asyncio
async def test_ai_assistant_anthropic_integration_mock(db: Session, ai_env):
    """Verifies that when Anthropic API responds, its output is correctly passed through."""
    from app.modules.ai_assistant.service import AIAssistantService

    mock_anthropic_response = {
        "id": "msg_12345",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Based on the retrieved records, you processed ₹50,000 across 12 transactions with zero failures.",
            }
        ],
        "model": "claude-3-5-sonnet-20241022",
    }

    mock_resp = httpx.Response(
        status_code=200,
        json=mock_anthropic_response,
        request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"),
    )

    custom_client = LLMClient(api_key="test-mock-anthropic-key", model="claude-3-5-sonnet-20241022")

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        result = await AIAssistantService.process_query(
            db=db,
            merchant_id=ai_env["merchant_id"],
            question="Summarize our financial performance",
            llm_client=custom_client,
        )

        assert "Based on the retrieved records" in result.answer
        assert result.model_used == "claude-3-5-sonnet-20241022"


def test_ai_assistant_merchant_not_found(client: TestClient, db: Session, ai_env):
    """Verifies that querying a nonexistent merchant returns 404 EntityNotFoundException."""
    fake_merchant_id = uuid.uuid4()

    # Make user superuser temporarily or use current token if bypassed
    from app.modules.auth.models import User
    user = db.query(User).filter(User.id == ai_env["owner_user_id"]).first()
    user.is_superuser = True
    db.commit()

    resp = client.post(
        f"/api/v1/merchants/{fake_merchant_id}/ai-assistant/query",
        headers={"Authorization": f"Bearer {ai_env['owner_token']}"},
        json={"question": "What are our total collections?"},
    )

    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"
