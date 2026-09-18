import os
import re
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.merchants.models import (
    KycDocumentStatus,
    KycDocumentType,
    KycStatus,
    Merchant,
    MerchantKycDocument,
    MerchantStaff,
    RiskTier,
    StaffRole,
)
from app.modules.merchants.schemas import (
    KycDocumentResponse,
    MerchantDetailResponse,
    MerchantOnboardRequest,
    MerchantResponse,
    MerchantUpdateRequest,
    StaffAssignRequest,
    StaffResponse,
)
from app.modules.rbac.models import Role, UserRole
from app.modules.rbac.seed import seed_rbac_data
from app.modules.stores.models import Store
from app.shared.exceptions import (
    BadRequestException,
    ConflictException,
    EntityNotFoundException,
)

UPLOAD_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
)


def onboard_merchant(
    db: Session,
    request: MerchantOnboardRequest,
    creator: User,
) -> MerchantResponse:
    """Onboards a new merchant, registers initial KYC documents, assigns creator as Owner,

    and writes an audit log entry.
    """
    existing_merchant = db.query(Merchant).filter(Merchant.email == request.email).first()
    if existing_merchant:
        raise ConflictException(
            message=f"Merchant with email '{request.email}' already exists",
            code="MERCHANT_EMAIL_EXISTS",
        )

    merchant = Merchant(
        business_name=request.business_name,
        legal_name=request.legal_name,
        email=request.email,
        phone=request.phone,
        kyc_status=KycStatus.PENDING,
        upi_vpa=request.initial_upi_vpa,
        mcc_code=request.mcc_code,
        risk_tier=RiskTier.MEDIUM,
        is_active=True,
    )
    db.add(merchant)
    db.flush()

    # Seed RBAC roles if not already present
    seed_rbac_data(db)
    owner_role = db.query(Role).filter(Role.name == "Owner").first()

    # Assign creator as Owner in RBAC user_roles
    user_role = UserRole(
        user_id=creator.id,
        role_id=owner_role.id,
        merchant_id=merchant.id,
    )
    db.add(user_role)

    # Assign creator as Owner in merchant_staff
    staff = MerchantStaff(
        merchant_id=merchant.id,
        user_id=creator.id,
        role=StaffRole.OWNER,
        is_active=True,
    )
    db.add(staff)

    # Register PAN document placeholder
    pan_doc = MerchantKycDocument(
        merchant_id=merchant.id,
        document_type=KycDocumentType.PAN,
        document_number=request.pan,
        file_url="pending_upload",
        status=KycDocumentStatus.SUBMITTED,
    )
    db.add(pan_doc)

    # Register GSTIN document placeholder if provided
    if request.gstin:
        gstin_doc = MerchantKycDocument(
            merchant_id=merchant.id,
            document_type=KycDocumentType.GSTIN,
            document_number=request.gstin,
            file_url="pending_upload",
            status=KycDocumentStatus.SUBMITTED,
        )
        db.add(gstin_doc)

    db.flush()

    # Record Audit Entry
    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="merchants",
        entity_id=merchant.id,
        actor_id=creator.id,
        merchant_id=merchant.id,
        after={
            "id": str(merchant.id),
            "business_name": merchant.business_name,
            "legal_name": merchant.legal_name,
            "email": merchant.email,
            "kyc_status": merchant.kyc_status.value,
            "pan": request.pan,
            "gstin": request.gstin,
        },
    )

    db.commit()
    db.refresh(merchant)
    return MerchantResponse.model_validate(merchant)


async def upload_kyc_document(
    db: Session,
    merchant_id: uuid.UUID,
    file: UploadFile,
    document_type: KycDocumentType,
    document_number: str,
    notes: Optional[str],
    actor: User,
) -> KycDocumentResponse:
    """Saves a KYC verification document to local disk and logs metadata."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None)).first()
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    # Sanitize filename and create storage directory
    safe_filename = re.sub(r"[^\w\.-]", "_", file.filename or "kyc_document")
    merchant_dir = os.path.join(UPLOAD_BASE_DIR, str(merchant_id))
    os.makedirs(merchant_dir, exist_ok=True)

    file_path = os.path.join(merchant_dir, safe_filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{merchant_id}/{safe_filename}"

    # Upsert or create KYC document entry
    kyc_doc = (
        db.query(MerchantKycDocument)
        .filter(
            MerchantKycDocument.merchant_id == merchant_id,
            MerchantKycDocument.document_type == document_type,
        )
        .first()
    )

    if kyc_doc:
        kyc_doc.document_number = document_number
        kyc_doc.file_url = file_url
        kyc_doc.status = KycDocumentStatus.SUBMITTED
        kyc_doc.notes = notes
    else:
        kyc_doc = MerchantKycDocument(
            merchant_id=merchant_id,
            document_type=document_type,
            document_number=document_number,
            file_url=file_url,
            status=KycDocumentStatus.SUBMITTED,
            notes=notes,
        )
        db.add(kyc_doc)

    db.flush()

    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="merchant_kyc_documents",
        entity_id=kyc_doc.id,
        actor_id=actor.id,
        merchant_id=merchant_id,
        after={
            "document_type": document_type.value,
            "document_number": document_number,
            "file_url": file_url,
            "status": kyc_doc.status.value,
        },
    )

    db.commit()
    db.refresh(kyc_doc)
    return KycDocumentResponse.model_validate(kyc_doc)


def update_merchant_profile(
    db: Session,
    merchant_id: uuid.UUID,
    request: MerchantUpdateRequest,
    actor: User,
) -> MerchantResponse:
    """Updates editable merchant profile fields with before/after audit tracking."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None)).first()
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    before_state = {
        "business_name": merchant.business_name,
        "legal_name": merchant.legal_name,
        "phone": merchant.phone,
        "upi_vpa": merchant.upi_vpa,
        "mcc_code": merchant.mcc_code,
    }

    if request.business_name is not None:
        merchant.business_name = request.business_name
    if request.legal_name is not None:
        merchant.legal_name = request.legal_name
    if request.phone is not None:
        merchant.phone = request.phone
    if request.upi_vpa is not None:
        merchant.upi_vpa = request.upi_vpa
    if request.mcc_code is not None:
        merchant.mcc_code = request.mcc_code

    db.flush()

    after_state = {
        "business_name": merchant.business_name,
        "legal_name": merchant.legal_name,
        "phone": merchant.phone,
        "upi_vpa": merchant.upi_vpa,
        "mcc_code": merchant.mcc_code,
    }

    record_audit(
        db=db,
        action=AuditAction.UPDATE,
        entity_name="merchants",
        entity_id=merchant.id,
        actor_id=actor.id,
        merchant_id=merchant.id,
        before=before_state,
        after=after_state,
    )

    db.commit()
    db.refresh(merchant)
    return MerchantResponse.model_validate(merchant)


def get_merchant_detail(db: Session, merchant_id: uuid.UUID) -> MerchantDetailResponse:
    """Retrieves merchant profile and KYC verification summary."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None)).first()
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    kyc_docs = (
        db.query(MerchantKycDocument)
        .filter(MerchantKycDocument.merchant_id == merchant_id)
        .order_by(MerchantKycDocument.created_at.asc())
        .all()
    )

    return MerchantDetailResponse(
        merchant=MerchantResponse.model_validate(merchant),
        kyc_documents=[KycDocumentResponse.model_validate(doc) for doc in kyc_docs],
    )


def list_merchant_staff(db: Session, merchant_id: uuid.UUID) -> List[StaffResponse]:
    """Lists all staff members assigned to the merchant."""
    staff_records = (
        db.query(MerchantStaff, User)
        .join(User, User.id == MerchantStaff.user_id)
        .filter(MerchantStaff.merchant_id == merchant_id)
        .all()
    )

    responses = []
    for staff, user in staff_records:
        responses.append(
            StaffResponse(
                id=staff.id,
                merchant_id=staff.merchant_id,
                user_id=user.id,
                user_email=user.email,
                user_name=user.full_name,
                store_id=staff.store_id,
                role=staff.role,
                is_active=staff.is_active,
                created_at=staff.created_at,
            )
        )
    return responses


def assign_merchant_staff(
    db: Session,
    merchant_id: uuid.UUID,
    request: StaffAssignRequest,
    actor: User,
) -> StaffResponse:
    """Assigns or updates a user's role in the merchant organization and synchronizes RBAC."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None)).first()
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    # Find user by ID or email
    user = None
    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id, User.deleted_at.is_(None)).first()
    elif request.email:
        user = db.query(User).filter(User.email == request.email, User.deleted_at.is_(None)).first()

    if not user:
        raise BadRequestException(
            message="Target user not found. Please provide a valid user_id or registered email.",
            code="USER_NOT_FOUND",
        )

    # Validate store if specified
    if request.store_id:
        store = (
            db.query(Store)
            .filter(
                Store.id == request.store_id,
                Store.merchant_id == merchant_id,
                Store.deleted_at.is_(None),
            )
            .first()
        )
        if not store:
            raise BadRequestException(
                message=f"Store '{request.store_id}' was not found for this merchant.",
                code="STORE_NOT_FOUND",
            )

    # Map StaffRole to corresponding RBAC Role name
    staff_to_rbac_role = {
        StaffRole.OWNER: "Owner",
        StaffRole.ADMIN: "Manager",
        StaffRole.MANAGER: "Manager",
        StaffRole.CASHIER: "Cashier",
        StaffRole.ACCOUNTANT: "Auditor",
    }
    rbac_role_name = staff_to_rbac_role[request.role]
    seed_rbac_data(db)
    rbac_role = db.query(Role).filter(Role.name == rbac_role_name).first()

    # Upsert MerchantStaff
    staff = (
        db.query(MerchantStaff)
        .filter(
            MerchantStaff.merchant_id == merchant_id,
            MerchantStaff.user_id == user.id,
        )
        .first()
    )

    action = AuditAction.UPDATE if staff else AuditAction.CREATE
    before_state = {"role": staff.role.value, "store_id": str(staff.store_id)} if staff else None

    if staff:
        staff.role = request.role
        staff.store_id = request.store_id
        staff.is_active = True
    else:
        staff = MerchantStaff(
            merchant_id=merchant_id,
            user_id=user.id,
            store_id=request.store_id,
            role=request.role,
            is_active=True,
        )
        db.add(staff)

    # Synchronize RBAC user_roles for this merchant
    user_role = (
        db.query(UserRole)
        .filter(
            UserRole.merchant_id == merchant_id,
            UserRole.user_id == user.id,
        )
        .first()
    )
    if user_role:
        user_role.role_id = rbac_role.id
    else:
        db.add(
            UserRole(
                user_id=user.id,
                role_id=rbac_role.id,
                merchant_id=merchant_id,
            )
        )

    db.flush()

    record_audit(
        db=db,
        action=action,
        entity_name="merchant_staff",
        entity_id=staff.id,
        actor_id=actor.id,
        merchant_id=merchant_id,
        before=before_state,
        after={
            "user_id": str(user.id),
            "role": request.role.value,
            "store_id": str(request.store_id) if request.store_id else None,
        },
    )

    db.commit()
    db.refresh(staff)

    return StaffResponse(
        id=staff.id,
        merchant_id=staff.merchant_id,
        user_id=user.id,
        user_email=user.email,
        user_name=user.full_name,
        store_id=staff.store_id,
        role=staff.role,
        is_active=staff.is_active,
        created_at=staff.created_at,
    )
