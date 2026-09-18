"""Duplicate Detection Module Service."""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.duplicate_detection.models import (
    DuplicateFlagReason,
    DuplicateFlagStatus,
    DuplicateTransactionFlag,
)
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams, paginate_query


class DuplicateDetectionService:
    """Service providing automated duplicate transaction detection, pairing, and resolution workflows."""

    DETECTION_WINDOW_MINUTES = 15

    @classmethod
    def detect_duplicates_for_transaction(
        cls,
        db: Session,
        transaction: PaymentTransaction,
    ) -> List[DuplicateTransactionFlag]:
        """Scans for potential duplicate transactions matching the given transaction.

        Checks:
          1. Provider-reported DUPLICATE scenario.
          2. Same invoice + matching amount + payment method within 15 minutes.
          3. Same customer + matching amount + payment method within 15 minutes.
        """
        created_flags: List[DuplicateTransactionFlag] = []

        tx_time = transaction.created_at
        if tx_time.tzinfo is None:
            tx_time = tx_time.replace(tzinfo=timezone.utc)

        window_start = tx_time - timedelta(minutes=cls.DETECTION_WINDOW_MINUTES)
        window_end = tx_time + timedelta(minutes=cls.DETECTION_WINDOW_MINUTES)

        candidates: List[Tuple[PaymentTransaction, DuplicateFlagReason, str]] = []

        # Rule 1: Provider-reported DUPLICATE scenario
        is_provider_duplicate = (
            transaction.mock_scenario == "DUPLICATE"
            or transaction.status == TransactionStatus.DUPLICATE
        )
        if is_provider_duplicate:
            prior_tx = (
                db.query(PaymentTransaction)
                .filter(
                    PaymentTransaction.merchant_id == transaction.merchant_id,
                    PaymentTransaction.id != transaction.id,
                    PaymentTransaction.amount == transaction.amount,
                )
                .order_by(PaymentTransaction.created_at.desc())
                .first()
            )
            matched_target = prior_tx if prior_tx else transaction
            candidates.append((
                matched_target,
                DuplicateFlagReason.IDENTICAL_AMOUNT_AND_VPA,
                f"Provider reported DUPLICATE scenario" + (f" against transaction {prior_tx.id}" if prior_tx else ""),
            ))

        # Rule 2: Same invoice, matching amount and method within window
        if transaction.invoice_id:
            invoice_matches = (
                db.query(PaymentTransaction)
                .filter(
                    PaymentTransaction.merchant_id == transaction.merchant_id,
                    PaymentTransaction.invoice_id == transaction.invoice_id,
                    PaymentTransaction.id != transaction.id,
                    PaymentTransaction.amount == transaction.amount,
                    PaymentTransaction.payment_method == transaction.payment_method,
                    PaymentTransaction.created_at >= window_start,
                    PaymentTransaction.created_at <= window_end,
                    PaymentTransaction.status.in_([
                        TransactionStatus.SUCCESS,
                        TransactionStatus.PENDING,
                    ]),
                )
                .all()
            )
            for m in invoice_matches:
                candidates.append((
                    m,
                    DuplicateFlagReason.TIMEFRAME_BURST,
                    f"Matching amount INR {transaction.amount} and method {transaction.payment_method.value} "
                    f"on same invoice within {cls.DETECTION_WINDOW_MINUTES}-minute window",
                ))

        # Rule 3: Same customer, matching amount and method within window
        if transaction.customer_id:
            customer_matches = (
                db.query(PaymentTransaction)
                .filter(
                    PaymentTransaction.merchant_id == transaction.merchant_id,
                    PaymentTransaction.customer_id == transaction.customer_id,
                    PaymentTransaction.id != transaction.id,
                    PaymentTransaction.amount == transaction.amount,
                    PaymentTransaction.payment_method == transaction.payment_method,
                    PaymentTransaction.created_at >= window_start,
                    PaymentTransaction.created_at <= window_end,
                    PaymentTransaction.status.in_([
                        TransactionStatus.SUCCESS,
                        TransactionStatus.PENDING,
                    ]),
                )
                .all()
            )
            for m in customer_matches:
                candidates.append((
                    m,
                    DuplicateFlagReason.TIMEFRAME_BURST,
                    f"Matching amount INR {transaction.amount} and method {transaction.payment_method.value} "
                    f"for same customer within {cls.DETECTION_WINDOW_MINUTES}-minute window",
                ))

        for matched_tx, reason_enum, match_reason_text in candidates:
            # Determine older vs newer transaction
            m_time = matched_tx.created_at
            if m_time.tzinfo is None:
                m_time = m_time.replace(tzinfo=timezone.utc)

            if m_time <= tx_time:
                orig_id, dup_id = matched_tx.id, transaction.id
            else:
                orig_id, dup_id = transaction.id, matched_tx.id

            # Avoid duplicate flag creation for the same transaction pair
            existing = (
                db.query(DuplicateTransactionFlag)
                .filter(
                    or_(
                        and_(
                            DuplicateTransactionFlag.original_transaction_id == orig_id,
                            DuplicateTransactionFlag.duplicate_transaction_id == dup_id,
                        ),
                        and_(
                            DuplicateTransactionFlag.original_transaction_id == dup_id,
                            DuplicateTransactionFlag.duplicate_transaction_id == orig_id,
                        ),
                    )
                )
                .first()
            )
            if existing:
                if not existing.match_reason:
                    existing.match_reason = match_reason_text
                    db.commit()
                continue

            flag = DuplicateTransactionFlag(
                merchant_id=transaction.merchant_id,
                original_transaction_id=orig_id,
                duplicate_transaction_id=dup_id,
                confidence_score=Decimal("1.0000"),
                flag_reason=reason_enum,
                match_reason=match_reason_text,
                status=DuplicateFlagStatus.SUSPECTED,
            )
            db.add(flag)
            db.flush()
            created_flags.append(flag)

        if created_flags:
            db.commit()
            for f in created_flags:
                db.refresh(f)
                record_audit(
                    db=db,
                    action=AuditAction.CREATE,
                    entity_name="duplicate_transaction_flags",
                    entity_id=f.id,
                    merchant_id=f.merchant_id,
                    after={
                        "original_transaction_id": str(f.original_transaction_id),
                        "duplicate_transaction_id": str(f.duplicate_transaction_id),
                        "match_reason": f.match_reason,
                        "status": f.status.value,
                    },
                )
            db.commit()

        return created_flags

    @classmethod
    def resolve_flag(
        cls,
        db: Session,
        flag_id: uuid.UUID,
        reason: str,
        resolved_by: Optional[uuid.UUID] = None,
        actor: Optional[User] = None,
    ) -> DuplicateTransactionFlag:
        """Marks a duplicate transaction flag as RESOLVED with explanation notes and audit logging."""
        flag = (
            db.query(DuplicateTransactionFlag)
            .filter(DuplicateTransactionFlag.id == flag_id)
            .first()
        )
        if not flag:
            raise EntityNotFoundException("DuplicateTransactionFlag", flag_id)

        old_status = flag.status
        effective_resolver_id = resolved_by or (actor.id if actor else None)

        flag.status = DuplicateFlagStatus.RESOLVED
        flag.resolved_by = effective_resolver_id
        flag.resolved_at = datetime.now(timezone.utc)
        flag.resolution_reason = reason

        db.commit()
        db.refresh(flag)

        record_audit(
            db=db,
            actor_id=effective_resolver_id,
            merchant_id=flag.merchant_id,
            action=AuditAction.UPDATE,
            entity_name="duplicate_transaction_flags",
            entity_id=flag.id,
            before={"status": old_status.value},
            after={
                "status": DuplicateFlagStatus.RESOLVED.value,
                "resolution_reason": reason,
                "resolved_by": str(effective_resolver_id) if effective_resolver_id else None,
            },
        )
        db.commit()

        logger.info(
            "duplicate_flag_resolved",
            flag_id=str(flag.id),
            merchant_id=str(flag.merchant_id),
            resolved_by=str(effective_resolver_id),
            reason=reason,
        )

        return flag

    @classmethod
    def get_unresolved_count(cls, db: Session, merchant_id: uuid.UUID) -> int:
        """Returns the total number of unresolved duplicate flags for a merchant (used by settlement/analytics)."""
        return (
            db.query(DuplicateTransactionFlag)
            .filter(
                DuplicateTransactionFlag.merchant_id == merchant_id,
                DuplicateTransactionFlag.status != DuplicateFlagStatus.RESOLVED,
            )
            .count()
        )

    @classmethod
    def list_flags(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        pagination: PaginationParams,
        status: Optional[DuplicateFlagStatus] = None,
    ):
        """Lists duplicate transaction flags for a merchant with pagination."""
        from app.modules.duplicate_detection.schemas import DuplicateFlagResponse

        query = (
            db.query(DuplicateTransactionFlag)
            .filter(DuplicateTransactionFlag.merchant_id == merchant_id)
        )
        if status:
            query = query.filter(DuplicateTransactionFlag.status == status)

        query = query.order_by(DuplicateTransactionFlag.created_at.desc())
        items, total = paginate_query(query, pagination)
        response_items = [DuplicateFlagResponse.model_validate(f) for f in items]
        return PaginatedResponse.create(
            items=response_items,
            total=total,
            params=pagination,
        )
