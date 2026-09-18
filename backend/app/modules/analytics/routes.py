"""Analytics Module Routes.

Exposes endpoints for merchant dashboard metrics, time-series revenue trend
visualizations (for mobile fl_chart), and payment method breakdowns.
"""

from datetime import date
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission
from app.modules.analytics.schemas import (
    AnalyticsOverviewResponse,
    GranularityEnum,
    PaymentMethodsAnalyticsResponse,
    RevenueTrendResponse,
)
from app.modules.analytics.service import AnalyticsService

router = APIRouter(tags=["Analytics"])


@router.get(
    "/merchants/{id}/analytics/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get merchant analytics overview metrics",
    description=(
        "Returns aggregated collections for today, this-week, and this-month, "
        "success rate %, pending transaction count, and average transaction value (ATV). "
        "Cached in Redis for 60 seconds."
    ),
)
def get_analytics_overview(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("payments:read")),
):
    return AnalyticsService.get_overview(db=db, merchant_id=id)


@router.get(
    "/merchants/{id}/analytics/revenue-trend",
    response_model=RevenueTrendResponse,
    summary="Get time-series revenue trend for mobile fl_chart",
    description=(
        "Returns time-series revenue aggregated by day, week, or month. "
        "Points include an index, formatted label, period, and amount, ready "
        "to feed directly into Flutter fl_chart FlSpot(index, amount) without reduction."
    ),
)
def get_revenue_trend(
    id: uuid.UUID,
    granularity: GranularityEnum = Query(GranularityEnum.DAY, description="Time bucket: day, week, month"),
    from_param: Optional[date] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_param: Optional[date] = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    from_date: Optional[date] = Query(None, description="Start date alias"),
    to_date: Optional[date] = Query(None, description="End date alias"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("payments:read")),
):
    effective_from = from_param or from_date
    effective_to = to_param or to_date
    return AnalyticsService.get_revenue_trend(
        db=db,
        merchant_id=id,
        granularity=granularity,
        from_date=effective_from,
        to_date=effective_to,
    )


@router.get(
    "/merchants/{id}/analytics/payment-methods",
    response_model=PaymentMethodsAnalyticsResponse,
    summary="Get payment methods distribution and status breakdown",
    description=(
        "Returns payment method breakdowns with counts, volume, and percentage share, "
        "as well as a granular method-status cross-tabulation. Cached in Redis for 60 seconds."
    ),
)
def get_payment_methods(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("payments:read")),
):
    return AnalyticsService.get_payment_methods(db=db, merchant_id=id)
