from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "payflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

from celery.schedules import crontab

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "nightly-merchant-reconciliation": {
            "task": "reconciliation.run_nightly_reconciliation",
            "schedule": crontab(hour=1, minute=0),  # Runs nightly at 01:00 UTC
        },
        "poll-stuck-transactions": {
            "task": "payments.poll_stuck_transactions",
            "schedule": 60.0,  # Polling interval: every 60 seconds
        },
        # Runs at 02:00 UTC (one hour after reconciliation) to process any
        # MATCHED batches whose inline settlement dispatch was missed or failed.
        "nightly-settlement-sweep": {
            "task": "settlements.create_from_batch",
            "schedule": crontab(hour=2, minute=0),
            "args": ["__nightly_sweep__"],  # Sentinel: task will detect and fan-out
        },
    },
)
