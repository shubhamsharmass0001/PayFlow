"""Analytics Module Schemas.

Models for analytics overview, revenue trends (formatted for fl_chart),
and payment method breakdown by status.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class GranularityEnum(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


# ---------------------------------------------------------------------------
# Overview Schemas
# ---------------------------------------------------------------------------

class AnalyticsOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: uuid.UUID
    # Collections over standard business intervals
    today_collections: Decimal = Field(default=Decimal("0.00"), description="Total SUCCESS collections for today (UTC)")
    this_week_collections: Decimal = Field(default=Decimal("0.00"), description="Total SUCCESS collections for current week (Mon-Sun UTC)")
    this_month_collections: Decimal = Field(default=Decimal("0.00"), description="Total SUCCESS collections for current calendar month (UTC)")
    
    # Transaction counts
    today_transaction_count: int = Field(default=0, description="Count of SUCCESS transactions today")
    this_week_transaction_count: int = Field(default=0, description="Count of SUCCESS transactions this week")
    this_month_transaction_count: int = Field(default=0, description="Count of SUCCESS transactions this month")

    # Operational KPI rates
    success_rate: float = Field(default=0.0, description="Percentage of terminal transactions that succeeded (0.0 to 100.0)")
    pending_count: int = Field(default=0, description="Number of transactions currently in PENDING or INITIATED state")
    average_transaction_value: Decimal = Field(default=Decimal("0.00"), description="Average gross amount across successful transactions")
    unresolved_duplicate_flags_count: int = Field(default=0, description="Number of unresolved duplicate transaction flags")


# ---------------------------------------------------------------------------
# Revenue Trend Schemas (for mobile fl_chart)
# ---------------------------------------------------------------------------

class RevenueTrendPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    index: int = Field(..., description="0-indexed sequential position for FlSpot(index, amount)")
    period: str = Field(..., description="ISO period key (e.g. '2026-09-18', '2026-W38', '2026-09')")
    label: str = Field(..., description="Human-readable bottom-axis label (e.g. '18 Sep', 'Week 38', 'Sep 2026')")
    amount: Decimal = Field(default=Decimal("0.00"), description="Total collections in this bucket")
    transaction_count: int = Field(default=0, description="Number of successful transactions in this bucket")


class RevenueTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: uuid.UUID
    granularity: str
    from_date: date
    to_date: date
    total_revenue: Decimal
    total_transactions: int
    points: List[RevenueTrendPoint]


# ---------------------------------------------------------------------------
# Payment Methods Breakdown Schemas
# ---------------------------------------------------------------------------

class PaymentMethodBreakdownItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_method: str
    status: str
    count: int
    total_amount: Decimal
    percentage_of_total_count: float
    percentage_of_total_volume: float


class PaymentMethodSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_method: str
    total_count: int
    total_amount: Decimal
    success_count: int
    success_amount: Decimal
    failed_count: int
    pending_count: int
    volume_percentage: float
    count_percentage: float


class PaymentMethodsAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: uuid.UUID
    total_transactions: int
    total_volume: Decimal
    breakdown: List[PaymentMethodBreakdownItem]
    methods_summary: List[PaymentMethodSummary]
