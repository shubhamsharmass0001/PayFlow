"""Reconciliation Module Celery Tasks."""
from datetime import datetime, time, timedelta, timezone
from typing import Dict, List, Optional
from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="reconciliation.run_nightly_reconciliation")
def run_nightly_reconciliation() -> Dict[str, any]:
    """Nightly Celery beat task that iterates over all active merchants and executes

    automated reconciliation for the preceding 24-hour calendar day.
    """
    from app.db.session import SessionLocal
    from app.modules.merchants.models import Merchant
    from app.modules.reconciliation.service import ReconciliationService

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        yesterday = (now - timedelta(days=1)).date()
        period_start = datetime.combine(yesterday, time.min).replace(tzinfo=timezone.utc)
        period_end = datetime.combine(yesterday, time.max).replace(tzinfo=timezone.utc)

        merchants = (
            db.query(Merchant)
            .filter(Merchant.deleted_at == None)
            .all()
        )

        logger.info(
            f"Starting nightly reconciliation for {len(merchants)} merchants. "
            f"Period: {period_start.isoformat()} to {period_end.isoformat()}"
        )

        results = []
        for merchant in merchants:
            try:
                batch = ReconciliationService.run_reconciliation(
                    db=db,
                    merchant_id=merchant.id,
                    period_start=period_start,
                    period_end=period_end,
                )
                results.append({
                    "merchant_id": str(merchant.id),
                    "batch_id": str(batch.id),
                    "total_records": batch.total_records,
                    "matched_records": batch.matched_records,
                    "discrepancies": batch.discrepancy_count,
                    "status": batch.status.value,
                })
            except Exception as exc:
                logger.error(f"Nightly reconciliation failed for merchant {merchant.id}: {exc}", exc_info=True)
                results.append({
                    "merchant_id": str(merchant.id),
                    "error": str(exc),
                })

        logger.info(f"Nightly reconciliation complete. Processed {len(results)} merchants.")
        return {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "merchants_processed": len(results),
            "details": results,
        }

    finally:
        db.close()
