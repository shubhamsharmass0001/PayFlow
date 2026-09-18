import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.invoices.models import Invoice, InvoiceStatus


@pytest.fixture
def merchant_with_customer_and_store(client: TestClient):
    """Provisions owner, merchant, customer, and store."""
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Invoice Test Owner",
            "phone": owner_phone,
        },
    )
    assert reg.status_code == 201
    owner_token = reg.json()["tokens"]["access_token"]

    merchant_email = f"merchant_{uuid.uuid4().hex[:8]}@retail.com"
    merchant_phone = f"+9197{uuid.uuid4().int % 100000000:08d}"
    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Apex Electronics",
            "legal_name": "Apex Electronics India Private Limited",
            "email": merchant_email,
            "phone": merchant_phone,
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5732",
            "initial_upi_vpa": "apex@icici",
        },
    )
    assert m_resp.status_code == 201
    merchant_id = m_resp.json()["id"]

    # Store
    store_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/stores",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Apex Flagship Store", "code": f"STORE-{uuid.uuid4().hex[:4]}", "city": "Mumbai", "postal_code": "400001"},
    )
    assert store_resp.status_code == 201, store_resp.text
    store_id = store_resp.json()["id"]

    # Customer
    cust_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Priya Patel",
            "phone": f"+9199{uuid.uuid4().int % 100000000:08d}",
            "email": f"priya_{uuid.uuid4().hex[:6]}@example.com",
        },
    )
    assert cust_resp.status_code == 201
    customer_id = cust_resp.json()["id"]

    return {
        "owner_token": owner_token,
        "merchant_id": merchant_id,
        "store_id": store_id,
        "customer_id": customer_id,
    }


def test_create_invoice_sequential_collision_safe_numbering(
    client: TestClient, merchant_with_customer_and_store, db: Session
):
    token = merchant_with_customer_and_store["owner_token"]
    merchant_id = merchant_with_customer_and_store["merchant_id"]
    customer_id = merchant_with_customer_and_store["customer_id"]
    store_id = merchant_with_customer_and_store["store_id"]

    # 1. Create first invoice
    resp1 = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_id": customer_id,
            "store_id": store_id,
            "allow_partial_payment": True,
            "allow_split_payment": True,
            "notes": "Payment terms: net 30",
        },
    )
    assert resp1.status_code == 201, resp1.text
    inv1_data = resp1.json()
    assert inv1_data["status"] == "DRAFT"
    assert "INV-APEXEL-" in inv1_data["invoice_number"]
    assert inv1_data["invoice_number"].endswith("-00001")
    assert Decimal(str(inv1_data["total_amount"])) == Decimal("0.00")

    # 2. Create second invoice under same merchant
    resp2 = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={"customer_id": customer_id},
    )
    assert resp2.status_code == 201, resp2.text
    inv2_data = resp2.json()
    assert inv2_data["invoice_number"].endswith("-00002")

    # Verify audit log
    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "invoices",
            AuditLog.entity_id == uuid.UUID(inv1_data["id"]),
            AuditLog.action == "CREATE",
        )
        .first()
    )
    assert audit is not None
    assert audit.changes["after"]["invoice_number"] == inv1_data["invoice_number"]


def test_server_computed_totals_and_item_management(
    client: TestClient, merchant_with_customer_and_store, db: Session
):
    token = merchant_with_customer_and_store["owner_token"]
    merchant_id = merchant_with_customer_and_store["merchant_id"]

    # Create DRAFT invoice
    inv_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert inv_resp.status_code == 201
    inv_id = inv_resp.json()["id"]

    # 1. Add item 1: qty 2 @ 100.00, discount 20.00, tax 18%
    # base = 200.00, taxable = 180.00, tax = 32.40, line_total = 212.40
    item1_resp = client.post(
        f"/api/v1/invoices/{inv_id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Wireless Mouse",
            "quantity": 2,
            "unit_price": 100.00,
            "discount_amount": 20.00,
            "tax_rate": 18.00,
        },
    )
    assert item1_resp.status_code == 201, item1_resp.text
    inv_data = item1_resp.json()
    assert Decimal(str(inv_data["subtotal"])) == Decimal("200.00")
    assert Decimal(str(inv_data["discount_total"])) == Decimal("20.00")
    assert Decimal(str(inv_data["tax_total"])) == Decimal("32.40")
    assert Decimal(str(inv_data["total_amount"])) == Decimal("212.40")
    assert len(inv_data["items"]) == 1
    item1_id = inv_data["items"][0]["id"]
    assert Decimal(str(inv_data["items"][0]["line_total"])) == Decimal("212.40")

    # 2. Add item 2: qty 1 @ 50.00, discount 0, tax 5%
    # base = 50.00, taxable = 50.00, tax = 2.50, line_total = 52.50
    item2_resp = client.post(
        f"/api/v1/invoices/{inv_id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Mousepad",
            "quantity": 1,
            "unit_price": 50.00,
            "discount_amount": 0.00,
            "tax_rate": 5.00,
        },
    )
    assert item2_resp.status_code == 201
    inv_data2 = item2_resp.json()
    # Totals: subtotal 250.00, discount 20.00, tax 34.90, grand_total 264.90
    assert Decimal(str(inv_data2["subtotal"])) == Decimal("250.00")
    assert Decimal(str(inv_data2["discount_total"])) == Decimal("20.00")
    assert Decimal(str(inv_data2["tax_total"])) == Decimal("34.90")
    assert Decimal(str(inv_data2["total_amount"])) == Decimal("264.90")
    assert len(inv_data2["items"]) == 2
    item2_id = [it["id"] for it in inv_data2["items"] if it["name"] == "Mousepad"][0]

    # 3. Delete item 2 -> Totals recalculate to item 1
    del_resp = client.delete(
        f"/api/v1/invoice-items/{item2_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_resp.status_code == 200, del_resp.text
    inv_after_del = del_resp.json()
    assert Decimal(str(inv_after_del["subtotal"])) == Decimal("200.00")
    assert Decimal(str(inv_after_del["discount_total"])) == Decimal("20.00")
    assert Decimal(str(inv_after_del["tax_total"])) == Decimal("32.40")
    assert Decimal(str(inv_after_del["total_amount"])) == Decimal("212.40")
    assert len(inv_after_del["items"]) == 1


def test_invoice_status_transitions_and_rules(
    client: TestClient, merchant_with_customer_and_store
):
    token = merchant_with_customer_and_store["owner_token"]
    merchant_id = merchant_with_customer_and_store["merchant_id"]

    inv_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    inv_id = inv_resp.json()["id"]

    # 1. Attempt manual transition to system-derived statuses (PAID, PARTIALLY_PAID, OVERDUE) -> 400
    for bad_status in ["PAID", "PARTIALLY_PAID", "OVERDUE", "REFUNDED"]:
        bad_patch = client.patch(
            f"/api/v1/invoices/{inv_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": bad_status},
        )
        assert bad_patch.status_code == 400, bad_patch.text
        assert bad_patch.json()["code"] == "INVALID_STATUS_TRANSITION"

    # 2. Valid transition: DRAFT -> SENT
    sent_resp = client.patch(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "SENT"},
    )
    assert sent_resp.status_code == 200, sent_resp.text
    assert sent_resp.json()["status"] == "SENT"

    # 3. Cannot add items once SENT
    add_item_sent = client.post(
        f"/api/v1/invoices/{inv_id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Late Item", "unit_price": 10.00},
    )
    assert add_item_sent.status_code == 400
    assert add_item_sent.json()["code"] == "INVOICE_NOT_EDITABLE"

    # 4. Valid transition: SENT -> CANCELLED
    cancel_resp = client.patch(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "CANCELLED"},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

    # 5. Cannot transition out of CANCELLED
    invalid_reopen = client.patch(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "SENT"},
    )
    assert invalid_reopen.status_code == 400


def test_invoice_search_filtering_and_pagination(
    client: TestClient, merchant_with_customer_and_store
):
    token = merchant_with_customer_and_store["owner_token"]
    merchant_id = merchant_with_customer_and_store["merchant_id"]
    customer_id = merchant_with_customer_and_store["customer_id"]

    # Create 3 invoices:
    # Inv 1: for customer Priya Patel
    inv1 = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={"customer_id": customer_id},
    ).json()

    # Inv 2: SENT
    inv2 = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()
    client.patch(
        f"/api/v1/invoices/{inv2['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "SENT"},
    )

    # Inv 3: DRAFT
    inv3 = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()

    # 1. Search by customer name "Priya"
    s_cust = client.get(
        f"/api/v1/merchants/{merchant_id}/invoices?search=priya",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert s_cust.status_code == 200
    assert s_cust.json()["total"] >= 1
    assert s_cust.json()["items"][0]["id"] == inv1["id"]

    # 2. Search by invoice number
    s_num = client.get(
        f"/api/v1/merchants/{merchant_id}/invoices?search={inv2['invoice_number']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert s_num.status_code == 200
    assert s_num.json()["total"] == 1
    assert s_num.json()["items"][0]["id"] == inv2["id"]

    # 3. Filter by status SENT
    f_sent = client.get(
        f"/api/v1/merchants/{merchant_id}/invoices?status=SENT",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert f_sent.status_code == 200
    for it in f_sent.json()["items"]:
        assert it["status"] == "SENT"

    # 4. Pagination test
    p_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/invoices?page=1&page_size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert p_data["page"] == 1
    assert p_data["page_size"] == 2
    assert p_data["total"] >= 3
    assert len(p_data["items"]) == 2


def test_invoice_rbac_enforcement(
    client: TestClient, merchant_with_customer_and_store
):
    owner_token = merchant_with_customer_and_store["owner_token"]
    merchant_id = merchant_with_customer_and_store["merchant_id"]

    # Provision Cashier and Auditor
    staff_tokens = {}
    for label, role_enum in [("Cashier", "CASHIER"), ("Auditor", "ACCOUNTANT")]:
        s_email = f"staff_{label.lower()}_{uuid.uuid4().hex[:6]}@test.com"
        s_phone = f"+9195{uuid.uuid4().int % 100000000:08d}"
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": s_email,
                "password": "Password123!",
                "full_name": f"{label} Staff",
                "phone": s_phone,
            },
        )
        s_token = reg.json()["tokens"]["access_token"]
        s_id = reg.json()["user"]["id"]

        client.post(
            f"/api/v1/merchants/{merchant_id}/staff",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"user_id": s_id, "role": role_enum},
        )
        staff_tokens[label] = s_token

    # 1. Cashier: Invoices:read AND invoices:write (can create and list invoices)
    cashier_post = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
        json={},
    )
    assert cashier_post.status_code == 201, cashier_post.text
    inv_id = cashier_post.json()["id"]

    cashier_get = client.get(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
    )
    assert cashier_get.status_code == 200

    # 2. Auditor: Invoices:read ONLY (cannot create or patch invoices)
    auditor_get = client.get(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
    )
    assert auditor_get.status_code == 200

    auditor_post = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
        json={},
    )
    assert auditor_post.status_code == 403
    assert auditor_post.json()["code"] == "FORBIDDEN"

    auditor_patch = client.patch(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
        json={"status": "SENT"},
    )
    assert auditor_patch.status_code == 403

    # 3. User from different merchant: Denied (403)
    other_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"other_{uuid.uuid4().hex[:6]}@test.com",
            "password": "Password123!",
            "full_name": "Foreign Merchant",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
        },
    )
    other_token = other_reg.json()["tokens"]["access_token"]

    denied = client.get(
        f"/api/v1/invoices/{inv_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert denied.status_code == 403
