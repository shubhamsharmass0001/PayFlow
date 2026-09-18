"""Tests for the Audit Logs read & query module.

Covers:
  - GET /merchants/{id}/audit-logs with RBAC (Auditor/Owner only, Manager/Cashier rejected)
  - Filtering by actor_user_id, entity_type, action, date range, and pagination
  - GET /audit-logs/{id} detail view with formatted before/after JSON diff
  - Error scenarios (401 unauthorized, 403 forbidden, 404 not found)
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction, AuditLog
from app.modules.audit.service import record_audit, AuditService
from app.modules.auth.models import User
from app.modules.merchants.models import MerchantStaff, StaffRole
from app.modules.rbac.seed import seed_rbac_data


@pytest.fixture
def audit_env(client: TestClient, db: Session):
    """Sets up an environment with:
    - Merchant organization
    - Owner user (has Owner RBAC role)
    - Auditor user (StaffRole.ACCOUNTANT -> Auditor RBAC role)
    - Manager user (StaffRole.MANAGER -> Manager RBAC role)
    - Cashier user (StaffRole.CASHIER -> Cashier RBAC role)
    """
    seed_rbac_data(db)

    # 1. Register Owner
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    r_owner = client.post(
        "/api/v1/auth/register",
        json={"email": owner_email, "password": "Password123!", "full_name": "Audit Org Owner"},
    )
    assert r_owner.status_code == 201
    owner_token = r_owner.json()["tokens"]["access_token"]
    owner_user_id = uuid.UUID(r_owner.json()["user"]["id"])

    # 2. Create Merchant
    r_merch = client.post(
        "/api/v1/merchants",
        json={
            "business_name": f"Audit Test Store {uuid.uuid4().hex[:6]}",
            "legal_name": "Audit Test Store Pvt Ltd",
            "email": f"auditstore_{uuid.uuid4().hex[:8]}@example.com",
            "phone": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "pan": "ABCDE1234F",
            "mcc_code": "5411",
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert r_merch.status_code == 201, r_merch.text
    merchant_id = uuid.UUID(r_merch.json()["id"])

    # Helper to register and onboard staff member
    def add_staff(role_enum: StaffRole, name: str):
        email = f"{role_enum.value.lower()}_{uuid.uuid4().hex[:8]}@example.com"
        r_user = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "full_name": name},
        )
        assert r_user.status_code == 201
        token = r_user.json()["tokens"]["access_token"]
        user_id = uuid.UUID(r_user.json()["user"]["id"])

        # Assign staff member role via API
        r_staff = client.post(
            f"/api/v1/merchants/{merchant_id}/staff",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"user_id": str(user_id), "role": role_enum.value},
        )
        assert r_staff.status_code == 201
        return {"token": token, "user_id": user_id, "email": email}

    auditor = add_staff(StaffRole.ACCOUNTANT, "Merchant Auditor")
    manager = add_staff(StaffRole.MANAGER, "Merchant Manager")
    cashier = add_staff(StaffRole.CASHIER, "Merchant Cashier")

    # Another independent merchant for cross-tenant isolation testing
    other_owner_email = f"other_owner_{uuid.uuid4().hex[:8]}@example.com"
    r_other = client.post(
        "/api/v1/auth/register",
        json={"email": other_owner_email, "password": "Password123!", "full_name": "Other Owner"},
    )
    assert r_other.status_code == 201
    other_owner_token = r_other.json()["tokens"]["access_token"]

    return {
        "merchant_id": merchant_id,
        "owner": {"token": owner_token, "user_id": owner_user_id, "email": owner_email},
        "auditor": auditor,
        "manager": manager,
        "cashier": cashier,
        "other_owner": {"token": other_owner_token},
    }


def test_audit_logs_rbac_enforcement(client: TestClient, db: Session, audit_env):
    """Ensures GET /merchants/{id}/audit-logs is strictly Owner/Auditor only."""
    merchant_id = str(audit_env["merchant_id"])

    # Seed one audit log
    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="merchants",
        entity_id=audit_env["merchant_id"],
        actor_id=audit_env["owner"]["user_id"],
        merchant_id=audit_env["merchant_id"],
        after={"name": "Test Merchant"},
    )
    db.commit()

    # 1. Owner CAN access
    res = client.get(
        f"/api/v1/merchants/{merchant_id}/audit-logs",
        headers={"Authorization": f"Bearer {audit_env['owner']['token']}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] >= 1

    # 2. Auditor CAN access
    res = client.get(
        f"/api/v1/merchants/{merchant_id}/audit-logs",
        headers={"Authorization": f"Bearer {audit_env['auditor']['token']}"},
    )
    assert res.status_code == 200
    assert len(res.json()["items"]) >= 1

    # 3. Manager CANNOT access (403 Forbidden)
    res = client.get(
        f"/api/v1/merchants/{merchant_id}/audit-logs",
        headers={"Authorization": f"Bearer {audit_env['manager']['token']}"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"

    # 4. Cashier CANNOT access (403 Forbidden)
    res = client.get(
        f"/api/v1/merchants/{merchant_id}/audit-logs",
        headers={"Authorization": f"Bearer {audit_env['cashier']['token']}"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"

    # 5. Other merchant's Owner CANNOT access (403 Forbidden)
    res = client.get(
        f"/api/v1/merchants/{merchant_id}/audit-logs",
        headers={"Authorization": f"Bearer {audit_env['other_owner']['token']}"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"

    # 6. Unauthenticated request CANNOT access (401 Unauthorized)
    res = client.get(f"/api/v1/merchants/{merchant_id}/audit-logs")
    assert res.status_code == 401


def test_audit_logs_filtering(client: TestClient, db: Session, audit_env):
    """Verifies filtering by actor_user_id, entity_type, action, and date range."""
    merchant_id = audit_env["merchant_id"]
    owner_id = audit_env["owner"]["user_id"]
    auditor_id = audit_env["auditor"]["user_id"]

    now = datetime.now(timezone.utc)
    t_past = now - timedelta(days=5)
    t_mid = now - timedelta(days=2)
    t_now = now

    # Clear existing logs for this test merchant to ensure precise counts
    db.query(AuditLog).filter(AuditLog.merchant_id == merchant_id).delete()
    db.commit()

    # Log 1: Created 5 days ago by owner on invoice
    log1 = AuditLog(
        merchant_id=merchant_id,
        user_id=owner_id,
        entity_name="invoices",
        entity_id=uuid.uuid4(),
        action=AuditAction.CREATE,
        changes={"after": {"number": "INV-001", "amount": 1000}},
        created_at=t_past,
    )
    # Log 2: Created 2 days ago by auditor on customer
    log2 = AuditLog(
        merchant_id=merchant_id,
        user_id=auditor_id,
        entity_name="customers",
        entity_id=uuid.uuid4(),
        action=AuditAction.UPDATE,
        changes={"before": {"name": "Alice"}, "after": {"name": "Alice Smith"}},
        created_at=t_mid,
    )
    # Log 3: Created now by owner on invoice status
    log3 = AuditLog(
        merchant_id=merchant_id,
        user_id=owner_id,
        entity_name="invoices",
        entity_id=uuid.uuid4(),
        action=AuditAction.STATUS_CHANGE,
        changes={"before": {"status": "ISSUED"}, "after": {"status": "PAID"}},
        created_at=t_now,
    )
    db.add_all([log1, log2, log3])
    db.commit()

    headers = {"Authorization": f"Bearer {audit_env['owner']['token']}"}
    base_url = f"/api/v1/merchants/{merchant_id}/audit-logs"

    # 1. No filter: returns all 3
    r = client.get(base_url, headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 3

    # 2. Filter by actor_user_id = auditor_id: returns 1
    r = client.get(f"{base_url}?actor_user_id={auditor_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["entity_type"] == "customers"

    # 3. Filter by entity_type = invoices: returns 2
    r = client.get(f"{base_url}?entity_type=invoices", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 2

    # 4. Filter by action = STATUS_CHANGE: returns 1
    r = client.get(f"{base_url}?action=STATUS_CHANGE", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["action"] == "STATUS_CHANGE"

    # 5. Filter by date range (only mid to now)
    from_iso = (t_mid - timedelta(hours=1)).isoformat()
    r = client.get(f"{base_url}?from_date={from_iso}", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 2

    # 6. Pagination check
    r = client.get(f"{base_url}?page=1&page_size=2", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["total_pages"] == 2
    assert data["page"] == 1


def test_audit_log_detail_view_and_diff_formatting(client: TestClient, db: Session, audit_env):
    """Verifies GET /audit-logs/{id} returns formatted before/after JSON diff."""
    merchant_id = audit_env["merchant_id"]
    owner_id = audit_env["owner"]["user_id"]

    # Create an UPDATE audit log with modified, added, removed, and unchanged fields
    before_state = {
        "title": "Old Store Name",
        "description": "Store description",
        "is_active": False,
        "legacy_code": "OLD-123",
    }
    after_state = {
        "title": "New Store Name",       # MODIFIED
        "description": "Store description", # UNCHANGED
        "is_active": True,                # MODIFIED
        "tax_id": "GSTIN-987654",         # ADDED
        # legacy_code is missing -> REMOVED
    }

    log = record_audit(
        db=db,
        action=AuditAction.UPDATE,
        entity_name="stores",
        entity_id=uuid.uuid4(),
        actor_id=owner_id,
        merchant_id=merchant_id,
        before=before_state,
        after=after_state,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    )
    db.commit()

    # 1. Owner views detail
    res = client.get(
        f"/api/v1/audit-logs/{log.id}",
        headers={"Authorization": f"Bearer {audit_env['owner']['token']}"},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["id"] == str(log.id)
    assert data["merchant_id"] == str(merchant_id)
    assert data["entity_type"] == "stores"
    assert data["action"] == "UPDATE"
    assert data["ip_address"] == "192.168.1.100"

    # Check before and after dictionaries
    assert data["before"] == before_state
    assert data["after"] == after_state

    # Check diff breakdown
    diff = data["diff"]
    assert "title" in diff
    assert diff["title"]["status"] == "MODIFIED"
    assert diff["title"]["before"] == "Old Store Name"
    assert diff["title"]["after"] == "New Store Name"

    assert "is_active" in diff
    assert diff["is_active"]["status"] == "MODIFIED"
    assert diff["is_active"]["before"] is False
    assert diff["is_active"]["after"] is True

    assert "description" in diff
    assert diff["description"]["status"] == "UNCHANGED"
    assert diff["description"]["before"] == "Store description"
    assert diff["description"]["after"] == "Store description"

    assert "tax_id" in diff
    assert diff["tax_id"]["status"] == "ADDED"
    assert diff["tax_id"]["before"] is None
    assert diff["tax_id"]["after"] == "GSTIN-987654"

    assert "legacy_code" in diff
    assert diff["legacy_code"]["status"] == "REMOVED"
    assert diff["legacy_code"]["before"] == "OLD-123"
    assert diff["legacy_code"]["after"] is None

    # 2. Auditor also CAN view detail
    res_auditor = client.get(
        f"/api/v1/audit-logs/{log.id}",
        headers={"Authorization": f"Bearer {audit_env['auditor']['token']}"},
    )
    assert res_auditor.status_code == 200

    # 3. Manager CANNOT view detail (403 Forbidden)
    res_manager = client.get(
        f"/api/v1/audit-logs/{log.id}",
        headers={"Authorization": f"Bearer {audit_env['manager']['token']}"},
    )
    assert res_manager.status_code == 403

    # 4. Cashier CANNOT view detail (403 Forbidden)
    res_cashier = client.get(
        f"/api/v1/audit-logs/{log.id}",
        headers={"Authorization": f"Bearer {audit_env['cashier']['token']}"},
    )
    assert res_cashier.status_code == 403

    # 5. Non-existent audit log returns 404
    fake_id = uuid.uuid4()
    res_404 = client.get(
        f"/api/v1/audit-logs/{fake_id}",
        headers={"Authorization": f"Bearer {audit_env['owner']['token']}"},
    )
    assert res_404.status_code == 404

    # 6. Other merchant owner CANNOT view detail (403 Forbidden)
    res_other = client.get(
        f"/api/v1/audit-logs/{log.id}",
        headers={"Authorization": f"Bearer {audit_env['other_owner']['token']}"},
    )
    assert res_other.status_code == 403


def test_audit_log_create_and_delete_diff(client: TestClient, db: Session, audit_env):
    """Verifies diff status computation for CREATE (ADDED) and DELETE (REMOVED)."""
    merchant_id = audit_env["merchant_id"]
    owner_id = audit_env["owner"]["user_id"]

    # 1. CREATE log
    create_log = record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="customers",
        entity_id=uuid.uuid4(),
        actor_id=owner_id,
        merchant_id=merchant_id,
        after={"name": "Bob", "email": "bob@example.com"},
    )
    # 2. DELETE log
    delete_log = record_audit(
        db=db,
        action=AuditAction.DELETE,
        entity_name="customers",
        entity_id=uuid.uuid4(),
        actor_id=owner_id,
        merchant_id=merchant_id,
        before={"name": "Charlie", "email": "charlie@example.com"},
    )
    db.commit()

    headers = {"Authorization": f"Bearer {audit_env['owner']['token']}"}

    # Verify CREATE
    r_create = client.get(f"/api/v1/audit-logs/{create_log.id}", headers=headers)
    assert r_create.status_code == 200
    c_data = r_create.json()
    assert c_data["before"] is None
    assert c_data["after"] == {"name": "Bob", "email": "bob@example.com"}
    assert c_data["diff"]["name"]["status"] == "ADDED"
    assert c_data["diff"]["name"]["after"] == "Bob"
    assert c_data["diff"]["email"]["status"] == "ADDED"

    # Verify DELETE
    r_del = client.get(f"/api/v1/audit-logs/{delete_log.id}", headers=headers)
    assert r_del.status_code == 200
    d_data = r_del.json()
    assert d_data["before"] == {"name": "Charlie", "email": "charlie@example.com"}
    assert d_data["after"] is None
    assert d_data["diff"]["name"]["status"] == "REMOVED"
    assert d_data["diff"]["name"]["before"] == "Charlie"
    assert d_data["diff"]["email"]["status"] == "REMOVED"


def test_audit_logs_start_date_end_date_aliases(client: TestClient, db: Session, audit_env):
    """Verifies that start_date and end_date aliases work for date range filtering."""
    merchant_id = audit_env["merchant_id"]
    headers = {"Authorization": f"Bearer {audit_env['owner']['token']}"}

    now = datetime.now(timezone.utc)
    t_start = (now - timedelta(days=1)).isoformat()
    t_end = (now + timedelta(days=1)).isoformat()

    r = client.get(
        f"/api/v1/merchants/{merchant_id}/audit-logs?start_date={t_start}&end_date={t_end}",
        headers=headers,
    )
    assert r.status_code == 200
    assert "items" in r.json()

