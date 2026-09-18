"""Celery Tasks for Payments Module."""
from typing import Any, Dict

from app.core.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(name="payments.poll_stuck_transactions")
def poll_stuck_transactions(
    stuck_threshold_seconds: int = 120,
    max_wait_seconds: int = 300,
) -> Dict[str, Any]:
    """Polls in-flight transactions stuck in PENDING or INITIATED past threshold.

    - If stuck past max_wait_seconds, escalates to FAILED with reason 'provider_timeout'.
    - Otherwise queries MockUPIProvider to resolve or update status.
    - On FAILED or TIMEOUT, triggers an operational alert notification to the merchant.

    Uses lazy imports (inside function body) so that test fixtures can patch
    app.db.session.SessionLocal before this function runs — matching the pattern
    used by run_nightly_reconciliation.
    """
    # Lazy imports: resolved at call time so test patching of SessionLocal works.
    from datetime import datetime, timedelta, timezone

    from app.db.session import SessionLocal
    from app.modules.mock_upi_provider.service import MockUPIProvider
    from app.modules.notifications.models import NotificationChannel
    from app.modules.notifications.service import NotificationService
    from app.modules.payments.models import PaymentTransaction, TransactionStatus
    from app.modules.payments.service import PaymentService

    db = SessionLocal()
    processed_count = 0
    resolved_count = 0
    failed_count = 0

    try:
        now = datetime.now(timezone.utc)
        stuck_cutoff = now - timedelta(seconds=stuck_threshold_seconds)
        max_wait_cutoff = now - timedelta(seconds=max_wait_seconds)

        stuck_txs = (
            db.query(PaymentTransaction)
            .filter(
                PaymentTransaction.status.in_([
                    TransactionStatus.PENDING,
                    TransactionStatus.INITIATED,
                ]),
                PaymentTransaction.created_at <= stuck_cutoff,
            )
            .all()
        )

        for tx in stuck_txs:
            processed_count += 1
            tx_created_at = tx.created_at
            if tx_created_at.tzinfo is None:
                tx_created_at = tx_created_at.replace(tzinfo=timezone.utc)

            # Scenario 1: Exceeded max wait → Escalate directly to FAILED
            if tx_created_at <= max_wait_cutoff:
                PaymentService.transition_status(
                    db=db,
                    transaction_id=tx.id,
                    to_status=TransactionStatus.FAILED,
                    reason="provider_timeout",
                )
                tx.failure_reason = "provider_timeout"
                db.commit()

                NotificationService.trigger_merchant_alert(
                    db=db,
                    merchant_id=tx.merchant_id,
                    title="Payment Transaction Timed Out",
                    content=f"Transaction {tx.id} for amount INR {tx.amount} timed out waiting for provider (provider_timeout).",
                    channel=NotificationChannel.IN_APP,
                )
                failed_count += 1
                continue

            # Scenario 2: Stuck past threshold but within max wait → Re-query mock provider
            new_status = MockUPIProvider.check_transaction_status(db=db, transaction=tx)
            if new_status == TransactionStatus.SUCCESS:
                PaymentService.transition_status(
                    db=db,
                    transaction_id=tx.id,
                    to_status=TransactionStatus.SUCCESS,
                    reason="Polled from mock provider: payment successful",
                )
                resolved_count += 1
            elif new_status == TransactionStatus.FAILED:
                PaymentService.transition_status(
                    db=db,
                    transaction_id=tx.id,
                    to_status=TransactionStatus.FAILED,
                    reason="provider_timeout",
                )
                tx.failure_reason = "provider_timeout"
                db.commit()

                NotificationService.trigger_merchant_alert(
                    db=db,
                    merchant_id=tx.merchant_id,
                    title="Payment Transaction Failed",
                    content=f"Transaction {tx.id} for amount INR {tx.amount} failed with reason: provider_timeout.",
                    channel=NotificationChannel.IN_APP,
                )
                failed_count += 1

        logger.info(
            "poll_stuck_transactions_completed",
            processed_count=processed_count,
            resolved_count=resolved_count,
            failed_count=failed_count,
        )

        return {
            "status": "success",
            "processed_count": processed_count,
            "resolved_count": resolved_count,
            "failed_count": failed_count,
        }
    except Exception as exc:
        logger.error("poll_stuck_transactions_error", error=str(exc))
        raise exc
    finally:
        db.close()
