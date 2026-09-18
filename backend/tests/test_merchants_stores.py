import io
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction, AuditLog
from app.modules.merchants.models import KycStatus, Merchant, MerchantStaff, StaffRole
from app.modules.rbac.models import UserRole
from app.modules.stores.models import Store


@pytest.fixture
def auth_owner(client: TestClient):
    """Registers and authenticates a test user who will act as owner."""
    email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "OwnerPassword123!",
            "full_name": "Merchant Owner",
            "phone": phone,
        },
    )
    assert reg.status_code == 201, reg.text
    token = reg.json()["tokens"]["access_token"]
    user_id = reg.json()["user"]["id"]
    return {"token": token, "user_id": user_id, "email": email}


def test_merchant_onboarding_success(client: TestClient, auth_owner, db: Session):
    token = auth_owner["token"]
    email = f"merchant_{uuid.uuid4().hex[:8]}@business.com"
    payload = {
        "business_name": "Fresh Mart Retail",
        "legal_name": "Fresh Mart Retail India Pvt Ltd",
        "email": email,
        "phone": "+919876543211",
        "pan": "ABCDE1234F",
        "gstin": "27ABCDE1234F1Z5",
        "mcc_code": "5411",
        "initial_upi_vpa": "freshmart@okicici",
    }

    resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    merchant_id = uuid.UUID(data["id"])

    assert data["business_name"] == "Fresh Mart Retail"
    assert data["kyc_status"] == "PENDING"
    assert data["risk_tier"] == "MEDIUM"

    # Verify Owner role assignment in user_roles and merchant_staff
    user_id = uuid.UUID(auth_owner["user_id"])
    staff = db.query(MerchantStaff).filter(
        MerchantStaff.merchant_id == merchant_id,
        MerchantStaff.user_id == user_id,
    ).first()
    assert staff is not None
    assert staff.role == StaffRole.OWNER

    user_role = db.query(UserRole).filter(
        UserRole.merchant_id == merchant_id,
        UserRole.user_id == user_id,
    ).first()
    assert user_role is not None

    # Verify audit_logs entry
    audit = db.query(AuditLog).filter(
        AuditLog.merchant_id == merchant_id,
        AuditLog.entity_name == "merchants",
        AuditLog.action == AuditAction.CREATE,
    ).first()
    assert audit is not None
    assert audit.changes["after"]["pan"] == "ABCDE1234F"


def test_merchant_onboarding_invalid_pan(client: TestClient, auth_owner):
    token = auth_owner["token"]
    payload = {
        "business_name": "Invalid Store",
        "legal_name": "Invalid Store Ltd",
        "email": f"badpan_{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+919876543222",
        "pan": "BADPAN123",  # Invalid PAN pattern
        "mcc_code": "5411",
    }
    resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "errors" in data["details"]


def test_merchant_onboarding_invalid_mcc(client: TestClient, auth_owner):
    token = auth_owner["token"]
    payload = {
        "business_name": "Invalid MCC Store",
        "legal_name": "Invalid MCC Store Ltd",
        "email": f"badmcc_{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+919876543223",
        "pan": "ABCDE1234F",
        "mcc_code": "12",  # Must be 4 digits
    }
    resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_kyc_document_upload_and_disk_storage(client: TestClient, auth_owner, db: Session):
    token = auth_owner["token"]
    onboard_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "Docs Store",
            "legal_name": "Docs Store Pvt Ltd",
            "email": f"docs_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+919876543233",
            "pan": "ABCDE1234F",
            "mcc_code": "5411",
        },
    )
    merchant_id = onboard_resp.json()["id"]

    # Upload mock KYC file
    file_content = b"PDF Mock Content for PAN Card Verification"
    files = {"file": ("pan_card.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {
        "document_type": "PAN",
        "document_number": "ABCDE1234F",
        "notes": "Original scan uploaded by merchant",
    }

    upload_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/kyc-documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data,
    )
    assert upload_resp.status_code == 201, upload_resp.text
    res_data = upload_resp.json()
    assert res_data["document_type"] == "PAN"
    assert "/uploads/" in res_data["file_url"]

    # Verify audit log entry
    audit = db.query(AuditLog).filter(
        AuditLog.merchant_id == uuid.UUID(merchant_id),
        AuditLog.entity_name == "merchant_kyc_documents",
        AuditLog.action == AuditAction.CREATE,
    ).first()
    assert audit is not None


def test_get_merchant_detail_and_profile_patch(client: TestClient, auth_owner, db: Session):
    token = auth_owner["token"]
    onboard_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "Patch Store",
            "legal_name": "Patch Store Ltd",
            "email": f"patch_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+919876543244",
            "pan": "ABCDE1234F",
            "mcc_code": "5411",
        },
    )
    merchant_id = onboard_resp.json()["id"]

    # GET merchant detail
    get_resp = client.get(
        f"/api/v1/merchants/{merchant_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    detail = get_resp.json()
    assert detail["merchant"]["business_name"] == "Patch Store"
    assert len(detail["kyc_documents"]) >= 1

    # PATCH profile
    patch_resp = client.patch(
        f"/api/v1/merchants/{merchant_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "Updated Store Name",
            "upi_vpa": "updated_store@upi",
        },
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["business_name"] == "Updated Store Name"
    assert updated["upi_vpa"] == "updated_store@upi"

    # Verify audit log diff
    audit = db.query(AuditLog).filter(
        AuditLog.merchant_id == uuid.UUID(merchant_id),
        AuditLog.entity_name == "merchants",
        AuditLog.action == AuditAction.UPDATE,
    ).first()
    assert audit is not None
    assert audit.changes["before"]["business_name"] == "Patch Store"
    assert audit.changes["after"]["business_name"] == "Updated Store Name"


def test_stores_management_and_vpa_override(client: TestClient, auth_owner, db: Session):
    token = auth_owner["token"]
    onboard_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "Retail Corp",
            "legal_name": "Retail Corp India",
            "email": f"retail_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+919876543255",
            "pan": "ABCDE1234F",
            "mcc_code": "5411",
            "initial_upi_vpa": "retail_corp@okhdfc",
        },
    )
    merchant_id = onboard_resp.json()["id"]

    # Create Store with custom UPI VPA override
    store_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/stores",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Indiranagar Branch",
            "code": "BLR-01",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560038",
            "upi_vpa": "retail_blr01@okhdfc",  # Override VPA
        },
    )
    assert store_resp.status_code == 201, store_resp.text
    store_data = store_resp.json()
    store_id = store_data["id"]
    assert store_data["upi_vpa"] == "retail_blr01@okhdfc"

    # List stores
    list_resp = client.get(
        f"/api/v1/merchants/{merchant_id}/stores",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # PATCH /stores/{id} to update VPA
    patch_resp = client.patch(
        f"/api/v1/stores/{store_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"upi_vpa": "retail_blr01_new@okaxis"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["upi_vpa"] == "retail_blr01_new@okaxis"


def test_staff_assignment_and_rbac_integration(client: TestClient, auth_owner, db: Session):
    owner_token = auth_owner["token"]
    onboard_resp = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "business_name": "Staffed Enterprise",
            "legal_name": "Staffed Enterprise Ltd",
            "email": f"staffed_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+919876543266",
            "pan": "ABCDE1234F",
            "mcc_code": "5411",
        },
    )
    merchant_id = onboard_resp.json()["id"]

    # Register a new user to assign as cashier
    cashier_email = f"cashier_{uuid.uuid4().hex[:8]}@example.com"
    cashier_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": cashier_email,
            "password": "CashierPassword123!",
            "full_name": "Cashier Bob",
        },
    )
    cashier_user_id = cashier_reg.json()["user"]["id"]
    cashier_token = cashier_reg.json()["tokens"]["access_token"]

    # Assign user as Cashier
    assign_resp = client.post(
        f"/api/v1/merchants/{merchant_id}/staff",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "user_id": cashier_user_id,
            "role": "CASHIER",
        },
    )
    assert assign_resp.status_code == 201, assign_resp.text
    assert assign_resp.json()["role"] == "CASHIER"

    # Verify Cashier can read invoices
    inv_resp = client.get(
        f"/api/v1/rbac/merchants/{merchant_id}/invoices",
        headers={"Authorization": f"Bearer {cashier_token}"},
    )
    assert inv_resp.status_code == 200

    # Verify Cashier cannot trigger refunds (403)
    refund_resp = client.post(
        f"/api/v1/rbac/merchants/{merchant_id}/refunds",
        headers={"Authorization": f"Bearer {cashier_token}"},
    )
    assert refund_resp.status_code == 403
    assert refund_resp.json()["code"] == "FORBIDDEN"
