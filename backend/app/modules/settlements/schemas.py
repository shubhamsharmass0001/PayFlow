"""Settlements Module Pydantic Schemas.

Response shapes are designed for direct consumption by the Flutter settlement
screen (Phase 23). They are pre-aggregated so the client never has to reduce
raw rows: the list endpoint returns chart-ready series and the detail endpoint
returns structured line items.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.modules.settlements.models import SettlementCycle, SettlementStatus


# ---------------------------------------------------------------------------
# Line item (per-transaction breakdown within a settlement)
# ---------------------------------------------------------------------------

class SettlementLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    settlement_id: uuid.UUID
    transaction_id: uuid.UUID
    amount: Decimal            # Gross transaction amount
    fee_amount: Decimal        # MDR fee deducted (illustrative)
    tax_amount: Decimal        # GST on MDR (illustrative)
    net_amount: Decimal        # Amount credited to merchant
    created_at: datetime


# ---------------------------------------------------------------------------
# Settlement summary (list view) — chart/series-ready
# ---------------------------------------------------------------------------

class SettlementSummaryResponse(BaseModel):
    """Compact settlement representation for list views and chart series.

    All monetary aggregates are pre-computed so the Flutter chart widget can
    render a time-series without any client-side reduction.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    settlement_date: date
    settlement_cycle: SettlementCycle
    status: SettlementStatus

    # Pre-aggregated financial fields
    transaction_count: int
    gross_amount: Decimal      # Sum of transaction amounts
    mdr_amount: Decimal        # Total MDR deducted (mock, illustrative)
    tax_on_mdr: Decimal        # GST on MDR @ 18% (illustrative)
    net_amount: Decimal        # Credited to merchant = gross - mdr - tax_on_mdr

    # Payout reference
    utr_reference: Optional[str] = None   # Mock UTR — illustrative only
    settled_at: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Settlement detail (includes line items)
# ---------------------------------------------------------------------------

class SettlementDetailResponse(SettlementSummaryResponse):
    """Full settlement detail including per-transaction line items.

    Consumed by the settlement detail screen and the Flutter settlement
    drill-down view.
    """
    line_items: List[SettlementLineItemResponse] = []


# ---------------------------------------------------------------------------
# Chart series helpers (returned by the list endpoint alongside paginated rows)
# ---------------------------------------------------------------------------

class SettlementChartPoint(BaseModel):
    """Single point in a settlement time series suitable for a bar/line chart."""
    settlement_date: date
    gross_amount: Decimal
    net_amount: Decimal
    mdr_amount: Decimal
    transaction_count: int


class SettlementListResponse(BaseModel):
    """Top-level list response wrapping paginated items + pre-built chart series.

    The `series` field is the same data aggregated by date so the Flutter
    settlement screen can render a chart without an extra API call.
    """
    items: List[SettlementSummaryResponse]
    total: int
    page: int
    page_size: int
    series: List[SettlementChartPoint]  # Chart-ready time series
    # Running totals for the current page/filter window
    window_gross: Decimal
    window_net: Decimal
    window_mdr: Decimal
    window_transaction_count: int
