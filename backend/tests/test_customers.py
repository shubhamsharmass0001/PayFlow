import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.customers.models import Customer


@pytest.fixture
def merchant_setup(client: TestClient):
    """Creates an owner user and onboarded merchant."""
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Merchant Owner",
            "phone": owner_phone,
        },
    )
    assert reg.status_code == 201, reg.text
    owner_token = reg.json()["tokens"]["access_token"]
    owner_id = reg.json()["user"]["id"]

    merchant_email = f"merchant_{uuid.uuid4().hex[:8]}@biz.com"
    merchant_phone = f"+9197{uuid.uuid4().int % 100000000:08d}"
    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Metro Hypermarket",
            "legal_name": "Metro Retail Enterprise Ltd",
            "email": merchant_email,
            "phone": merchant_phone,
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5411",
            "initial_upi_vpa": "metro@okaxis",
        },
    )
    assert m_resp.status_code == 201, m_resp.text
    merchant_id = m_resp.json()["id"]

    return {
        "owner_token": owner_token,
        "owner_id": owner_id,
        "merchant_id": merchant_id,
    }


def test_customer_creation_and_audit(client: TestClient, merchant_setup, db: Session):
    token = merchant_setup["owner_token"]
    merchant_id = merchant_setup["merchant_id"]

    customer_phone = f"+9191{uuid.uuid4().int % 100000000:08d}"
    payload = {
        "name": "Aarav Sharma",
        "phone": customer_phone,
        "email": "aarav.sharma@example.com",
        "upi_vpa": "aarav@oksbi",
    }

    resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["name"] == "Aarav Sharma"
    assert data["phone"] == customer_phone
    assert data["email"] == "aarav.sharma@example.com"
    assert data["upi_vpa"] == "aarav@oksbi"
    assert data["warning"] is None
    assert "X-Warning" not in resp.headers

    customer_id = uuid.UUID(data["id"])
    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "customers",
            AuditLog.entity_id == customer_id,
            AuditLog.action == "CREATE",
        )
        .first()
    )
    assert audit is not None
    assert audit.changes["after"]["name"] == "Aarav Sharma"


def test_customer_deduplication_warns_and_does_not_merge(
    client: TestClient, merchant_setup, db: Session
):
    token = merchant_setup["owner_token"]
    merchant_id = merchant_setup["merchant_id"]

    shared_phone = f"+9192{uuid.uuid4().int % 100000000:08d}"

    # 1. Create first customer
    resp1 = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "First Customer",
            "phone": shared_phone,
            "email": "first@example.com",
        },
    )
    assert resp1.status_code == 201, resp1.text
    cust1_id = resp1.json()["id"]

    # 2. Create second customer under same merchant with duplicate phone
    resp2 = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Second Customer",
            "phone": shared_phone,
            "email": "second@example.com",
        },
    )
    assert resp2.status_code == 201, resp2.text
    cust2_data = resp2.json()
    cust2_id = cust2_data["id"]

    # Must be separate records, NOT silently merged
    assert cust1_id != cust2_id
    assert cust2_data["name"] == "Second Customer"
    assert cust2_data["email"] == "second@example.com"

    # Warning must be present in response and header
    assert cust2_data["warning"] is not None
    assert "already exists" in cust2_data["warning"]
    assert cust1_id in cust2_data["warning"]
    assert "X-Warning" in resp2.headers
    assert "already exists" in resp2.headers["X-Warning"]

    # First customer must remain unchanged in DB
    db.expire_all()
    c1_db = db.query(Customer).filter(Customer.id == uuid.UUID(cust1_id)).first()
    assert c1_db.name == "First Customer"
    assert c1_db.email == "first@example.com"


def test_customer_get_and_patch(client: TestClient, merchant_setup, db: Session):
    token = merchant_setup["owner_token"]
    merchant_id = merchant_setup["merchant_id"]

    phone = f"+9193{uuid.uuid4().int % 100000000:08d}"
    create_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Rohit Verma", "phone": phone, "email": "rohit@test.com"},
    )
    assert create_resp.status_code == 201
    cust_id = create_resp.json()["id"]

    # GET /customers/{id}
    get_resp = client.get(
        f"/api/v1/customers/{cust_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()["name"] == "Rohit Verma"

    # PATCH /customers/{id}
    patch_resp = client.patch(
        f"/api/v1/customers/{cust_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Rohit V. Sharma", "upi_vpa": "rohit@paytm"},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    assert patch_resp.json()["name"] == "Rohit V. Sharma"
    assert patch_resp.json()["upi_vpa"] == "rohit@paytm"

    # Verify audit log recorded UPDATE
    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "customers",
            AuditLog.entity_id == uuid.UUID(cust_id),
            AuditLog.action == "UPDATE",
        )
        .first()
    )
    assert audit is not None
    assert audit.changes["before"]["name"] == "Rohit Verma"
    assert audit.changes["after"]["name"] == "Rohit V. Sharma"


def test_customer_pagination_search_and_sorting(client: TestClient, merchant_setup):
    token = merchant_setup["owner_token"]
    merchant_id = merchant_setup["merchant_id"]

    suffix = uuid.uuid4().hex[:4]
    # Seed multiple customers
    test_customers = [
        {"name": f"Alice Wonderland {suffix}", "phone": f"+919400{uuid.uuid4().int % 100000:05d}", "email": f"alice_{suffix}@story.com"},
        {"name": f"Bob Builder {suffix}", "phone": f"+919400{uuid.uuid4().int % 100000:05d}", "email": f"bob_{suffix}@tool.com"},
        {"name": f"Charlie Chaplin {suffix}", "phone": f"+919400{uuid.uuid4().int % 100000:05d}", "email": f"charlie_{suffix}@film.com"},
        {"name": f"David Copperfield {suffix}", "phone": f"+919400{uuid.uuid4().int % 100000:05d}", "email": f"david_{suffix}@magic.com"},
        {"name": f"Eva Green {suffix}", "phone": f"+919400{uuid.uuid4().int % 100000:05d}", "email": f"eva_{suffix}@cinema.com"},
    ]

    for c in test_customers:
        res = client.post(
            f"/api/v1/merchants/{merchant_id}/customers",
            headers={"Authorization": f"Bearer {token}"},
            json=c,
        )
        assert res.status_code == 201

    # 1. Test pagination
    p_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/customers?page=1&page_size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert p_resp.status_code == 200, p_resp.text
    p_data = p_resp.json()
    assert p_data["page"] == 1
    assert p_data["page_size"] == 2
    assert p_data["total"] >= 5
    assert len(p_data["items"]) == 2

    # 2. Test search by name (case-insensitive)
    s_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/customers?search=builder+{suffix}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert s_resp.status_code == 200
    s_data = s_resp.json()
    assert s_data["total"] == 1
    assert s_data["items"][0]["name"] == f"Bob Builder {suffix}"

    # 3. Test search by email
    s_email = client.get(
        f"/api/v1/merchants/{merchant_id}/customers?search=david_{suffix}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert s_email.status_code == 200
    assert s_email.json()["total"] == 1
    assert s_email.json()["items"][0]["name"] == f"David Copperfield {suffix}"

    # 4. Test search by phone
    s_phone = client.get(
        f"/api/v1/merchants/{merchant_id}/customers?search={test_customers[4]['phone'][-6:]}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert s_phone.status_code == 200
    assert s_phone.json()["total"] == 1
    assert s_phone.json()["items"][0]["name"] == f"Eva Green {suffix}"

    # 5. Test sorting
    sort_asc = client.get(
        f"/api/v1/merchants/{merchant_id}/customers?sort_by=name&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"},
    )
    names = [c["name"] for c in sort_asc.json()["items"]]
    assert names == sorted(names)


def test_customer_rbac_roles(client: TestClient, merchant_setup):
    owner_token = merchant_setup["owner_token"]
    merchant_id = merchant_setup["merchant_id"]

    # Setup staff members: Manager, Cashier, Auditor (StaffRole.ACCOUNTANT)
    roles = [("Manager", "MANAGER"), ("Cashier", "CASHIER"), ("Auditor", "ACCOUNTANT")]
    staff_tokens = {}

    for label, role_enum in roles:
        s_email = f"staff_{label.lower()}_{uuid.uuid4().hex[:6]}@example.com"
        s_phone = f"+9195{uuid.uuid4().int % 100000000:08d}"
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": s_email,
                "password": "Password123!",
                "full_name": f"{label} User",
                "phone": s_phone,
            },
        )
        assert reg.status_code == 201
        staff_token = reg.json()["tokens"]["access_token"]
        staff_id = reg.json()["user"]["id"]

        # Assign role via Owner
        assign = client.post(
            f"/api/v1/merchants/{merchant_id}/staff",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"user_id": staff_id, "role": role_enum},
        )
        assert assign.status_code == 201, assign.text
        staff_tokens[label] = staff_token

    # 1. Manager: Can read and write customers
    mgr_create = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {staff_tokens['Manager']}"},
        json={"name": "Manager Client", "phone": "+919600000001"},
    )
    assert mgr_create.status_code == 201, mgr_create.text
    cust_id = mgr_create.json()["id"]

    mgr_patch = client.patch(
        f"/api/v1/customers/{cust_id}",
        headers={"Authorization": f"Bearer {staff_tokens['Manager']}"},
        json={"name": "Manager Client Updated"},
    )
    assert mgr_patch.status_code == 200

    # 2. Cashier: Read-only
    cashier_get = client.get(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
    )
    assert cashier_get.status_code == 200

    cashier_cust_get = client.get(
        f"/api/v1/customers/{cust_id}",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
    )
    assert cashier_cust_get.status_code == 200

    cashier_create = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
        json={"name": "Cashier Client", "phone": "+919600000002"},
    )
    assert cashier_create.status_code == 403
    assert cashier_create.json()["code"] == "FORBIDDEN"

    cashier_patch = client.patch(
        f"/api/v1/customers/{cust_id}",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
        json={"name": "Forbidden Edit"},
    )
    assert cashier_patch.status_code == 403

    # 3. Auditor: Read-only
    auditor_get = client.get(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
    )
    assert auditor_get.status_code == 200

    auditor_create = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
        json={"name": "Auditor Client", "phone": "+919600000003"},
    )
    assert auditor_create.status_code == 403

    # 4. Separate Merchant user: Denied access to this merchant's customers
    other_email = f"other_{uuid.uuid4().hex[:6]}@example.com"
    other_phone = f"+9196{uuid.uuid4().int % 100000000:08d}"
    reg_other = client.post(
        "/api/v1/auth/register",
        json={
            "email": other_email,
            "password": "Password123!",
            "full_name": "Other Merchant User",
            "phone": other_phone,
        },
    )
    other_token = reg_other.json()["tokens"]["access_token"]

    denied_list = client.get(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert denied_list.status_code == 403

    denied_get = client.get(
        f"/api/v1/customers/{cust_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert denied_get.status_code == 403
