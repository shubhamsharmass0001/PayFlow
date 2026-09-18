"""Refunds Module Routes.

Endpoints:
  POST   /transactions/{id}/refunds           → initiate refund (payments:write)
  PATCH  /refunds/{id}/approve                → approve refund (refunds:approve — Manager/Owner only)
  GET    /refunds/{id}                        → get refund detail (payments:read)
  GET    /merchants/{id}/refunds              → list refunds for merchant (payments:read)
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.payments.models import PaymentTransaction
from app.modules.refunds.models import RefundStatus
from app.modules.refunds.schemas import RefundApproveRequest, RefundCreate, RefundResponse
from app.modules.refunds.service import RefundService
from app.core.security import get_current_user
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Refunds"])


@router.post(
    "/transactions/{id}/refunds",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate a refund against a SUCCESS transaction",
)
def initiate_refund(
    id: uuid.UUID,
    payload: RefundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a refund in INITIATED status.

    - amount must be ≤ (transaction.amount − already refunded).
    - Partial refunds are valid: multiple refunds on one transaction are allowed
      as long as cumulative amount ≤ original transaction amount.
    - Requires 'payments:write' permission for the transaction's merchant.
    """
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == id).first()
    if not tx:
        raise EntityNotFoundException("PaymentTransaction", id)

    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=tx.merchant_id,
        permission_code="payments:write",
    )

    return RefundService.initiate_refund(
        db=db,
        transaction_id=id,
        payload=payload,
        actor=current_user,
    )


@router.patch(
    "/refunds/{id}/approve",
    response_model=RefundResponse,
    summary="Approve a pending refund (Manager/Owner only)",
)
def approve_refund(
    id: uuid.UUID,
    body: RefundApproveRequest = RefundApproveRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approves a refund in INITIATED status, triggering MockUPIProvider simulation.

    - Gated to Manager/Owner ('refunds:approve' permission).
    - Transitions: INITIATED → PENDING → REFUNDED | PARTIALLY_REFUNDED | REFUND_FAILED.
    - Appends status history on parent transaction for every transition.
    - Dispatches outbound webhook on completion.
    """
    from app.modules.refunds.models import Refund

    refund = db.query(Refund).filter(Refund.id == id).first()
    if not refund:
        raise EntityNotFoundException("Refund", id)

    # RBAC: Manager/Owner only — 'refunds:approve'
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=refund.merchant_id,
        permission_code="refunds:approve",
    )

    return RefundService.approve_refund(
        db=db,
        refund_id=id,
        actor=current_user,
        notes=body.notes,
    )


@router.get(
    "/refunds/{id}",
    response_model=RefundResponse,
    summary="Get refund detail by ID",
)
def get_refund(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns full detail for a single refund record."""
    refund = RefundService.get_refund_by_id(db=db, refund_id=id)

    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=refund.merchant_id,
        permission_code="payments:read",
    )
    return refund


@router.get(
    "/merchants/{id}/refunds",
    response_model=PaginatedResponse[RefundResponse],
    summary="List refunds for a merchant with optional filters",
)
def list_merchant_refunds(
    id: uuid.UUID,
    refund_status: Optional[RefundStatus] = Query(
        None,
        alias="status",
        description="Filter by refund status (INITIATED, PENDING, SUCCESS, FAILED)",
    ),
    transaction_id: Optional[uuid.UUID] = Query(
        None,
        description="Filter refunds belonging to a specific transaction",
    ),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payments:read")),
):
    """Paginated list of refunds scoped to a merchant.

    Optional filters: status, transaction_id.
    """
    return RefundService.list_merchant_refunds(
        db=db,
        merchant_id=id,
        pagination=pagination,
        status=refund_status,
        transaction_id=transaction_id,
    )
