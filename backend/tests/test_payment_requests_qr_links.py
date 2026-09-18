import os
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.invoices.models import Invoice


@pytest.fixture
def invoice_setup(client: TestClient):
    """Provisions owner, merchant, and an invoice with calculated total amount."""
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    owner_phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": owner_email,
            "password": "Password123!",
            "full_name": "Payment Test Owner",
            "phone": owner_phone,
        },
    )
    owner_token = reg.json()["tokens"]["access_token"]

    merchant_email = f"merchant_{uuid.uuid4().hex[:8]}@store.com"
    merchant_phone = f"+9197{uuid.uuid4().int % 100000000:08d}"
    m_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Zenith Retail",
            "legal_name": "Zenith Retail Pvt Ltd",
            "email": merchant_email,
            "phone": merchant_phone,
            "pan": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "mcc_code": "5311",
            "initial_upi_vpa": "zenith@hdfcbank",
        },
    )
    merchant_id = m_resp.json()["id"]

    # Create Invoice and add an item with total = 1000.00
    inv_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"notes": "Order #4521"},
    )
    invoice_id = inv_resp.json()["id"]

    item_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/items",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Mechanical Keyboard",
            "quantity": 1,
            "unit_price": 1000.00,
            "discount_amount": 0.00,
            "tax_rate": 0.00,
        },
    )
    assert item_resp.status_code == 201
    assert Decimal(str(item_resp.json()["total_amount"])) == Decimal("1000.00")

    return {
        "owner_token": owner_token,
        "merchant_id": merchant_id,
        "invoice_id": invoice_id,
    }


def test_create_payment_request_and_balance_validation(
    client: TestClient, invoice_setup, db: Session
):
    token = invoice_setup["owner_token"]
    invoice_id = invoice_setup["invoice_id"]

    # 1. Create first payment request (Installment 1: 600.00)
    pr1_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": 600.00,
            "purpose": "Installment 1: Deposit",
            "payer_vpa": "payer@okhdfcbank",
        },
    )
    assert pr1_resp.status_code == 201, pr1_resp.text
    pr1 = pr1_resp.json()
    assert Decimal(str(pr1["amount"])) == Decimal("600.00")
    assert pr1["purpose"] == "Installment 1: Deposit"
    assert pr1["status"] == "PENDING"
    assert pr1["payer_vpa"] == "payer@okhdfcbank"

    # Verify audit log
    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "payment_requests",
            AuditLog.entity_id == uuid.UUID(pr1["id"]),
            AuditLog.action == "CREATE",
        )
        .first()
    )
    assert audit is not None
    assert audit.changes["after"]["amount"] == "600.00"

    # 2. Create second payment request (Installment 2: 400.00)
    # Legitimate multiple payment requests against single invoice
    pr2_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": 400.00,
            "purpose": "Installment 2: Final Settlement",
        },
    )
    assert pr2_resp.status_code == 201, pr2_resp.text
    assert Decimal(str(pr2_resp.json()["amount"])) == Decimal("400.00")

    # 3. Create payment request exceeding invoice total balance (> 1000.00)
    bad_pr = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 1000.01},
    )
    assert bad_pr.status_code == 400
    assert bad_pr.json()["code"] == "AMOUNT_EXCEEDS_BALANCE"


def test_generate_upi_qr_payload_and_image(
    client: TestClient, invoice_setup, db: Session
):
    token = invoice_setup["owner_token"]
    invoice_id = invoice_setup["invoice_id"]

    pr_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 750.00, "purpose": "Online Payment"},
    )
    pr_id = pr_resp.json()["id"]

    # Generate QR Code
    qr_resp = client.post(
        f"/api/v1/payment-requests/{pr_id}/qr",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert qr_resp.status_code == 201, qr_resp.text
    qr_data = qr_resp.json()

    # Verify intent parameters
    upi_str = qr_data["upi_string"]
    assert "pa=zenith@hdfcbank" in upi_str
    assert "pn=Zenith Retail" in upi_str
    assert "am=750.00" in upi_str
    assert f"tr={pr_id}" in upi_str
    assert "cu=INR" in upi_str

    # Verify base64 data URL
    assert qr_data["qr_data_url"].startswith("data:image/png;base64,")

    # Verify file saved on disk
    file_url = qr_data["image_url"]
    assert file_url.startswith("/uploads/qr/")
    filename = os.path.basename(file_url)
    disk_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "qr", filename)
    )
    assert os.path.exists(disk_path)
    assert os.path.getsize(disk_path) > 0

    # Verify audit log
    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_name == "upi_qr_codes",
            AuditLog.entity_id == uuid.UUID(qr_data["id"]),
            AuditLog.action == "CREATE",
        )
        .first()
    )
    assert audit is not None


def test_payment_link_generation_and_tamper_proof_public_checkout(
    client: TestClient, invoice_setup, db: Session
):
    token = invoice_setup["owner_token"]
    invoice_id = invoice_setup["invoice_id"]

    # 1. Create Payment Request for 600.00
    pr_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 600.00, "purpose": "Milestone #1"},
    )
    pr_id = pr_resp.json()["id"]

    # 2. Create Payment Link
    link_resp = client.post(
        f"/api/v1/payment-requests/{pr_id}/link",
        headers={"Authorization": f"Bearer {token}"},
        json={"max_uses": 2},
    )
    assert link_resp.status_code == 201, link_resp.text
    link_data = link_resp.json()
    slug = link_data["short_code"]
    assert len(slug) >= 6
    assert link_data["payment_url"] == f"/pay/{slug}"
    assert Decimal(str(link_data["amount"])) == Decimal("600.00")

    # 3. Access Public Checkout Page without Authentication
    public_resp = client.get(f"/pay/{slug}")
    assert public_resp.status_code == 200, public_resp.text
    pay_page = public_resp.json()

    assert pay_page["slug"] == slug
    assert pay_page["merchant_name"] == "Zenith Retail"
    assert pay_page["purpose"] == "Milestone #1"
    assert pay_page["status"] == "ACTIVE"
    assert pay_page["is_mock_provider"] is True

    # TAMPER-PROOF VERIFICATION:
    # Amount is strictly 600.00 as stored on server
    assert Decimal(str(pay_page["amount"])) == Decimal("600.00")

    # Tampering attempt via query params must be ignored
    tamper_resp = client.get(f"/pay/{slug}?amount=1.00&merchant=Hacker")
    assert tamper_resp.status_code == 200
    tampered_data = tamper_resp.json()
    assert Decimal(str(tampered_data["amount"])) == Decimal("600.00")
    assert tampered_data["merchant_name"] == "Zenith Retail"


def test_payment_link_expired(client: TestClient, invoice_setup):
    token = invoice_setup["owner_token"]
    invoice_id = invoice_setup["invoice_id"]

    pr_resp = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 250.00},
    )
    pr_id = pr_resp.json()["id"]

    # Create link with expiration in the past
    past_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    link_resp = client.post(
        f"/api/v1/payment-requests/{pr_id}/link",
        headers={"Authorization": f"Bearer {token}"},
        json={"expires_at": past_time},
    )
    assert link_resp.status_code == 201
    slug = link_resp.json()["short_code"]

    # Accessing expired link returns 400 PAYMENT_LINK_EXPIRED
    pub_resp = client.get(f"/pay/{slug}")
    assert pub_resp.status_code == 400
    assert pub_resp.json()["code"] == "PAYMENT_LINK_EXPIRED"


def test_payment_requests_rbac_and_isolation(
    client: TestClient, invoice_setup
):
    owner_token = invoice_setup["owner_token"]
    merchant_id = invoice_setup["merchant_id"]
    invoice_id = invoice_setup["invoice_id"]

    # Provision Cashier (has payments:write) and Auditor (has payments:read only)
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

    # 1. Cashier can create payment request, QR, and link (payments:write)
    cashier_pr = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
        json={"amount": 100.00},
    )
    assert cashier_pr.status_code == 201, cashier_pr.text
    pr_id = cashier_pr.json()["id"]

    cashier_qr = client.post(
        f"/api/v1/payment-requests/{pr_id}/qr",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
    )
    assert cashier_qr.status_code == 201

    cashier_link = client.post(
        f"/api/v1/payment-requests/{pr_id}/link",
        headers={"Authorization": f"Bearer {staff_tokens['Cashier']}"},
        json={},
    )
    assert cashier_link.status_code == 201

    # 2. Auditor cannot create payment request or link (payments:write forbidden)
    auditor_pr = client.post(
        f"/api/v1/invoices/{invoice_id}/payment-requests",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
        json={"amount": 50.00},
    )
    assert auditor_pr.status_code == 403
    assert auditor_pr.json()["code"] == "FORBIDDEN"

    auditor_qr = client.post(
        f"/api/v1/payment-requests/{pr_id}/qr",
        headers={"Authorization": f"Bearer {staff_tokens['Auditor']}"},
    )
    assert auditor_qr.status_code == 403

    # 3. Foreign user from another merchant is denied
    other_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"other_{uuid.uuid4().hex[:6]}@test.com",
            "password": "Password123!",
            "full_name": "Foreign User",
            "phone": f"+9196{uuid.uuid4().int % 100000000:08d}",
        },
    )
    other_token = other_reg.json()["tokens"]["access_token"]
    denied = client.post(
        f"/api/v1/payment-requests/{pr_id}/qr",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert denied.status_code == 403
