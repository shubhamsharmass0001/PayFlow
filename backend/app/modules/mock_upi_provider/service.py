import random
import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.duplicate_detection.models import (
    DuplicateFlagReason,
    DuplicateFlagStatus,
    DuplicateTransactionFlag,
)
from app.modules.mock_upi_provider.schemas import MockPaymentResult, MockScenario
from app.modules.mock_upi_provider.tasks import resolve_simulated_payment_async
from app.modules.payments.models import (
    PaymentTransaction,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.webhooks.models import WebhookEventInbound, WebhookInboundStatus
from app.shared.exceptions import BadRequestException, EntityNotFoundException


class MockUPIProvider:
    """Standalone Mock UPI Provider Simulator.

    CRITICAL NOTICE:
      This is a local simulated sandbox environment. It does NOT connect to NPCI, UPI switches,
      or live banking rails. All transactions are simulated for prototype verification.
    """

    SCENARIO_WEIGHTS = [
        (MockScenario.SUCCESS, 0.80),
        (MockScenario.FAILED, 0.06),
        (MockScenario.PENDING, 0.05),
        (MockScenario.TIMEOUT, 0.03),
        (MockScenario.DUPLICATE, 0.02),
        (MockScenario.PARTIAL_PAYMENT, 0.02),
        (MockScenario.REFUND, 0.02),
    ]

    @classmethod
    def select_scenario(cls, override: Optional[MockScenario] = None) -> MockScenario:
        """Picks scenario: returns explicit override if supplied, else uses weighted distribution (~80% SUCCESS)."""
        if override is not None:
            return override
        scenarios = [s for s, _ in cls.SCENARIO_WEIGHTS]
        weights = [w for _, w in cls.SCENARIO_WEIGHTS]
        return random.choices(scenarios, weights=weights, k=1)[0]

    @classmethod
    def initiate_payment(
        cls,
        db: Session,
        amount: Decimal,
        vpa: str,
        idempotency_key: str,
        scenario: Optional[MockScenario] = None,
        transaction_id: Optional[uuid.UUID] = None,
        merchant_id: Optional[uuid.UUID] = None,
        auto_commit: bool = True,
        record_history: bool = True,
    ) -> MockPaymentResult:
        """Simulates initiating a UPI payment across one of the 7 supported scenarios."""
        chosen_scenario = cls.select_scenario(scenario)
        now = datetime.now(timezone.utc)
        provider_ref_id = f"MOCK-UPI-{secrets.token_hex(6).upper()}"

        status = TransactionStatus.INITIATED
        settled_amount = Decimal("0.00")
        failure_reason = None
        is_async = False
        duplicate_of_id = None

        if chosen_scenario == MockScenario.SUCCESS:
            status = TransactionStatus.SUCCESS
            settled_amount = amount

        elif chosen_scenario == MockScenario.FAILED:
            status = TransactionStatus.FAILED
            failure_reason = "PSP_DECLINED: Simulated bank decline (insufficient funds or user cancelled)"

        elif chosen_scenario == MockScenario.PENDING:
            status = TransactionStatus.PENDING
            is_async = True

        elif chosen_scenario == MockScenario.TIMEOUT:
            status = TransactionStatus.TIMEOUT
            failure_reason = "GATEWAY_TIMEOUT: Simulated timeout waiting for acquiring bank switch"
            is_async = True

        elif chosen_scenario == MockScenario.DUPLICATE:
            status = TransactionStatus.DUPLICATE
            failure_reason = "DUPLICATE_PAYMENT_DETECTED: Replay of identical idempotency key or rapid duplicate submission"
            flag_reason = DuplicateFlagReason.IDENTICAL_IDEMPOTENCY_KEY

            # 1. Match by idempotency_key first (exact replay)
            existing_tx = None
            if idempotency_key:
                q = db.query(PaymentTransaction).filter(PaymentTransaction.idempotency_key == idempotency_key)
                if transaction_id:
                    q = q.filter(PaymentTransaction.id != transaction_id)
                existing_tx = q.first()

            # 2. Match by (merchant_id, payer_vpa, amount) if not found by key
            if not existing_tx and vpa:
                q2 = db.query(PaymentTransaction).filter(
                    PaymentTransaction.payer_vpa == vpa,
                    PaymentTransaction.amount == amount,
                )
                if merchant_id:
                    q2 = q2.filter(PaymentTransaction.merchant_id == merchant_id)
                if transaction_id:
                    q2 = q2.filter(PaymentTransaction.id != transaction_id)
                existing_tx = q2.order_by(PaymentTransaction.created_at.desc()).first()
                if existing_tx:
                    flag_reason = DuplicateFlagReason.IDENTICAL_AMOUNT_AND_VPA

            if existing_tx:
                duplicate_of_id = existing_tx.id
            elif transaction_id:
                duplicate_of_id = transaction_id

            # Create DuplicateTransactionFlag if merchant context is known
            if merchant_id and transaction_id and duplicate_of_id:
                flag = DuplicateTransactionFlag(
                    merchant_id=merchant_id,
                    original_transaction_id=duplicate_of_id,
                    duplicate_transaction_id=transaction_id,
                    confidence_score=Decimal("0.9900"),
                    flag_reason=flag_reason,
                    match_reason="Provider reported DUPLICATE scenario",
                    status=DuplicateFlagStatus.SUSPECTED,
                )
                db.add(flag)
                db.flush()

        elif chosen_scenario == MockScenario.PARTIAL_PAYMENT:
            status = TransactionStatus.SUCCESS
            settled_amount = (Decimal(str(amount)) * Decimal("0.50")).quantize(Decimal("0.01"))

        elif chosen_scenario == MockScenario.REFUND:
            status = TransactionStatus.REFUNDED
            settled_amount = amount
            provider_ref_id = f"MOCK-REFUND-{secrets.token_hex(6).upper()}"

        # If a live PaymentTransaction record exists in DB, update it
        if transaction_id:
            tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == transaction_id).first()
            if tx:
                old_status = tx.status.value
                tx.status = status
                tx.provider_ref_id = provider_ref_id
                tx.mock_scenario = chosen_scenario.value
                tx.failure_reason = failure_reason
                if status in (TransactionStatus.SUCCESS, TransactionStatus.REFUNDED):
                    tx.completed_at = now

                if record_history:
                    history = TransactionStatusHistory(
                        transaction_id=tx.id,
                        from_status=old_status,
                        to_status=status.value,
                        reason=f"Simulated execution via MockUPIProvider ({chosen_scenario.value})",
                    )
                    db.add(history)

                    record_audit(
                        db=db,
                        action=AuditAction.STATUS_CHANGE,
                        entity_name="payment_transactions",
                        entity_id=tx.id,
                        merchant_id=tx.merchant_id,
                        before={"status": old_status},
                        after={"status": status.value, "scenario": chosen_scenario.value},
                    )
                if auto_commit:
                    db.commit()
                    db.refresh(tx)
                else:
                    db.flush()

                # Schedule Celery async follow-up for PENDING / TIMEOUT
                if is_async:
                    target_status_str = (
                        TransactionStatus.SUCCESS.value
                        if chosen_scenario == MockScenario.PENDING
                        else TransactionStatus.FAILED.value
                    )
                    try:
                        resolve_simulated_payment_async.apply_async(
                            args=[str(tx.id), target_status_str, failure_reason],
                            countdown=2,
                        )
                    except Exception:
                        # Graceful handling when Celery broker is offline in tests/local
                        pass

        return MockPaymentResult(
            scenario=chosen_scenario,
            status=status,
            provider_ref_id=provider_ref_id,
            amount=amount,
            settled_amount=settled_amount,
            idempotency_key=idempotency_key,
            payer_vpa=vpa,
            failure_reason=failure_reason,
            is_async=is_async,
            duplicate_of_transaction_id=duplicate_of_id,
            created_at=now,
        )

    @classmethod
    def resolve_async_settlement(
        cls,
        db: Session,
        transaction_id: uuid.UUID,
        target_status: TransactionStatus,
        reason: Optional[str] = None,
    ) -> PaymentTransaction:
        """Direct/synchronous settlement resolution method invoked by Celery tasks or tests.

        Transitions transaction state, appends status history, creates inbound webhook event,
        and records an audit log.
        """
        tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == transaction_id).first()
        if not tx:
            raise EntityNotFoundException("PaymentTransaction", transaction_id)

        old_status = tx.status.value
        tx.status = target_status
        tx.completed_at = datetime.now(timezone.utc)
        if target_status == TransactionStatus.FAILED and reason:
            tx.failure_reason = reason

        history = TransactionStatusHistory(
            transaction_id=tx.id,
            from_status=old_status,
            to_status=target_status.value,
            reason=reason or f"MockUPIProvider async resolution ({old_status} -> {target_status.value})",
        )
        db.add(history)

        # Inbound webhook event (mimics bank webhook arrival)
        event_type = "payment.success" if target_status == TransactionStatus.SUCCESS else "payment.failed"
        webhook = WebhookEventInbound(
            provider="MOCK_UPI_PROVIDER",
            event_type=event_type,
            payload={
                "event": event_type,
                "provider": "MOCK_UPI_SIMULATOR",
                "transaction_id": str(tx.id),
                "provider_ref_id": tx.provider_ref_id,
                "amount": str(tx.amount),
                "status": target_status.value,
                "idempotency_key": tx.idempotency_key,
                "resolved_at": tx.completed_at.isoformat(),
                "simulated": True,
            },
            headers={"X-Mock-Provider": "PayFlowSimulator/1.0"},
            status=WebhookInboundStatus.RECEIVED,
        )
        db.add(webhook)

        record_audit(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_name="payment_transactions",
            entity_id=tx.id,
            merchant_id=tx.merchant_id,
            before={"status": old_status},
            after={"status": target_status.value, "async_resolution": True},
        )

        db.commit()
        db.refresh(tx)
        return tx

    @classmethod
    def check_transaction_status(
        cls,
        db: Session,
        transaction: PaymentTransaction,
    ) -> TransactionStatus:
        """Simulates an inquiry to the upstream UPI/banking switch for an in-flight transaction.

        If mock_scenario was PENDING, resolves to SUCCESS.
        If mock_scenario was TIMEOUT or FAILED, resolves to FAILED.
        Defaults to SUCCESS for simulated clearing.
        """
        scenario = transaction.mock_scenario
        if scenario in [MockScenario.PENDING.value, "PENDING"]:
            return TransactionStatus.SUCCESS
        elif scenario in [MockScenario.TIMEOUT.value, "TIMEOUT", MockScenario.FAILED.value, "FAILED"]:
            return TransactionStatus.FAILED
        return TransactionStatus.SUCCESS
