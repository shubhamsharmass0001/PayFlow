import uuid
from typing import Optional
from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app
from app.modules.payments.models import TransactionStatus

logger = get_task_logger(__name__)


@celery_app.task(name="mock_upi.resolve_simulated_payment_async", bind=True, max_retries=3)
def resolve_simulated_payment_async(
    self,
    transaction_id_str: str,
    target_status_str: str,
    reason: Optional[str] = None,
):
    """Celery background task that simulates delayed bank network resolution.

    Resolves a PENDING or TIMEOUT simulated transaction to its final status (SUCCESS/FAILED)
    after a simulated delay, then records an inbound webhook event mimicking banking webhooks.
    """
    from app.modules.mock_upi_provider.service import MockUPIProvider
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        tx_id = uuid.UUID(transaction_id_str)
        target_status = TransactionStatus(target_status_str)
        tx = MockUPIProvider.resolve_async_settlement(
            db=db,
            transaction_id=tx_id,
            target_status=target_status,
            reason=reason,
        )
        logger.info(f"Simulated async payment '{tx_id}' successfully resolved to '{target_status.value}'.")
        return {
            "status": "resolved",
            "transaction_id": str(tx.id),
            "final_status": target_status.value,
        }
    except Exception as exc:
        db.rollback()
        logger.error(f"Error resolving simulated async payment '{transaction_id_str}': {exc}")
        raise self.retry(exc=exc, countdown=2)
    finally:
        db.close()
