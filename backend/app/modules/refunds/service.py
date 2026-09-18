"""Refunds Module Service.

Business rules:
  - Refunds can only be initiated against SUCCESS transactions.
  - Partial refunds are allowed: multiple refunds on one transaction summing ≤ original amount.
    This is DISTINCT from split-payment structuring (Phase 9); keep code paths separate.
  - The parent transaction's status in the PaymentStateMachine transitions are:
      SUCCESS → REFUND_INITIATED → REFUND_PENDING → REFUNDED | REFUND_FAILED
    But partial refunds leave the transaction in PARTIALLY_REFUNDED (not REFUNDED)
    until the full amount is refunded.
  - Approval is gated to Manager/Owner (RBAC checked at the route layer).
  - Every refund action is written to the audit log.
  - On REFUNDED / PARTIALLY_REFUNDED, outbound webhook events are dispatched.
"""

import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.payments.models import (
    PaymentTransaction,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.payments.service import PaymentStateMachine
from app.modules.refunds.models import Refund, RefundStatus
from app.modules.refunds.schemas import RefundCreate
from app.shared.exceptions import (
    BadRequestException,
    ConflictException,
    EntityNotFoundException,
)
from app.shared.pagination import PaginatedResponse, PaginationParams, paginate_query


class RefundService:
    """Core service for the refund lifecycle.

    Partial refunds are a first-class citizen: multiple calls with different
    amounts against the same transaction are all valid as long as the cumulative
    refunded amount ≤ original transaction amount.
    """

    # -----------------------------------------------------------------
    # Helper: compute how much has already been refunded on a transaction
    # -----------------------------------------------------------------
    @staticmethod
    def _already_refunded_amount(db: Session, transaction_id: uuid.UUID) -> Decimal:
        """Returns the sum of all REFUND_PENDING / SUCCESS refunds (excluding FAILED)."""
        result = (
            db.query(func.coalesce(func.sum(Refund.amount), Decimal("0.00")))
            .filter(
                Refund.transaction_id == transaction_id,
                Refund.status.in_([RefundStatus.INITIATED, RefundStatus.PENDING, RefundStatus.SUCCESS]),
            )
            .scalar()
        )
        return Decimal(str(result))

    # -----------------------------------------------------------------
    # POST /transactions/{id}/refunds → status REFUND_INITIATED
    # -----------------------------------------------------------------
    @classmethod
    def initiate_refund(
        cls,
        db: Session,
        transaction_id: uuid.UUID,
        payload: RefundCreate,
        actor: User,
    ) -> Refund:
        """Creates a refund record in INITIATED status.

        Validates:
          1. Parent transaction must be in SUCCESS status (or PARTIALLY_REFUNDED —
             allowed to stack additional partial refunds).
          2. Requested amount ≤ remaining refundable balance
             (transaction.amount − already_refunded).

        Does NOT call MockUPIProvider yet — approval does that.
        """
        tx = (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.id == transaction_id)
            .first()
        )
        if not tx:
            raise EntityNotFoundException("PaymentTransaction", transaction_id)

        # Only SUCCESS and PARTIALLY_REFUNDED allow new refund requests
        if tx.status not in (
            TransactionStatus.SUCCESS,
            TransactionStatus.PARTIALLY_REFUNDED,
        ):
            raise ConflictException(
                message=(
                    f"Cannot initiate refund on a transaction in '{tx.status.value}' status. "
                    "Only SUCCESS or PARTIALLY_REFUNDED transactions are eligible."
                ),
                code="REFUND_INELIGIBLE_STATUS",
                details={"current_status": tx.status.value},
            )

        already_refunded = cls._already_refunded_amount(db, transaction_id)
        remaining = tx.amount - already_refunded

        if payload.amount > remaining:
            raise BadRequestException(
                message=(
                    f"Refund amount ₹{payload.amount} exceeds the remaining refundable balance "
                    f"₹{remaining} (original: ₹{tx.amount}, already refunded: ₹{already_refunded})."
                ),
                code="REFUND_AMOUNT_EXCEEDS_BALANCE",
                details={
                    "transaction_amount": str(tx.amount),
                    "already_refunded": str(already_refunded),
                    "remaining_refundable": str(remaining),
                    "requested_amount": str(payload.amount),
                },
            )

        # Create refund record
        refund = Refund(
            merchant_id=tx.merchant_id,
            transaction_id=tx.id,
            amount=payload.amount,
            reason=payload.reason,
            status=RefundStatus.INITIATED,
        )
        db.add(refund)
        db.flush()

        # Write transaction_status_history entry on the parent transaction
        history = TransactionStatusHistory(
            transaction_id=tx.id,
            from_status=tx.status.value,
            to_status=TransactionStatus.REFUND_INITIATED.value,
            reason=f"Refund {refund.id} initiated: {payload.reason}",
        )
        db.add(history)

        # Transition parent transaction to REFUND_INITIATED (state machine validated)
        # Note: PARTIALLY_REFUNDED is NOT in the state machine transitions because
        # it's a system-derived state set here. We only write to status_history,
        # we do NOT call PaymentStateMachine.validate_transition for the
        # PARTIALLY_REFUNDED → REFUND_INITIATED path (it would reject it).
        # The parent transaction status only changes to REFUND_INITIATED if it was SUCCESS.
        if tx.status == TransactionStatus.SUCCESS:
            PaymentStateMachine.validate_transition(
                TransactionStatus.SUCCESS, TransactionStatus.REFUND_INITIATED
            )
            tx.status = TransactionStatus.REFUND_INITIATED

        record_audit(
            db=db,
            action=AuditAction.CREATE,
            entity_name="refunds",
            entity_id=refund.id,
            actor_id=actor.id,
            merchant_id=tx.merchant_id,
            before={"transaction_status": tx.status.value},
            after={
                "refund_id": str(refund.id),
                "amount": str(refund.amount),
                "reason": refund.reason,
                "status": refund.status.value,
            },
        )

        db.commit()
        db.refresh(refund)

        # Trigger Risk Evaluation Celery Task on refund event
        try:
            from app.modules.risk.tasks import evaluate_risk_rules
            evaluate_risk_rules.delay(str(tx.id), refund_id=str(refund.id))
        except Exception:
            pass

        return refund

    # -----------------------------------------------------------------
    # PATCH /refunds/{id}/approve → REFUND_PENDING → REFUNDED | REFUND_FAILED
    # -----------------------------------------------------------------
    @classmethod
    def approve_refund(
        cls,
        db: Session,
        refund_id: uuid.UUID,
        actor: User,
        notes: Optional[str] = None,
    ) -> Refund:
        """Manager/Owner-gated refund approval.

        Transitions:
          Refund: INITIATED → PENDING → SUCCESS | FAILED
          Parent PaymentTransaction: REFUND_INITIATED → REFUND_PENDING
                                     → REFUNDED | REFUND_FAILED (or PARTIALLY_REFUNDED)

        Calls MockUPIProvider (simulated refund scenario) and persists the result.
        """
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise EntityNotFoundException("Refund", refund_id)

        if refund.status != RefundStatus.INITIATED:
            raise ConflictException(
                message=f"Refund is in '{refund.status.value}' status and cannot be approved.",
                code="REFUND_INVALID_APPROVAL_STATUS",
                details={"current_status": refund.status.value},
            )

        tx = (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.id == refund.transaction_id)
            .first()
        )
        if not tx:
            raise EntityNotFoundException("PaymentTransaction", refund.transaction_id)

        # --- REFUND_PENDING phase ---
        refund.status = RefundStatus.PENDING

        # Transition parent tx: REFUND_INITIATED → REFUND_PENDING
        if tx.status == TransactionStatus.REFUND_INITIATED:
            tx.status = TransactionStatus.REFUND_PENDING
            h_pending = TransactionStatusHistory(
                transaction_id=tx.id,
                from_status=TransactionStatus.REFUND_INITIATED.value,
                to_status=TransactionStatus.REFUND_PENDING.value,
                reason=f"Refund {refund.id} approved by {actor.email}",
            )
            db.add(h_pending)
        db.flush()

        # --- Call MockUPIProvider refund simulation ---
        # We use a weighted outcome: ~90% REFUNDED, ~10% REFUND_FAILED
        # (simulated here without the full MockUPIProvider to keep refund path self-contained)
        import random
        provider_refund_id = f"MOCK-REFUND-{secrets.token_hex(6).upper()}"
        # Simulate a realistic outcome: overwhelmingly SUCCESS
        success = random.random() < 0.90

        now = datetime.now(timezone.utc)

        if success:
            refund.status = RefundStatus.SUCCESS
            refund.provider_refund_id = provider_refund_id
            refund.completed_at = now
            provider_outcome_desc = "MockUPIProvider: refund credited to payer source account"

            # Determine if full amount has now been refunded
            # Re-query to include this refund's amount in the tally
            already_refunded = cls._already_refunded_amount(db, tx.id)
            # Note: _already_refunded_amount includes the CURRENT refund (now SUCCESS)
            # since we already set refund.status = SUCCESS and flushed above
            db.flush()
            already_refunded_requeried = cls._already_refunded_amount(db, tx.id)

            if already_refunded_requeried >= tx.amount:
                # Full amount refunded → REFUNDED (terminal)
                tx.status = TransactionStatus.REFUNDED
                tx.completed_at = now
                h_refunded = TransactionStatusHistory(
                    transaction_id=tx.id,
                    from_status=TransactionStatus.REFUND_PENDING.value,
                    to_status=TransactionStatus.REFUNDED.value,
                    reason=f"Full refund completed via refund {refund.id}",
                )
                db.add(h_refunded)
                webhook_event = "refund.completed"
            else:
                # Partial refund → PARTIALLY_REFUNDED (non-terminal, allows further refunds)
                tx.status = TransactionStatus.PARTIALLY_REFUNDED
                h_partial = TransactionStatusHistory(
                    transaction_id=tx.id,
                    from_status=TransactionStatus.REFUND_PENDING.value,
                    to_status=TransactionStatus.PARTIALLY_REFUNDED.value,
                    reason=(
                        f"Partial refund ₹{refund.amount} completed via refund {refund.id}. "
                        f"Total refunded so far: ₹{already_refunded_requeried}"
                    ),
                )
                db.add(h_partial)
                webhook_event = "refund.partial"

        else:
            # REFUND_FAILED
            refund.status = RefundStatus.FAILED
            refund.failure_reason = "MOCK_REFUND_DECLINED: Simulated bank decline on refund processing"
            tx.status = TransactionStatus.REFUND_FAILED
            h_failed = TransactionStatusHistory(
                transaction_id=tx.id,
                from_status=TransactionStatus.REFUND_PENDING.value,
                to_status=TransactionStatus.REFUND_FAILED.value,
                reason=f"Refund {refund.id} rejected by mock provider",
            )
            db.add(h_failed)
            webhook_event = "refund.failed"
            provider_outcome_desc = "MockUPIProvider: refund declined"

        record_audit(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_name="refunds",
            entity_id=refund.id,
            actor_id=actor.id,
            merchant_id=tx.merchant_id,
            before={"status": RefundStatus.INITIATED.value},
            after={
                "status": refund.status.value,
                "provider_refund_id": refund.provider_refund_id,
                "notes": notes,
                "outcome": provider_outcome_desc,
            },
        )

        db.commit()
        db.refresh(refund)

        # Dispatch outbound webhook
        try:
            from app.modules.webhooks.service import WebhookService
            WebhookService.dispatch_event(
                db=db,
                merchant_id=tx.merchant_id,
                event_type=webhook_event,
                payload={
                    "event": webhook_event,
                    "refund_id": str(refund.id),
                    "transaction_id": str(tx.id),
                    "refund_amount": str(refund.amount),
                    "transaction_amount": str(tx.amount),
                    "status": refund.status.value,
                    "provider_refund_id": refund.provider_refund_id,
                },
            )
        except Exception:
            pass

        # Dispatch Notification on refund completion
        try:
            from app.modules.notifications.service import NotificationService
            from app.modules.notifications.models import NotificationChannel
            if refund.status == RefundStatus.SUCCESS:
                NotificationService.send_notification(
                    merchant_id=refund.merchant_id,
                    channel=NotificationChannel.EMAIL,
                    template="refund_processed",
                    payload={
                        "refund_id": str(refund.id),
                        "transaction_id": str(tx.id),
                        "amount": str(refund.amount),
                        "reason": refund.reason or "Customer refund processed",
                    },
                )
        except Exception:
            pass

        # Trigger Risk Evaluation Celery Task on refund approval
        try:
            from app.modules.risk.tasks import evaluate_risk_rules
            evaluate_risk_rules.delay(str(tx.id), refund_id=str(refund.id))
        except Exception:
            pass

        return refund

    # -----------------------------------------------------------------
    # GET /refunds/{id}
    # -----------------------------------------------------------------
    @staticmethod
    def get_refund_by_id(db: Session, refund_id: uuid.UUID) -> Refund:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise EntityNotFoundException("Refund", refund_id)
        return refund

    # -----------------------------------------------------------------
    # GET /merchants/{id}/refunds (paginated, filtered)
    # -----------------------------------------------------------------
    @staticmethod
    def list_merchant_refunds(
        db: Session,
        merchant_id: uuid.UUID,
        pagination: PaginationParams,
        status: Optional[RefundStatus] = None,
        transaction_id: Optional[uuid.UUID] = None,
    ) -> PaginatedResponse:
        """Lists refunds for a merchant with optional status and transaction filters."""
        query = db.query(Refund).filter(Refund.merchant_id == merchant_id)

        if status:
            query = query.filter(Refund.status == status)

        if transaction_id:
            query = query.filter(Refund.transaction_id == transaction_id)

        query = query.order_by(Refund.created_at.desc())
        items, total = paginate_query(query, pagination)
        return PaginatedResponse.create(items, total, pagination)
