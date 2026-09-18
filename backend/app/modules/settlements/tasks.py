"""Settlements Module Celery Task.

This task is invoked two ways:
  1. Inline (triggered by reconciliation service when a batch reaches MATCHED):
       create_settlement_from_batch.apply_async(args=[str(batch.id)], countdown=2)

  2. Nightly sweep (Celery beat at 02:00 UTC via __nightly_sweep__ sentinel):
       Iterates all MATCHED batches that don't yet have a settlement and
       creates settlements for each one. Acts as a safety net for any batches
       whose inline dispatch failed.

MDR / fee notice:
  All fee computations are ILLUSTRATIVE MOCK values (default 1.5% MDR + 18%
  GST-on-MDR). They do NOT represent live NPCI/interchange rates.
"""
from typing import Dict, Any

from app.core.celery_app import celery_app
from app.core.logging import logger

# Sentinel value used by the nightly Celery beat sweep
_NIGHTLY_SWEEP_SENTINEL = "__nightly_sweep__"


@celery_app.task(name="settlements.create_from_batch")
def create_settlement_from_batch(batch_id: str) -> Dict[str, Any]:
    """Creates a Settlement from a MATCHED reconciliation batch.

    When called with the __nightly_sweep__ sentinel, fans out across all
    MATCHED batches that have no settlement yet.

    Uses lazy imports so the conftest TestingSessionLocal patch is effective.
    """
    from app.db.session import SessionLocal
    from app.modules.reconciliation.models import ReconciliationBatch, ReconciliationStatus
    from app.modules.settlements.models import Settlement
    from app.modules.settlements.service import SettlementService

    db = SessionLocal()
    try:
        # ----------------------------------------------------------
        # Nightly sweep: fan-out across all unsettled MATCHED batches
        # ----------------------------------------------------------
        if batch_id == _NIGHTLY_SWEEP_SENTINEL:
            import uuid as _uuid

            unsettled_batch_ids = (
                db.query(ReconciliationBatch.id)
                .outerjoin(
                    Settlement,
                    Settlement.reconciliation_batch_id == ReconciliationBatch.id,
                )
                .filter(
                    ReconciliationBatch.status == ReconciliationStatus.MATCHED,
                    Settlement.id.is_(None),
                )
                .all()
            )

            logger.info(
                "nightly_settlement_sweep_started",
                unsettled_batch_count=len(unsettled_batch_ids),
            )

            results = []
            for (bid,) in unsettled_batch_ids:
                batch = db.query(ReconciliationBatch).filter(ReconciliationBatch.id == bid).first()
                if not batch:
                    continue
                try:
                    settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)
                    results.append({
                        "batch_id": str(bid),
                        "settlement_id": str(settlement.id) if settlement else None,
                        "status": "created" if settlement else "skipped",
                    })
                except Exception as exc:
                    logger.error(
                        "nightly_settlement_sweep_batch_error",
                        batch_id=str(bid),
                        error=str(exc),
                    )
                    results.append({"batch_id": str(bid), "status": "error", "error": str(exc)})

            return {
                "status": "nightly_sweep_complete",
                "batches_processed": len(results),
                "results": results,
            }

        # ----------------------------------------------------------
        # Single batch: inline path
        # ----------------------------------------------------------
        import uuid as _uuid
        batch = db.query(ReconciliationBatch).filter(
            ReconciliationBatch.id == _uuid.UUID(batch_id)
        ).first()

        if not batch:
            logger.warning("create_settlement_batch_not_found", batch_id=batch_id)
            return {"status": "skipped", "reason": "batch_not_found", "batch_id": batch_id}

        settlement = SettlementService.create_from_matched_batch(db=db, batch=batch)

        if settlement:
            return {
                "status": "created",
                "settlement_id": str(settlement.id),
                "batch_id": batch_id,
                "merchant_id": str(settlement.merchant_id),
                "gross_amount": str(settlement.gross_amount),
                "net_amount": str(settlement.net_amount),
                "utr_reference": settlement.utr_reference,
            }
        else:
            return {"status": "skipped", "batch_id": batch_id}

    except Exception as exc:
        logger.error("create_settlement_from_batch_error", batch_id=batch_id, error=str(exc))
        raise exc
    finally:
        db.close()
