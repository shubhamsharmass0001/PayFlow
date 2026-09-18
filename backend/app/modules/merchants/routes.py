import uuid
from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.merchants.models import KycDocumentType
from app.modules.merchants.schemas import (
    KycDocumentResponse,
    MerchantDetailResponse,
    MerchantOnboardRequest,
    MerchantResponse,
    MerchantUpdateRequest,
    StaffAssignRequest,
    StaffResponse,
)
from app.modules.merchants.service import (
    assign_merchant_staff,
    get_merchant_detail,
    list_merchant_staff,
    onboard_merchant,
    update_merchant_profile,
    upload_kyc_document,
)
from app.modules.rbac.dependencies import require_permission

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.post(
    "",
    response_model=MerchantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard a new merchant organization",
)
def onboard(
    payload: MerchantOnboardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return onboard_merchant(db=db, request=payload, creator=current_user)


@router.get(
    "/{id}",
    response_model=MerchantDetailResponse,
    summary="Retrieve merchant profile and KYC verification summary",
)
def get_merchant(
    id: uuid.UUID,
    user: User = Depends(require_permission("staff:read")),
    db: Session = Depends(get_db),
):
    return get_merchant_detail(db=db, merchant_id=id)


@router.patch(
    "/{id}",
    response_model=MerchantResponse,
    summary="Update merchant profile attributes",
)
def update_merchant(
    id: uuid.UUID,
    payload: MerchantUpdateRequest,
    user: User = Depends(require_permission("staff:write")),
    db: Session = Depends(get_db),
):
    return update_merchant_profile(db=db, merchant_id=id, request=payload, actor=user)


@router.post(
    "/{id}/kyc-documents",
    response_model=KycDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a KYC compliance verification document",
)
async def upload_document(
    id: uuid.UUID,
    file: UploadFile = File(..., description="Document scan/image file"),
    document_type: KycDocumentType = Form(..., description="Document type: PAN, GSTIN, etc."),
    document_number: str = Form(..., description="Official document identifier/number"),
    notes: Optional[str] = Form(None, description="Optional notes"),
    user: User = Depends(require_permission("staff:write")),
    db: Session = Depends(get_db),
):
    return await upload_kyc_document(
        db=db,
        merchant_id=id,
        file=file,
        document_type=document_type,
        document_number=document_number,
        notes=notes,
        actor=user,
    )


@router.get(
    "/{id}/staff",
    response_model=List[StaffResponse],
    summary="List staff members for a merchant",
)
def get_staff(
    id: uuid.UUID,
    user: User = Depends(require_permission("staff:read")),
    db: Session = Depends(get_db),
):
    return list_merchant_staff(db=db, merchant_id=id)


@router.post(
    "/{id}/staff",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite or assign a user to a merchant role and store",
)
def assign_staff(
    id: uuid.UUID,
    payload: StaffAssignRequest,
    user: User = Depends(require_permission("staff:write")),
    db: Session = Depends(get_db),
):
    return assign_merchant_staff(
        db=db,
        merchant_id=id,
        request=payload,
        actor=user,
    )
