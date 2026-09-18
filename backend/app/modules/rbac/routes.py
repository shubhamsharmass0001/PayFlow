import uuid
from fastapi import APIRouter, Depends, status
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.get(
    "/merchants/{merchant_id}/invoices",
    summary="Example route requiring invoices:read permission",
)
def read_merchant_invoices(
    merchant_id: uuid.UUID,
    user: User = Depends(require_permission("invoices:read")),
):
    return {
        "status": "success",
        "message": f"User {user.email} authorized to read invoices for merchant {merchant_id}",
        "merchant_id": str(merchant_id),
    }


@router.post(
    "/merchants/{merchant_id}/refunds",
    status_code=status.HTTP_201_CREATED,
    summary="Example route requiring refunds:write permission",
)
def create_merchant_refund(
    merchant_id: uuid.UUID,
    user: User = Depends(require_permission("refunds:write")),
):
    return {
        "status": "success",
        "message": f"User {user.email} authorized to trigger refunds for merchant {merchant_id}",
        "merchant_id": str(merchant_id),
    }
