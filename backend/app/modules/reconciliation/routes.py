"""Reconciliation Module API Routes."""
import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.modules.reconciliation.models import MatchStatus, ReconciliationStatus
from app.modules.reconciliation.schemas import (
    ReconciliationBatchResponse,
    ReconciliationEntryResponse,
    ReconciliationRunRequest,
)
from app.modules.reconciliation.service import ReconciliationService
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Reconciliation"])


@router.post(
    "/merchants/{id}/reconciliation/run",
    response_model=ReconciliationBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute an on-demand reconciliation run for a merchant",
)
def run_merchant_reconciliation(
    id: uuid.UUID,
    payload: Optional[ReconciliationRunRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settlements:write")),
):
    """Executes a reconciliation job comparing captured SUCCESS transactions against

    settlement records for the specified merchant and window.
    """
    return ReconciliationService.run_reconciliation(
        db=db,
        merchant_id=id,
        request=payload,
        actor_id=current_user.id,
    )


@router.get(
    "/merchants/{id}/reconciliation/batches",
    response_model=PaginatedResponse[ReconciliationBatchResponse],
    summary="List reconciliation batches for a merchant",
)
def list_merchant_reconciliation_batches(
    id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    from_date: Optional[date] = Query(None, description="Filter batches on or after date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter batches on or before date (YYYY-MM-DD)"),
    status: Optional[ReconciliationStatus] = Query(None, description="Filter by batch status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settlements:read")),
):
    """Retrieves paginated history of reconciliation batches for the specified merchant."""
    pagination = PaginationParams(page=page, page_size=page_size)
    return ReconciliationService.list_merchant_batches(
        db=db,
        merchant_id=id,
        pagination_params=pagination,
        from_date=from_date,
        to_date=to_date,
        status=status,
    )


@router.get(
    "/reconciliation/batches/{id}/entries",
    response_model=PaginatedResponse[ReconciliationEntryResponse],
    summary="List transaction entries for a reconciliation batch",
)
def get_reconciliation_batch_entries(
    id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    match_status: Optional[MatchStatus] = Query(
        None,
        description="Filter entries by match status (MATCHED, UNMATCHED, MANUAL_REVIEW)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves paginated line items for a reconciliation batch, filterable by match_status."""
    pagination = PaginationParams(page=page, page_size=page_size)
    batch, entries = ReconciliationService.get_batch_entries(
        db=db,
        batch_id=id,
        pagination_params=pagination,
        match_status=match_status,
    )

    # Enforce merchant-scoped authorization
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=batch.merchant_id,
        permission_code="settlements:read",
    )

    return entries
