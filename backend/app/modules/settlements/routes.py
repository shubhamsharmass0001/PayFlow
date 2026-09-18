"""Settlements Module Routes.

Endpoints consumed by the Flutter settlement screen (Phase 23).
All responses are pre-aggregated so the client renders without reduction.

Endpoints:
  GET /merchants/{merchant_id}/settlements
      → SettlementListResponse (paginated + chart series + window totals)

  GET /settlements/{settlement_id}
      → SettlementDetailResponse (with per-transaction line items)
"""

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.modules.settlements.models import Settlement, SettlementStatus
from app.modules.settlements.schemas import SettlementDetailResponse, SettlementListResponse
from app.modules.settlements.service import SettlementService
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginationParams

router = APIRouter(tags=["settlements"])


@router.get(
    "/merchants/{merchant_id}/settlements",
    response_model=SettlementListResponse,
    summary="List merchant settlements (chart-ready)",
    description=(
        "Returns paginated settlement records for the merchant with pre-built chart series "
        "and window-level totals. One call gives the Flutter settlement screen everything it "
        "needs to render the list AND the chart without further aggregation.\n\n"
        "**Note:** Fee figures (MDR, GST-on-MDR) are illustrative mock values. "
        "UTR references are simulated and not real bank UTRs."
    ),
)
def list_merchant_settlements(
    merchant_id: uuid.UUID,
    from_date: Optional[date] = Query(None, description="Filter from this settlement date (inclusive)"),
    to_date: Optional[date] = Query(None, description="Filter up to this settlement date (inclusive)"),
    status: Optional[SettlementStatus] = Query(None, description="Filter by settlement status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission("settlements:read")),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return SettlementService.list_merchant_settlements(
        db=db,
        merchant_id=merchant_id,
        pagination=pagination,
        from_date=from_date,
        to_date=to_date,
        status=status,
    )


@router.get(
    "/settlements/{settlement_id}",
    response_model=SettlementDetailResponse,
    summary="Get settlement detail with line items",
    description=(
        "Returns a single settlement including all per-transaction line items. "
        "Use this for the settlement drill-down screen.\n\n"
        "**Note:** Fee figures (MDR, GST-on-MDR) are illustrative mock values."
    ),
)
def get_settlement(
    settlement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settlement = (
        db.query(Settlement)
        .options(joinedload(Settlement.line_items))
        .filter(Settlement.id == settlement_id)
        .first()
    )
    if not settlement:
        raise EntityNotFoundException("Settlement", settlement_id)

    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=settlement.merchant_id,
        permission_code="settlements:read",
    )
    return SettlementDetailResponse.model_validate(settlement)
