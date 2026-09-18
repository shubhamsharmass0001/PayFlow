"""Audit Module API Routes.

Endpoints:
  GET /merchants/{id}/audit-logs  → List & filter merchant audit logs (Auditor/Owner-only)
  GET /audit-logs/{id}           → Detail view with formatted before/after JSON diff (Auditor/Owner-only)
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.audit.models import AuditAction, AuditLog
from app.modules.audit.schemas import (
    AuditLogDetailResponse,
    AuditLogListItemResponse,
)
from app.modules.audit.service import AuditService
from app.modules.auth.models import User
from app.modules.rbac.dependencies import verify_auditor_or_owner_access
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Audit Logs"])


def _parse_dt(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    try:
        cleaned = str(val).strip().replace(" ", "+")
        return datetime.fromisoformat(cleaned)
    except Exception:
        return None


@router.get(
    "/merchants/{id}/audit-logs",
    response_model=PaginatedResponse[AuditLogListItemResponse],
    status_code=status.HTTP_200_OK,
    summary="List merchant audit logs with filters (Auditor/Owner-only)",
)
def list_merchant_audit_logs(
    id: uuid.UUID,
    actor_user_id: Optional[uuid.UUID] = Query(
        None,
        description="Filter by user UUID who initiated the action",
    ),
    entity_type: Optional[str] = Query(
        None,
        description="Filter by entity type (e.g. 'invoices', 'customers', 'merchants')",
    ),
    action: Optional[AuditAction] = Query(
        None,
        description="Filter by mutation action (CREATE, UPDATE, DELETE, etc.)",
    ),
    from_date: Optional[str] = Query(
        None,
        description="Filter audit logs created on or after this timestamp (ISO-8601)",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Alias for from_date",
    ),
    to_date: Optional[str] = Query(
        None,
        description="Filter audit logs created on or before this timestamp (ISO-8601)",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Alias for to_date",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves paginated audit logs for a merchant organization.

    - **RBAC**: Restricted to **Owner** and **Auditor** roles only.
    - Supports filtering by actor_user_id, entity_type, action, and date range.
    """
    # Enforce Auditor/Owner-only access for this merchant
    verify_auditor_or_owner_access(db=db, user=current_user, merchant_id=id)

    raw_from = from_date or start_date
    raw_to = to_date or end_date
    effective_from = _parse_dt(raw_from)
    effective_to = _parse_dt(raw_to)
    pagination_params = PaginationParams(page=page, page_size=page_size)

    items, total = AuditService.list_merchant_audit_logs(
        db=db,
        merchant_id=id,
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        action=action,
        from_date=effective_from,
        to_date=effective_to,
        pagination_params=pagination_params,
    )

    return PaginatedResponse.create(items=items, total=total, params=pagination_params)


@router.get(
    "/audit-logs/{id}",
    response_model=AuditLogDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single audit log with formatted before/after JSON diff",
)
def get_audit_log_detail(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetches full details of an audit log entry.

    - Returns complete before and after states along with a structured field-level diff.
    - **RBAC**: Restricted to **Owner** and **Auditor** roles of the affected merchant.
    """
    detail = AuditService.get_audit_log_detail(db=db, audit_id=id)

    if detail.merchant_id:
        verify_auditor_or_owner_access(
            db=db,
            user=current_user,
            merchant_id=detail.merchant_id,
        )

    return detail
