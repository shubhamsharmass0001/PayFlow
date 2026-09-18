import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_password_hash
from app.modules.merchants.models import KycStatus, Merchant, RiskTier
from app.modules.rbac.models import Role, UserRole
from app.modules.rbac.seed import seed_rbac_data


@pytest.fixture
def rbac_setup(db: Session):
    """Sets up seeded roles, permissions, a test merchant, and helper accounts."""
    roles = seed_rbac_data(db)

    # Create Merchant
    merchant = Merchant(
        business_name="Test Store Mart",
        legal_name="Test Store Retail Pvt Ltd",
        email=f"merchant_{uuid.uuid4().hex[:8]}@example.com",
        phone="+919800011111",
        kyc_status=KycStatus.APPROVED,
        risk_tier=RiskTier.LOW,
    )
    db.add(merchant)
    db.flush()

    # Create Cashier User
    cashier = User(
        email=f"cashier_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("CashierPass123!"),
        full_name="Cashier John",
        is_active=True,
    )
    db.add(cashier)
    db.flush()

    # Create Manager User
    manager = User(
        email=f"manager_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("ManagerPass123!"),
        full_name="Manager Alice",
        is_active=True,
    )
    db.add(manager)
    db.flush()

    # Assign Cashier role scoped to merchant
    db.add(
        UserRole(
            user_id=cashier.id,
            role_id=roles["Cashier"].id,
            merchant_id=merchant.id,
        )
    )

    # Assign Manager role scoped to merchant
    db.add(
        UserRole(
            user_id=manager.id,
            role_id=roles["Manager"].id,
            merchant_id=merchant.id,
        )
    )

    db.commit()
    db.refresh(merchant)
    db.refresh(cashier)
    db.refresh(manager)

    return {
        "merchant": merchant,
        "cashier": cashier,
        "manager": manager,
    }


def test_rbac_authorized_access(client: TestClient, rbac_setup):
    """Cashier has 'invoices:read' permission, should succeed with 200."""
    cashier = rbac_setup["cashier"]
    merchant = rbac_setup["merchant"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": cashier.email, "password": "CashierPass123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    resp = client.get(
        f"/api/v1/rbac/merchants/{merchant.id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "success"


def test_rbac_permission_denied(client: TestClient, rbac_setup):
    """Cashier lacks 'refunds:write' permission, should fail with 403 Forbidden and standard error envelope."""
    cashier = rbac_setup["cashier"]
    merchant = rbac_setup["merchant"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": cashier.email, "password": "CashierPass123!"},
    )
    token = login_resp.json()["access_token"]

    resp = client.post(
        f"/api/v1/rbac/merchants/{merchant.id}/refunds",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    error_body = resp.json()

    # Verify standard JSON error envelope
    assert "code" in error_body
    assert error_body["code"] == "FORBIDDEN"
    assert "refunds:write" in error_body["message"]
    assert "details" in error_body
    assert error_body["details"]["required_permission"] == "refunds:write"
    assert error_body["details"]["merchant_id"] == str(merchant.id)


def test_rbac_manager_can_refund(client: TestClient, rbac_setup):
    """Manager possesses 'refunds:write', should succeed with 201."""
    manager = rbac_setup["manager"]
    merchant = rbac_setup["merchant"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": manager.email, "password": "ManagerPass123!"},
    )
    token = login_resp.json()["access_token"]

    resp = client.post(
        f"/api/v1/rbac/merchants/{merchant.id}/refunds",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "success"


def test_rbac_different_merchant_denied(client: TestClient, rbac_setup):
    """Cashier role is scoped to merchant A; requesting for arbitrary merchant B must fail with 403."""
    cashier = rbac_setup["cashier"]
    other_merchant_id = uuid.uuid4()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": cashier.email, "password": "CashierPass123!"},
    )
    token = login_resp.json()["access_token"]

    resp = client.get(
        f"/api/v1/rbac/merchants/{other_merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"
