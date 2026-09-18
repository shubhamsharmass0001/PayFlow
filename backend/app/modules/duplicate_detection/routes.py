"""Duplicate Detection Module API Routes."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.duplicate_detection.models import (
    DuplicateFlagStatus,
    DuplicateTransactionFlag,
)
from app.modules.duplicate_detection.schemas import (
    DuplicateFlagResponse,
    DuplicateFlagSummaryResponse,
    ResolveDuplicateFlagRequest,
)
from app.modules.duplicate_detection.service import DuplicateDetectionService
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Duplicate Detection"])


@router.patch(
    "/duplicate-flags/{id}/resolve",
    response_model=DuplicateFlagResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark a duplicate transaction flag as resolved",
)
def resolve_duplicate_flag(
    id: uuid.UUID,
    payload: ResolveDuplicateFlagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marks a duplicate transaction flag resolved with an explanation reason."""
    flag = db.query(DuplicateTransactionFlag).filter(DuplicateTransactionFlag.id == id).first()
    if not flag:
        raise EntityNotFoundException("DuplicateTransactionFlag", id)

    # Verify merchant permission
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=flag.merchant_id,
        permission_code="payments:write",
    )

    return DuplicateDetectionService.resolve_flag(
        db=db,
        flag_id=id,
        reason=payload.reason,
        resolved_by=payload.resolved_by,
        actor=current_user,
    )


@router.get(
    "/merchants/{id}/duplicate-flags",
    response_model=PaginatedResponse[DuplicateFlagResponse],
    summary="List duplicate transaction flags for a merchant",
)
def list_merchant_duplicate_flags(
    id: uuid.UUID,
    status: Optional[DuplicateFlagStatus] = Query(None, description="Filter by flag status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payments:read")),
):
    """Retrieves paginated duplicate flags for a merchant."""
    pagination = PaginationParams(page=page, page_size=page_size)
    return DuplicateDetectionService.list_flags(
        db=db,
        merchant_id=id,
        pagination=pagination,
        status=status,
    )


@router.get(
    "/merchants/{id}/duplicate-flags/summary",
    response_model=DuplicateFlagSummaryResponse,
    summary="Get count of unresolved duplicate flags for a merchant",
)
def get_merchant_duplicate_flags_summary(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payments:read")),
):
    """Returns the total number of unresolved duplicate flags for a merchant."""
    count = DuplicateDetectionService.get_unresolved_count(db=db, merchant_id=id)
    return DuplicateFlagSummaryResponse(
        merchant_id=id,
        unresolved_count=count,
    )
