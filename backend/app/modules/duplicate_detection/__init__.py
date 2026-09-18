"""Duplicate Detection Module."""
from app.modules.duplicate_detection.models import DuplicateFlagStatus, DuplicateTransactionFlag
from app.modules.duplicate_detection.routes import router
from app.modules.duplicate_detection.schemas import (
    DuplicateFlagResponse,
    DuplicateFlagSummaryResponse,
    ResolveDuplicateFlagRequest,
)
from app.modules.duplicate_detection.service import DuplicateDetectionService
from app.modules.duplicate_detection.tasks import detect_duplicate_transaction

__all__ = [
    "DuplicateFlagStatus",
    "DuplicateTransactionFlag",
    "DuplicateDetectionService",
    "detect_duplicate_transaction",
    "DuplicateFlagResponse",
    "DuplicateFlagSummaryResponse",
    "ResolveDuplicateFlagRequest",
    "router",
]
