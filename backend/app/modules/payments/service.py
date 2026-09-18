import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, Tuple, Union
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.customers.models import Customer
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.mock_upi_provider.schemas import MockScenario
from app.modules.mock_upi_provider.service import MockUPIProvider
from app.modules.mock_upi_provider.tasks import resolve_simulated_payment_async
from app.modules.payments.models import (
    PaymentMethod,
    PaymentTransaction,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.payments.schemas import InitiatePaymentRequest
from app.shared.exceptions import BadRequestException, ConflictException, EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams, paginate_query


class PaymentStateMachine:
    """Finite State Machine enforcing allowed transaction state transitions."""

    VALID_TRANSITIONS: dict[TransactionStatus, set[TransactionStatus]] = {
        TransactionStatus.CREATED: {
            TransactionStatus.INITIATED,
        },
        TransactionStatus.INITIATED: {
            TransactionStatus.SUCCESS,
            TransactionStatus.FAILED,
            TransactionStatus.PENDING,
            TransactionStatus.TIMEOUT,
            TransactionStatus.DUPLICATE,
        },
        TransactionStatus.PENDING: {
            TransactionStatus.SUCCESS,
            TransactionStatus.FAILED,
        },
        TransactionStatus.TIMEOUT: {
            TransactionStatus.SUCCESS,
            TransactionStatus.FAILED,
        },
        TransactionStatus.SUCCESS: {
            TransactionStatus.REFUND_INITIATED,
        },
        TransactionStatus.REFUND_INITIATED: {
            TransactionStatus.REFUND_PENDING,
            TransactionStatus.REFUND_FAILED,
        },
        TransactionStatus.REFUND_PENDING: {
            TransactionStatus.REFUNDED,
            TransactionStatus.REFUND_FAILED,
        },
        # PARTIALLY_REFUNDED is a system-derived state set by RefundService after
        # a partial refund clears. It allows additional refund requests to be stacked
        # until the full original amount has been recovered.
        TransactionStatus.PARTIALLY_REFUNDED: {
            TransactionStatus.REFUND_INITIATED,
        },
        TransactionStatus.FAILED: set(),
        TransactionStatus.DUPLICATE: set(),
        TransactionStatus.REFUNDED: set(),
        TransactionStatus.REFUND_FAILED: set(),
    }

    @classmethod
    def validate_transition(
        cls, from_status: TransactionStatus, to_status: TransactionStatus
    ) -> None:
        """Validates if transition from from_status to to_status is allowed.
        Raises 409 Conflict if not allowed.
        """
        allowed = cls.VALID_TRANSITIONS.get(from_status, set())
        if to_status not in allowed:
            raise ConflictException(
                message=f"Invalid transaction status transition from '{from_status.value}' to '{to_status.value}'.",
                code="INVALID_STATUS_TRANSITION",
                details={
                    "current_status": from_status.value,
                    "target_status": to_status.value,
                    "allowed_transitions": [s.value for s in allowed],
                },
            )


class PaymentService:
    """Core financial ledger service for payment transactions."""

    @classmethod
    def validate_transition(
        cls, from_status: TransactionStatus, to_status: TransactionStatus
    ) -> None:
        PaymentStateMachine.validate_transition(from_status, to_status)

    @staticmethod
    def recompute_invoice_status(db: Session, invoice_id: uuid.UUID) -> Optional[Invoice]:
        """Recomputes parent invoice's aggregate status (PARTIALLY_PAID vs PAID)

        and paid_amount based on sum of successful transactions.
        Invoice status for these states is always derived, never set directly.
        """
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return None

        # Calculate sum of all settled SUCCESS transactions for this invoice
        sum_successful = (
            db.query(func.coalesce(func.sum(PaymentTransaction.amount), Decimal("0.00")))
            .filter(
                PaymentTransaction.invoice_id == invoice_id,
                PaymentTransaction.status == TransactionStatus.SUCCESS,
            )
            .scalar()
        )

        old_status = invoice.status
        old_paid = invoice.paid_amount
        invoice.paid_amount = Decimal(str(sum_successful))

        if invoice.total_amount > Decimal("0.00") and invoice.paid_amount >= invoice.total_amount:
            new_status = InvoiceStatus.PAID
        elif invoice.paid_amount > Decimal("0.00"):
            new_status = InvoiceStatus.PARTIALLY_PAID
        else:
            new_status = invoice.status

        if invoice.status != new_status:
            invoice.status = new_status
            record_audit(
                db=db,
                action=AuditAction.STATUS_CHANGE,
                entity_name="invoices",
                entity_id=invoice.id,
                merchant_id=invoice.merchant_id,
                before={"status": old_status.value, "paid_amount": str(old_paid)},
                after={"status": new_status.value, "paid_amount": str(invoice.paid_amount)},
            )
            if new_status == InvoiceStatus.PAID:
                try:
                    from app.modules.webhooks.service import WebhookService
                    WebhookService.dispatch_event(
                        db=db,
                        merchant_id=invoice.merchant_id,
                        event_type="invoice.paid",
                        payload={
                            "event": "invoice.paid",
                            "invoice_id": str(invoice.id),
                            "invoice_number": invoice.invoice_number,
                            "total_amount": str(invoice.total_amount),
                            "paid_amount": str(invoice.paid_amount),
                        },
                    )
                except Exception:
                    pass
        return invoice

    @staticmethod
    def recompute_installment_and_plan_status(db: Session, installment_id: uuid.UUID) -> None:
        """Marks installment as PAID and recomputes the parent payment plan's status."""
        from app.modules.splits.models import (
            PaymentPlan,
            PaymentPlanInstallment,
            InstallmentStatus,
            PaymentPlanStatus,
        )

        installment = (
            db.query(PaymentPlanInstallment)
            .filter(PaymentPlanInstallment.id == installment_id)
            .first()
        )
        if not installment:
            return

        installment.paid_amount = installment.amount
        installment.status = InstallmentStatus.PAID

        plan = (
            db.query(PaymentPlan)
            .filter(PaymentPlan.id == installment.payment_plan_id)
            .first()
        )
        if plan:
            all_paid = all(
                inst.status == InstallmentStatus.PAID for inst in plan.installments
            )
            if all_paid:
                plan.status = PaymentPlanStatus.COMPLETED

    @classmethod
    def initiate_payment(
        cls,
        db: Session,
        payload: InitiatePaymentRequest,
        idempotency_key: str,
    ) -> Tuple[PaymentTransaction, bool]:
        """Initiates a payment transaction or returns the existing transaction on idempotent replay.

        Uses a Postgres transaction block around the full initiate->persist->status-history write
        to guarantee ledger consistency.
        Returns: (PaymentTransaction, is_new: bool)
        """
        # 1. Idempotency lookup: if key exists, return immediately without re-initiating
        existing_tx = (
            db.query(PaymentTransaction)
            .options(joinedload(PaymentTransaction.status_history))
            .filter(PaymentTransaction.idempotency_key == idempotency_key)
            .first()
        )
        if existing_tx:
            return existing_tx, False

        # 2. Atomic ledger write inside Postgres transaction
        with db.begin_nested() if db.in_transaction() else db.begin():
            # Step A: Create in CREATED status
            tx = PaymentTransaction(
                merchant_id=payload.merchant_id,
                amount=payload.amount,
                currency=payload.currency,
                invoice_id=payload.invoice_id,
                customer_id=payload.customer_id,
                payment_method=payload.payment_method,
                installment_id=payload.installment_id,
                idempotency_key=idempotency_key,
                payer_vpa=payload.payer_vpa,
                payee_vpa=payload.payee_vpa,
                status=TransactionStatus.CREATED,
            )
            db.add(tx)
            db.flush()

            # Record initial CREATED history
            h_created = TransactionStatusHistory(
                transaction_id=tx.id,
                from_status=None,
                to_status=TransactionStatus.CREATED.value,
                reason="Transaction created in payment ledger",
            )
            db.add(h_created)
            db.flush()

            # Step B: Transition to INITIATED
            cls.validate_transition(TransactionStatus.CREATED, TransactionStatus.INITIATED)
            tx.status = TransactionStatus.INITIATED
            h_initiated = TransactionStatusHistory(
                transaction_id=tx.id,
                from_status=TransactionStatus.CREATED.value,
                to_status=TransactionStatus.INITIATED.value,
                reason="Payment session initiated with UPI provider",
            )
            db.add(h_initiated)
            db.flush()

            # Step C: Call MockUPIProvider simulator
            vpa_to_use = tx.payer_vpa or "customer@upi"
            mock_res = MockUPIProvider.initiate_payment(
                db=db,
                amount=tx.amount,
                vpa=vpa_to_use,
                idempotency_key=idempotency_key,
                scenario=payload.scenario,
                transaction_id=tx.id,
                merchant_id=tx.merchant_id,
                auto_commit=False,
                record_history=False,
            )

            # Step D: Apply outcome status transition
            outcome_status = mock_res.status
            cls.validate_transition(TransactionStatus.INITIATED, outcome_status)

            tx.status = outcome_status
            tx.provider_ref_id = mock_res.provider_ref_id
            tx.mock_scenario = mock_res.scenario.value
            tx.failure_reason = mock_res.failure_reason
            if outcome_status in (TransactionStatus.SUCCESS, TransactionStatus.REFUNDED):
                tx.completed_at = datetime.now(timezone.utc)

            h_outcome = TransactionStatusHistory(
                transaction_id=tx.id,
                from_status=TransactionStatus.INITIATED.value,
                to_status=outcome_status.value,
                reason=f"Provider simulated scenario: {mock_res.scenario.value}",
            )
            db.add(h_outcome)

            record_audit(
                db=db,
                action=AuditAction.CREATE,
                entity_name="payment_transactions",
                entity_id=tx.id,
                merchant_id=tx.merchant_id,
                before=None,
                after={
                    "status": outcome_status.value,
                    "scenario": mock_res.scenario.value,
                    "amount": str(tx.amount),
                    "idempotency_key": idempotency_key,
                },
            )

            # Step E: If SUCCESS, recompute installment, plan, and invoice aggregate status
            if outcome_status == TransactionStatus.SUCCESS:
                if tx.installment_id:
                    cls.recompute_installment_and_plan_status(db=db, installment_id=tx.installment_id)
                if tx.invoice_id:
                    cls.recompute_invoice_status(db=db, invoice_id=tx.invoice_id)

        db.commit()
        db.refresh(tx)

        # Trigger Celery async resolution outside transaction if PENDING / TIMEOUT
        if mock_res.is_async:
            target_status_str = (
                TransactionStatus.SUCCESS.value
                if mock_res.scenario == MockScenario.PENDING
                else TransactionStatus.FAILED.value
            )
            try:
                resolve_simulated_payment_async.apply_async(
                    args=[str(tx.id), target_status_str, mock_res.failure_reason],
                    countdown=2,
                )
            except Exception:
                pass

        # Dispatch Outbound Merchant Webhooks on terminal outcomes
        try:
            from app.modules.webhooks.service import WebhookService
            if outcome_status == TransactionStatus.SUCCESS:
                WebhookService.dispatch_event(
                    db=db,
                    merchant_id=tx.merchant_id,
                    event_type="payment.success",
                    payload={
                        "event": "payment.success",
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "currency": tx.currency,
                        "status": "SUCCESS",
                        "provider_ref_id": tx.provider_ref_id,
                        "idempotency_key": tx.idempotency_key,
                    },
                )
            elif outcome_status == TransactionStatus.FAILED:
                WebhookService.dispatch_event(
                    db=db,
                    merchant_id=tx.merchant_id,
                    event_type="payment.failed",
                    payload={
                        "event": "payment.failed",
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "currency": tx.currency,
                        "status": "FAILED",
                        "failure_reason": tx.failure_reason,
                        "idempotency_key": tx.idempotency_key,
                    },
                )
        except Exception:
            pass

        # Trigger Duplicate Detection Celery Task on SUCCESS / PENDING / DUPLICATE
        if outcome_status in (TransactionStatus.SUCCESS, TransactionStatus.PENDING, TransactionStatus.DUPLICATE) or (mock_res and mock_res.scenario == MockScenario.DUPLICATE):
            try:
                from app.modules.duplicate_detection.tasks import detect_duplicate_transaction
                detect_duplicate_transaction.delay(str(tx.id))
            except Exception:
                pass

        # Invalidate Analytics Cache on SUCCESS
        if outcome_status == TransactionStatus.SUCCESS:
            try:
                from app.modules.analytics.service import AnalyticsService
                AnalyticsService.invalidate_cache(merchant_id=tx.merchant_id)
            except Exception:
                pass

        # Trigger Risk Evaluation Celery Task
        try:
            from app.modules.risk.tasks import evaluate_risk_rules
            evaluate_risk_rules.delay(str(tx.id))
        except Exception:
            pass

        # Dispatch Notification on terminal outcomes
        try:
            from app.modules.notifications.service import NotificationService
            from app.modules.notifications.models import NotificationChannel
            if outcome_status == TransactionStatus.SUCCESS:
                NotificationService.send_notification(
                    merchant_id=tx.merchant_id,
                    channel=NotificationChannel.PUSH,
                    template="payment_success",
                    payload={
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "currency": tx.currency,
                        "payer_vpa": tx.payer_vpa,
                    },
                )
            elif outcome_status == TransactionStatus.FAILED:
                NotificationService.send_notification(
                    merchant_id=tx.merchant_id,
                    channel=NotificationChannel.PUSH,
                    template="payment_failed",
                    payload={
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "reason": tx.failure_reason or "Payment failed",
                    },
                )
        except Exception:
            pass

        return tx, True

    @classmethod
    def transition_status(
        cls,
        db: Session,
        transaction_id: uuid.UUID,
        to_status: TransactionStatus,
        reason: Optional[str] = None,
    ) -> PaymentTransaction:
        """Transitions transaction status enforcing the finite state machine.

        Raises 409 Conflict if transition is not explicitly allowed.
        """
        tx = (
            db.query(PaymentTransaction)
            .options(joinedload(PaymentTransaction.status_history))
            .filter(PaymentTransaction.id == transaction_id)
            .first()
        )
        if not tx:
            raise EntityNotFoundException("PaymentTransaction", transaction_id)

        from_status = tx.status
        cls.validate_transition(from_status, to_status)

        with db.begin_nested() if db.in_transaction() else db.begin():
            tx.status = to_status
            if to_status in (TransactionStatus.SUCCESS, TransactionStatus.REFUNDED):
                tx.completed_at = datetime.now(timezone.utc)

            history = TransactionStatusHistory(
                transaction_id=tx.id,
                from_status=from_status.value,
                to_status=to_status.value,
                reason=reason or f"Transitioned from {from_status.value} to {to_status.value}",
            )
            db.add(history)

            record_audit(
                db=db,
                action=AuditAction.STATUS_CHANGE,
                entity_name="payment_transactions",
                entity_id=tx.id,
                merchant_id=tx.merchant_id,
                before={"status": from_status.value},
                after={"status": to_status.value, "reason": reason},
            )

            # Recompute parent installment, plan, and invoice if transition was into SUCCESS
            if to_status == TransactionStatus.SUCCESS:
                if tx.installment_id:
                    cls.recompute_installment_and_plan_status(db=db, installment_id=tx.installment_id)
                if tx.invoice_id:
                    cls.recompute_invoice_status(db=db, invoice_id=tx.invoice_id)

        db.commit()
        db.refresh(tx)

        try:
            from app.modules.webhooks.service import WebhookService
            if to_status == TransactionStatus.SUCCESS:
                WebhookService.dispatch_event(
                    db=db,
                    merchant_id=tx.merchant_id,
                    event_type="payment.success",
                    payload={
                        "event": "payment.success",
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "currency": tx.currency,
                        "status": "SUCCESS",
                        "provider_ref_id": tx.provider_ref_id,
                    },
                )
            elif to_status == TransactionStatus.FAILED:
                WebhookService.dispatch_event(
                    db=db,
                    merchant_id=tx.merchant_id,
                    event_type="payment.failed",
                    payload={
                        "event": "payment.failed",
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "currency": tx.currency,
                        "status": "FAILED",
                        "failure_reason": tx.failure_reason,
                    },
                )
            elif to_status in (TransactionStatus.REFUND_INITIATED, TransactionStatus.REFUND_PENDING, TransactionStatus.REFUNDED):
                WebhookService.dispatch_event(
                    db=db,
                    merchant_id=tx.merchant_id,
                    event_type=f"refund.{to_status.value.lower()}",
                    payload={
                        "event": f"refund.{to_status.value.lower()}",
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "status": to_status.value,
                    },
                )
        except Exception:
            pass

        # Trigger Duplicate Detection Celery Task when reaching SUCCESS or PENDING
        if to_status in (TransactionStatus.SUCCESS, TransactionStatus.PENDING):
            try:
                from app.modules.duplicate_detection.tasks import detect_duplicate_transaction
                detect_duplicate_transaction.delay(str(tx.id))
            except Exception:
                pass

        # Invalidate Analytics Cache on transition to SUCCESS
        if to_status == TransactionStatus.SUCCESS:
            try:
                from app.modules.analytics.service import AnalyticsService
                AnalyticsService.invalidate_cache(merchant_id=tx.merchant_id)
            except Exception:
                pass

        # Trigger Risk Evaluation Celery Task
        try:
            from app.modules.risk.tasks import evaluate_risk_rules
            evaluate_risk_rules.delay(str(tx.id))
        except Exception:
            pass

        # Dispatch Notification on transition to terminal states
        try:
            from app.modules.notifications.service import NotificationService
            from app.modules.notifications.models import NotificationChannel
            if to_status == TransactionStatus.SUCCESS:
                NotificationService.send_notification(
                    merchant_id=tx.merchant_id,
                    channel=NotificationChannel.PUSH,
                    template="payment_success",
                    payload={
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "currency": tx.currency,
                        "payer_vpa": tx.payer_vpa,
                    },
                )
            elif to_status in (TransactionStatus.FAILED, TransactionStatus.TIMEOUT):
                NotificationService.send_notification(
                    merchant_id=tx.merchant_id,
                    channel=NotificationChannel.PUSH,
                    template="payment_failed",
                    payload={
                        "transaction_id": str(tx.id),
                        "amount": str(tx.amount),
                        "reason": reason or tx.failure_reason or to_status.value,
                    },
                )
        except Exception:
            pass

        return tx

    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: uuid.UUID) -> PaymentTransaction:
        """Fetches transaction detail including full status history."""
        tx = (
            db.query(PaymentTransaction)
            .options(joinedload(PaymentTransaction.status_history))
            .filter(PaymentTransaction.id == transaction_id)
            .first()
        )
        if not tx:
            raise EntityNotFoundException("PaymentTransaction", transaction_id)
        return tx

    @staticmethod
    def list_merchant_transactions(
        db: Session,
        merchant_id: uuid.UUID,
        pagination: PaginationParams,
        status: Optional[Union[TransactionStatus, str]] = None,
        payment_method: Optional[PaymentMethod] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        search: Optional[str] = None,
        flag: Optional[str] = None,
        stuck: Optional[bool] = None,
        stuck_threshold_seconds: int = 120,
    ) -> PaginatedResponse:
        """Lists merchant transactions with status/method/date filters, stuck filter, search, and pagination."""
        query = (
            db.query(PaymentTransaction)
            .options(joinedload(PaymentTransaction.status_history))
            .filter(PaymentTransaction.merchant_id == merchant_id)
        )

        effective_status: Optional[TransactionStatus] = None
        if status:
            if isinstance(status, str):
                try:
                    effective_status = TransactionStatus(status.upper())
                except ValueError:
                    effective_status = None
            else:
                effective_status = status

        if effective_status and not stuck:
            query = query.filter(PaymentTransaction.status == effective_status)

        if stuck:
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=stuck_threshold_seconds)
            if effective_status:
                query = query.filter(
                    PaymentTransaction.status == effective_status,
                    PaymentTransaction.created_at <= cutoff,
                )
            else:
                query = query.filter(
                    PaymentTransaction.status.in_([
                        TransactionStatus.PENDING,
                        TransactionStatus.INITIATED,
                    ]),
                    PaymentTransaction.created_at <= cutoff,
                )

        if payment_method:
            query = query.filter(PaymentTransaction.payment_method == payment_method)

        if from_date:
            query = query.filter(PaymentTransaction.created_at >= from_date)

        if to_date:
            query = query.filter(PaymentTransaction.created_at <= to_date)

        if flag and flag.lower() == "duplicate":
            from app.modules.duplicate_detection.models import DuplicateTransactionFlag
            dup_subq = (
                db.query(DuplicateTransactionFlag.original_transaction_id)
                .filter(DuplicateTransactionFlag.merchant_id == merchant_id)
                .union(
                    db.query(DuplicateTransactionFlag.duplicate_transaction_id)
                    .filter(DuplicateTransactionFlag.merchant_id == merchant_id)
                )
            )
            query = query.filter(PaymentTransaction.id.in_(dup_subq))

        if search:
            search_pat = f"%{search.strip()}%"
            query = (
                query.outerjoin(Invoice, PaymentTransaction.invoice_id == Invoice.id)
                .outerjoin(Customer, PaymentTransaction.customer_id == Customer.id)
                .filter(
                    or_(
                        PaymentTransaction.provider_ref_id.ilike(search_pat),
                        Invoice.invoice_number.ilike(search_pat),
                        Customer.name.ilike(search_pat),
                    )
                )
            )

        query = query.order_by(PaymentTransaction.created_at.desc())
        items, total = paginate_query(query, pagination)
        return PaginatedResponse.create(items, total, pagination)

    @classmethod
    def regenerate_payment_request_for_failed_transaction(
        cls,
        db: Session,
        transaction_id: uuid.UUID,
        actor: User,
    ):
        """Allows merchant to generate a new payment request for a FAILED or TIMEOUT transaction.

        Reuses Phase 6 payment_requests logic and enforces remaining invoice balance.
        Leaves the original historical failed transaction record completely intact and un-mutated.
        """
        tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == transaction_id).first()
        if not tx:
            raise EntityNotFoundException("PaymentTransaction", transaction_id)

        if tx.status not in (TransactionStatus.FAILED, TransactionStatus.TIMEOUT):
            raise BadRequestException(
                message=f"Cannot regenerate payment request for transaction in '{tx.status.value}' status. Only FAILED or TIMEOUT transactions are eligible.",
                code="INVALID_TRANSACTION_STATUS",
            )

        if not tx.invoice_id:
            raise BadRequestException(
                message="Transaction is not associated with an invoice.",
                code="INVOICE_NOT_LINKED",
            )

        from app.modules.payment_requests.schemas import PaymentRequestCreate
        from app.modules.payment_requests.service import create_payment_request

        request_payload = PaymentRequestCreate(
            amount=tx.amount,
            purpose=f"Regenerated payment request following {tx.status.value} transaction {tx.id}",
            payer_vpa=tx.payer_vpa,
        )

        return create_payment_request(
            db=db,
            invoice_id=tx.invoice_id,
            request=request_payload,
            actor=actor,
        )
