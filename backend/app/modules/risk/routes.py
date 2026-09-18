"""Risk Module API Routes.

Endpoints:
  GET   /merchants/{id}/risk/signals  → List & filter risk signals (severity/reviewed)
  PATCH /risk/signals/{id}/review     → Review and resolve a risk signal
  GET   /risk/rules                   → Explainable, auditable documentation for risk rules
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.dependencies import verify_merchant_permission
from app.modules.risk.models import RiskAction, RiskLevel, RiskSignal
from app.modules.risk.schemas import (
    ReviewRiskSignalRequest,
    RiskRulesDocumentationResponse,
    RiskSignalResponse,
)
from app.modules.risk.service import RiskService
from app.shared.exceptions import EntityNotFoundException, ForbiddenException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Risk & Compliance"])


@router.get(
    "/merchants/{id}/risk/signals",
    response_model=PaginatedResponse[RiskSignalResponse],
    status_code=status.HTTP_200_OK,
    summary="List merchant risk signals with severity & reviewed filters",
    description=(
        "Retrieves paginated risk signals raised for a merchant organization.\n\n"
        "### Auditable Risk Rules Evaluated:\n"
        "- **VELOCITY_SPIKE**: Burst in transaction count (>= 3x trailing hourly average) "
        "or transaction value (>= 5x historical average).\n"
        "- **ODD_HOUR**: Transactions occurring between 01:00 and 04:59 IST for merchants with normal daytime turnover.\n"
        "- **STRUCTURING_PATTERN**: Repeated transactions clustering in the ₹1,800.00 – ₹1,999.99 range "
        "designed to bypass 2FA / reporting thresholds, or rapid split payment structuring.\n"
        "- **GEO_MISMATCH**: Omitted per gateway design; device GPS is not captured at gateway level.\n\n"
        "**Filters Supported**:\n"
        "- `severity`: Filter by RiskLevel (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)\n"
        "- `reviewed`: Filter by reviewed status (`true` / `false`)\n"
        "- `rule`: Filter by rule name (e.g. `VELOCITY_SPIKE`, `ODD_HOUR`, `STRUCTURING_PATTERN`)"
    ),
)
def list_merchant_risk_signals(
    id: uuid.UUID,
    severity: Optional[RiskLevel] = Query(
        None,
        description="Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)",
    ),
    reviewed: Optional[bool] = Query(
        None,
        description="Filter by review status (true = resolved, false = pending review)",
    ),
    rule: Optional[str] = Query(
        None,
        alias="rule_triggered",
        description="Filter by rule name (e.g. VELOCITY_SPIKE, ODD_HOUR, STRUCTURING_PATTERN)",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists risk signals for merchant with RBAC enforcement."""
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=id,
        permission_code="payments:read",
    )

    pagination = PaginationParams(page=page, page_size=page_size)
    items, total = RiskService.list_merchant_risk_signals(
        db=db,
        merchant_id=id,
        severity=severity,
        reviewed=reviewed,
        rule_triggered=rule,
        pagination_params=pagination,
    )
    return PaginatedResponse.create(items=items, total=total, params=pagination)


@router.patch(
    "/risk/signals/{id}/review",
    response_model=RiskSignalResponse,
    status_code=status.HTTP_200_OK,
    summary="Review and resolve a risk signal with an auditable resolution note",
    description=(
        "Marks a raised risk signal as reviewed.\n\n"
        "- Requires **Manager** or **Owner** permission (`refunds:approve` / `payments:write`).\n"
        "- Appends reviewer identity and timestamp.\n"
        "- Creates an immutable audit trail entry in `audit_logs` table."
    ),
)
def review_risk_signal(
    id: uuid.UUID,
    payload: ReviewRiskSignalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reviews and resolves a risk signal."""
    signal = db.query(RiskSignal).filter(RiskSignal.id == id).first()
    if not signal:
        raise EntityNotFoundException("RiskSignal", id)

    # RBAC: Verify Manager or Owner permission for the affected merchant
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=signal.merchant_id,
        permission_code="refunds:approve",
    )

    return RiskService.review_signal(
        db=db,
        signal_id=id,
        resolution_note=payload.resolution_note,
        reviewed_by=payload.reviewed_by or current_user.id,
        action_taken=payload.action_taken,
        actor=current_user,
    )


@router.get(
    "/risk/rules",
    response_model=RiskRulesDocumentationResponse,
    status_code=status.HTTP_200_OK,
    summary="Explainable documentation of all active risk detection rules",
    description=(
        "Returns public/auditable documentation detailing every risk rule, "
        "its thresholds, mathematical rationale, and governance defaults."
    ),
)
def get_risk_rules_documentation():
    """Returns transparent documentation for all active risk rules."""
    return RiskService.get_documented_rules()
