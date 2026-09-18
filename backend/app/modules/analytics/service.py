"""Analytics Module Service.

Provides analytical queries and aggregations for merchant dashboards:
  1. Overview: today/this-week/this-month collections, success rate, pending count, ATV.
  2. Revenue Trend: time-series aggregated for mobile fl_chart (day, week, month).
  3. Payment Methods: volume and count breakdown by payment method and status.

Responses are cached in Redis with a 60-second TTL keyed by merchant_id + query params,
and automatically invalidated whenever a transaction reaches SUCCESS for that merchant.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional
import uuid
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.core import rate_limit as rate_limit_module
from app.core.logging import logger
from app.modules.analytics.schemas import (
    AnalyticsOverviewResponse,
    GranularityEnum,
    PaymentMethodBreakdownItem,
    PaymentMethodSummary,
    PaymentMethodsAnalyticsResponse,
    RevenueTrendPoint,
    RevenueTrendResponse,
)
from app.modules.duplicate_detection.service import DuplicateDetectionService
from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus

CACHE_TTL_SECONDS = 60


class AnalyticsService:

    # -----------------------------------------------------------------------
    # Caching Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _make_cache_key(merchant_id: uuid.UUID, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        param_str = json.dumps(params or {}, sort_keys=True, default=str)
        param_hash = hashlib.sha256(param_str.encode("utf-8")).hexdigest()[:12]
        return f"payflow:analytics:{merchant_id}:{endpoint}:{param_hash}"

    @classmethod
    def invalidate_cache(cls, merchant_id: uuid.UUID) -> None:
        """Invalidates all cached analytics responses for the specified merchant."""
        client = rate_limit_module.get_redis_client()
        if not client:
            return

        pattern = f"payflow:analytics:{merchant_id}:*"
        try:
            matched_keys = list(client.keys(pattern))
            if matched_keys:
                client.delete(*matched_keys)
                logger.info(
                    "analytics_cache_invalidated",
                    merchant_id=str(merchant_id),
                    keys_deleted=len(matched_keys),
                )
        except Exception as exc:
            logger.warning("analytics_cache_invalidation_error", merchant_id=str(merchant_id), error=str(exc))

    # -----------------------------------------------------------------------
    # 1. Overview
    # -----------------------------------------------------------------------

    @classmethod
    def get_overview(cls, db: Session, merchant_id: uuid.UUID) -> AnalyticsOverviewResponse:
        cache_key = cls._make_cache_key(merchant_id, "overview")
        client = rate_limit_module.get_redis_client()
        if client:
            try:
                cached = client.get(cache_key)
                if cached:
                    return AnalyticsOverviewResponse.model_validate_json(cached)
            except Exception as exc:
                logger.warning("analytics_cache_read_error", key=cache_key, error=str(exc))

        # Calculate time windows in UTC
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # Week starts on Monday
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Base filter: merchant transactions
        # Query collections and counts
        def _get_window_stats(start_dt: datetime):
            res = (
                db.query(
                    func.coalesce(func.sum(PaymentTransaction.amount), Decimal("0.00")),
                    func.count(PaymentTransaction.id),
                )
                .filter(
                    PaymentTransaction.merchant_id == merchant_id,
                    PaymentTransaction.status == TransactionStatus.SUCCESS,
                    PaymentTransaction.created_at >= start_dt,
                )
                .first()
            )
            return (res[0] or Decimal("0.00"), res[1] or 0) if res else (Decimal("0.00"), 0)

        today_amt, today_cnt = _get_window_stats(today_start)
        week_amt, week_cnt = _get_window_stats(week_start)
        month_amt, month_cnt = _get_window_stats(month_start)

        # Success Rate calculation:
        # Total terminal transactions: SUCCESS + FAILED + TIMEOUT
        terminal_stats = (
            db.query(
                func.count(PaymentTransaction.id).filter(PaymentTransaction.status == TransactionStatus.SUCCESS),
                func.count(PaymentTransaction.id).filter(
                    PaymentTransaction.status.in_([
                        TransactionStatus.SUCCESS,
                        TransactionStatus.FAILED,
                        TransactionStatus.TIMEOUT,
                    ])
                ),
            )
            .filter(PaymentTransaction.merchant_id == merchant_id)
            .first()
        )
        total_success = terminal_stats[0] if terminal_stats else 0
        total_terminal = terminal_stats[1] if terminal_stats else 0
        success_rate = round((total_success / total_terminal * 100.0), 2) if total_terminal > 0 else 100.0

        # Pending Count: PENDING or INITIATED
        pending_cnt = (
            db.query(func.count(PaymentTransaction.id))
            .filter(
                PaymentTransaction.merchant_id == merchant_id,
                PaymentTransaction.status.in_([
                    TransactionStatus.PENDING,
                    TransactionStatus.INITIATED,
                ]),
            )
            .scalar()
            or 0
        )

        # Average Transaction Value (ATV): total SUCCESS volume / total SUCCESS count
        all_success = (
            db.query(
                func.coalesce(func.sum(PaymentTransaction.amount), Decimal("0.00")),
                func.count(PaymentTransaction.id),
            )
            .filter(
                PaymentTransaction.merchant_id == merchant_id,
                PaymentTransaction.status == TransactionStatus.SUCCESS,
            )
            .first()
        )
        all_success_amt = all_success[0] or Decimal("0.00")
        all_success_cnt = all_success[1] or 0
        atv = (
            (all_success_amt / Decimal(all_success_cnt)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if all_success_cnt > 0
            else Decimal("0.00")
        )

        # Unresolved duplicate flags count
        try:
            unresolved_flags = DuplicateDetectionService.get_unresolved_count(db=db, merchant_id=merchant_id)
        except Exception:
            unresolved_flags = 0

        response = AnalyticsOverviewResponse(
            merchant_id=merchant_id,
            today_collections=today_amt,
            this_week_collections=week_amt,
            this_month_collections=month_amt,
            today_transaction_count=today_cnt,
            this_week_transaction_count=week_cnt,
            this_month_transaction_count=month_cnt,
            success_rate=success_rate,
            pending_count=pending_cnt,
            average_transaction_value=atv,
            unresolved_duplicate_flags_count=unresolved_flags,
        )

        # Cache in Redis
        if client:
            try:
                client.set(cache_key, response.model_dump_json(), ex=CACHE_TTL_SECONDS)
            except Exception as exc:
                logger.warning("analytics_cache_write_error", key=cache_key, error=str(exc))

        return response

    # -----------------------------------------------------------------------
    # 2. Revenue Trend (fl_chart ready)
    # -----------------------------------------------------------------------

    @classmethod
    def get_revenue_trend(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        granularity: GranularityEnum = GranularityEnum.DAY,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> RevenueTrendResponse:
        today = date.today()
        if to_date is None:
            to_date = today

        if from_date is None:
            if granularity == GranularityEnum.DAY:
                from_date = to_date - timedelta(days=29)  # 30 days
            elif granularity == GranularityEnum.WEEK:
                from_date = to_date - timedelta(weeks=11)  # 12 weeks
            elif granularity == GranularityEnum.MONTH:
                # 12 months roughly
                from_date = (to_date.replace(day=1) - timedelta(days=330)).replace(day=1)

        # Ensure order
        if from_date > to_date:
            from_date, to_date = to_date, from_date

        params = {
            "granularity": granularity.value,
            "from_date": str(from_date),
            "to_date": str(to_date),
        }
        cache_key = cls._make_cache_key(merchant_id, "revenue_trend", params)
        client = rate_limit_module.get_redis_client()
        if client:
            try:
                cached = client.get(cache_key)
                if cached:
                    return RevenueTrendResponse.model_validate_json(cached)
            except Exception as exc:
                logger.warning("analytics_cache_read_error", key=cache_key, error=str(exc))

        # Query all SUCCESS transactions in the date range
        from_dt = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)

        txs = (
            db.query(PaymentTransaction.created_at, PaymentTransaction.amount)
            .filter(
                PaymentTransaction.merchant_id == merchant_id,
                PaymentTransaction.status == TransactionStatus.SUCCESS,
                PaymentTransaction.created_at >= from_dt,
                PaymentTransaction.created_at <= to_dt,
            )
            .order_by(PaymentTransaction.created_at.asc())
            .all()
        )

        # Helper mapping to populate continuous buckets
        points: List[RevenueTrendPoint] = []
        total_revenue = Decimal("0.00")
        total_tx_count = 0

        if granularity == GranularityEnum.DAY:
            # Daily buckets
            day_map: Dict[str, Dict[str, Any]] = {}
            curr = from_date
            idx = 0
            while curr <= to_date:
                key = curr.isoformat()
                label = curr.strftime("%d %b")
                day_map[key] = {
                    "index": idx,
                    "period": key,
                    "label": label,
                    "amount": Decimal("0.00"),
                    "count": 0,
                }
                curr += timedelta(days=1)
                idx += 1

            for created_at, amount in txs:
                dt_key = created_at.date().isoformat()
                if dt_key in day_map:
                    day_map[dt_key]["amount"] += amount
                    day_map[dt_key]["count"] += 1
                    total_revenue += amount
                    total_tx_count += 1

            for key in sorted(day_map.keys()):
                d = day_map[key]
                points.append(
                    RevenueTrendPoint(
                        index=d["index"],
                        period=d["period"],
                        label=d["label"],
                        amount=d["amount"].quantize(Decimal("0.01")),
                        transaction_count=d["count"],
                    )
                )

        elif granularity == GranularityEnum.WEEK:
            # Weekly buckets (ISO calendar year and week)
            week_map: Dict[str, Dict[str, Any]] = {}
            curr = from_date
            # Align curr to Monday
            curr = curr - timedelta(days=curr.weekday())
            idx = 0
            while curr <= to_date:
                iso_year, iso_week, _ = curr.isocalendar()
                key = f"{iso_year}-W{iso_week:02d}"
                if key not in week_map:
                    week_map[key] = {
                        "index": idx,
                        "period": key,
                        "label": f"W{iso_week}",
                        "amount": Decimal("0.00"),
                        "count": 0,
                    }
                    idx += 1
                curr += timedelta(days=7)

            for created_at, amount in txs:
                iso_year, iso_week, _ = created_at.date().isocalendar()
                key = f"{iso_year}-W{iso_week:02d}"
                if key in week_map:
                    week_map[key]["amount"] += amount
                    week_map[key]["count"] += 1
                    total_revenue += amount
                    total_tx_count += 1

            for key in sorted(week_map.keys()):
                w = week_map[key]
                points.append(
                    RevenueTrendPoint(
                        index=w["index"],
                        period=w["period"],
                        label=w["label"],
                        amount=w["amount"].quantize(Decimal("0.01")),
                        transaction_count=w["count"],
                    )
                )

        elif granularity == GranularityEnum.MONTH:
            # Monthly buckets (YYYY-MM)
            month_map: Dict[str, Dict[str, Any]] = {}
            curr = from_date.replace(day=1)
            idx = 0
            while curr <= to_date:
                key = curr.strftime("%Y-%m")
                label = curr.strftime("%b %Y")
                if key not in month_map:
                    month_map[key] = {
                        "index": idx,
                        "period": key,
                        "label": label,
                        "amount": Decimal("0.00"),
                        "count": 0,
                    }
                    idx += 1
                # Advance one month
                next_month = curr.month + 1 if curr.month < 12 else 1
                next_year = curr.year if curr.month < 12 else curr.year + 1
                curr = date(next_year, next_month, 1)

            for created_at, amount in txs:
                key = created_at.date().strftime("%Y-%m")
                if key in month_map:
                    month_map[key]["amount"] += amount
                    month_map[key]["count"] += 1
                    total_revenue += amount
                    total_tx_count += 1

            for key in sorted(month_map.keys()):
                m = month_map[key]
                points.append(
                    RevenueTrendPoint(
                        index=m["index"],
                        period=m["period"],
                        label=m["label"],
                        amount=m["amount"].quantize(Decimal("0.01")),
                        transaction_count=m["count"],
                    )
                )

        response = RevenueTrendResponse(
            merchant_id=merchant_id,
            granularity=granularity.value,
            from_date=from_date,
            to_date=to_date,
            total_revenue=total_revenue.quantize(Decimal("0.01")),
            total_transactions=total_tx_count,
            points=points,
        )

        if client:
            try:
                client.set(cache_key, response.model_dump_json(), ex=CACHE_TTL_SECONDS)
            except Exception as exc:
                logger.warning("analytics_cache_write_error", key=cache_key, error=str(exc))

        return response

    # -----------------------------------------------------------------------
    # 3. Payment Methods Breakdown
    # -----------------------------------------------------------------------

    @classmethod
    def get_payment_methods(cls, db: Session, merchant_id: uuid.UUID) -> PaymentMethodsAnalyticsResponse:
        cache_key = cls._make_cache_key(merchant_id, "payment_methods")
        client = rate_limit_module.get_redis_client()
        if client:
            try:
                cached = client.get(cache_key)
                if cached:
                    return PaymentMethodsAnalyticsResponse.model_validate_json(cached)
            except Exception as exc:
                logger.warning("analytics_cache_read_error", key=cache_key, error=str(exc))

        # Query all transactions grouped by method and status
        rows = (
            db.query(
                PaymentTransaction.payment_method,
                PaymentTransaction.status,
                func.count(PaymentTransaction.id),
                func.coalesce(func.sum(PaymentTransaction.amount), Decimal("0.00")),
            )
            .filter(PaymentTransaction.merchant_id == merchant_id)
            .group_by(PaymentTransaction.payment_method, PaymentTransaction.status)
            .all()
        )

        total_transactions = sum(r[2] for r in rows) if rows else 0
        total_volume = sum((r[3] or Decimal("0.00")) for r in rows) if rows else Decimal("0.00")

        breakdown_items: List[PaymentMethodBreakdownItem] = []
        method_map: Dict[str, Dict[str, Any]] = {}

        for method_enum, status_enum, count, amount in rows:
            method_str = method_enum.value if hasattr(method_enum, "value") else str(method_enum or "UNKNOWN")
            status_str = status_enum.value if hasattr(status_enum, "value") else str(status_enum or "UNKNOWN")
            amt = amount or Decimal("0.00")

            pct_cnt = round((count / total_transactions * 100.0), 2) if total_transactions > 0 else 0.0
            pct_vol = round(float(amt / total_volume) * 100.0, 2) if total_volume > 0 else 0.0

            breakdown_items.append(
                PaymentMethodBreakdownItem(
                    payment_method=method_str,
                    status=status_str,
                    count=count,
                    total_amount=amt.quantize(Decimal("0.01")),
                    percentage_of_total_count=pct_cnt,
                    percentage_of_total_volume=pct_vol,
                )
            )

            # Accumulate into method summary
            if method_str not in method_map:
                method_map[method_str] = {
                    "payment_method": method_str,
                    "total_count": 0,
                    "total_amount": Decimal("0.00"),
                    "success_count": 0,
                    "success_amount": Decimal("0.00"),
                    "failed_count": 0,
                    "pending_count": 0,
                }

            s = method_map[method_str]
            s["total_count"] += count
            s["total_amount"] += amt
            if status_str == TransactionStatus.SUCCESS.value:
                s["success_count"] += count
                s["success_amount"] += amt
            elif status_str in (TransactionStatus.FAILED.value, TransactionStatus.TIMEOUT.value):
                s["failed_count"] += count
            elif status_str in (TransactionStatus.PENDING.value, TransactionStatus.INITIATED.value):
                s["pending_count"] += count

        methods_summary: List[PaymentMethodSummary] = []
        for method_str, s in method_map.items():
            vol_pct = round(float(s["total_amount"] / total_volume) * 100.0, 2) if total_volume > 0 else 0.0
            cnt_pct = round((s["total_count"] / total_transactions * 100.0), 2) if total_transactions > 0 else 0.0
            methods_summary.append(
                PaymentMethodSummary(
                    payment_method=method_str,
                    total_count=s["total_count"],
                    total_amount=s["total_amount"].quantize(Decimal("0.01")),
                    success_count=s["success_count"],
                    success_amount=s["success_amount"].quantize(Decimal("0.01")),
                    failed_count=s["failed_count"],
                    pending_count=s["pending_count"],
                    volume_percentage=vol_pct,
                    count_percentage=cnt_pct,
                )
            )

        response = PaymentMethodsAnalyticsResponse(
            merchant_id=merchant_id,
            total_transactions=total_transactions,
            total_volume=total_volume.quantize(Decimal("0.01")),
            breakdown=breakdown_items,
            methods_summary=methods_summary,
        )

        if client:
            try:
                client.set(cache_key, response.model_dump_json(), ex=CACHE_TTL_SECONDS)
            except Exception as exc:
                logger.warning("analytics_cache_write_error", key=cache_key, error=str(exc))

        return response
