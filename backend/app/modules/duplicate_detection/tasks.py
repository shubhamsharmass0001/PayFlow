"""Duplicate Detection Celery Tasks."""
import uuid
from typing import Dict, List
from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="duplicate_detection.detect_duplicate_transaction")
def detect_duplicate_transaction(transaction_id_str: str) -> Dict[str, any]:
    """Asynchronous Celery task that checks for duplicate transactions matching the given transaction."""
    from app.db.session import SessionLocal
    from app.modules.duplicate_detection.service import DuplicateDetectionService
    from app.modules.payments.models import PaymentTransaction

    db = SessionLocal()
    try:
        tx_id = uuid.UUID(transaction_id_str)
        tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == tx_id).first()
        if not tx:
            logger.warning(f"Transaction '{transaction_id_str}' not found for duplicate detection.")
            return {"status": "not_found", "transaction_id": transaction_id_str}

        flags = DuplicateDetectionService.detect_duplicates_for_transaction(db=db, transaction=tx)
        flag_ids = [str(f.id) for f in flags]

        logger.info(
            f"Duplicate detection completed for transaction '{tx_id}'. "
            f"Created {len(flags)} duplicate flags: {flag_ids}"
        )
        return {
            "status": "success",
            "transaction_id": transaction_id_str,
            "flags_created": len(flags),
            "flag_ids": flag_ids,
        }

    except Exception as exc:
        logger.error(f"Error during duplicate detection for transaction '{transaction_id_str}': {exc}", exc_info=True)
        return {"status": "error", "error": str(exc), "transaction_id": transaction_id_str}
    finally:
        db.close()
