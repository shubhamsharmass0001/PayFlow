"""Celery Tasks for the Risk Module."""

import uuid
from typing import List, Optional

from app.core.celery_app import celery_app
from app.core.logging import logger
from app.modules.risk.service import RiskService


@celery_app.task(name="risk.evaluate_risk_rules")
def evaluate_risk_rules(transaction_id: str, refund_id: Optional[str] = None) -> List[str]:
    """Evaluates auditable risk rules asynchronously for a transaction or refund event.

    Args:
        transaction_id: String UUID of the PaymentTransaction.
        refund_id: Optional String UUID of the Refund.

    Returns:
        List of triggered risk signal IDs.
    """
    logger.info("risk_evaluation_started", transaction_id=transaction_id, refund_id=refund_id)
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        tx_uuid = uuid.UUID(transaction_id)
        refund_uuid = uuid.UUID(refund_id) if refund_id else None
        signals = RiskService.evaluate_transaction_rules(
            db=db,
            transaction_id=tx_uuid,
            refund_id=refund_uuid,
        )
        signal_ids = [str(s.id) for s in signals]
        logger.info(
            "risk_evaluation_completed",
            transaction_id=transaction_id,
            signals_raised=len(signal_ids),
            signal_ids=signal_ids,
        )
        return signal_ids
    except Exception as exc:
        logger.error(
            "risk_evaluation_error",
            transaction_id=transaction_id,
            error=str(exc),
        )
        return []
    finally:
        db.close()
