import uuid
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.schemas import InitiatePaymentRequest, PaymentTransactionResponse
from app.modules.payments.service import PaymentService
from app.modules.risk.models import RiskAction, RiskLevel, RiskSignal
from app.modules.splits.models import (
    InstallmentStatus,
    PaymentPlan,
    PaymentPlanInstallment,
    PaymentPlanStatus,
    PlanType,
)
from app.modules.splits.schemas import (
    CreatePaymentPlanRequest,
    InitiateInstallmentPaymentRequest,
)
from app.shared.exceptions import BadRequestException, EntityNotFoundException


class SplitsService:
    """Business logic for Payment Plans, Installments, and Anti-Structuring Heuristics."""

    @staticmethod
    def check_structuring_pattern(
        db: Session,
        merchant_id: uuid.UUID,
        invoice_id: uuid.UUID,
        installments: List,
    ) -> Optional[RiskSignal]:
        """Anti-Structuring (Smurfing) Heuristic Guardrail.

        Heuristic:
          - More than 3 installments (>3).
          - Each installment amount is in a narrow band just under ₹2,000 (₹1,800.00 <= amount < ₹2,000.00).
          - All installments share the exact same due date (same calendar day, no date/milestone spread).

        Action:
          Does NOT block plan creation outright. Instead, generates an auditable RiskSignal
          with signal_type="STRUCTURING_PATTERN" and action_taken="FLAG_FOR_REVIEW" for compliance review (Phase 19).
        """
        if len(installments) <= 3:
            return None

        # Check if all installments fall in narrow band just below ₹2,000
        narrow_band = all(
            Decimal("1800.00") <= inst.amount < Decimal("2000.00") for inst in installments
        )
        if not narrow_band:
            return None

        # Check if all installments are scheduled on the same calendar day
        dates = [inst.due_date.date() for inst in installments]
        same_day = len(set(dates)) == 1

        if narrow_band and same_day:
            risk_signal = RiskSignal(
                merchant_id=merchant_id,
                risk_score=Decimal("80.00"),
                risk_level=RiskLevel.HIGH,
                rule_triggered="STRUCTURING_PATTERN",
                action_taken=RiskAction.FLAG_FOR_REVIEW,
                metadata_json={
                    "signal_type": "STRUCTURING_PATTERN",
                    "invoice_id": str(invoice_id),
                    "installment_count": len(installments),
                    "amounts": [str(inst.amount) for inst in installments],
                    "due_date": dates[0].isoformat(),
                    "rationale": (
                        "Detected >3 installments near ₹2,000 on the same date with no temporal "
                        "distribution (anti-structuring guardrail triggered)."
                    ),
                },
            )
            db.add(risk_signal)
            db.flush()

            # Dispatch notification on risk signal raised
            try:
                from app.modules.notifications.service import NotificationService
                from app.modules.notifications.models import NotificationChannel
                NotificationService.send_notification(
                    merchant_id=merchant_id,
                    channel=NotificationChannel.PUSH,
                    template="risk_signal_raised",
                    payload={
                        "risk_signal_id": str(risk_signal.id),
                        "rule_triggered": "STRUCTURING_PATTERN",
                        "risk_score": "80.00",
                        "risk_level": "HIGH",
                        "invoice_id": str(invoice_id),
                    },
                )
            except Exception:
                pass

            return risk_signal

        return None

    @classmethod
    def create_payment_plan(
        cls,
        db: Session,
        invoice_id: uuid.UUID,
        payload: CreatePaymentPlanRequest,
    ) -> PaymentPlan:
        """Creates a payment plan and installments, enforcing exact invoice reconciliation

        and evaluating the anti-structuring heuristic.
        """
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise EntityNotFoundException("Invoice", invoice_id)

        # 1. Reconcile installments total to invoice amount
        # For DEPOSIT plans: sum must equal (grand_total - already_collected_deposit)
        # For all other plans: sum must equal full invoice total_amount
        if payload.plan_type == PlanType.DEPOSIT:
            required_amount = invoice.total_amount - invoice.paid_amount
        else:
            required_amount = invoice.total_amount

        sum_installments = sum((inst.amount for inst in payload.installments), Decimal("0.00"))

        if sum_installments != required_amount:
            raise BadRequestException(
                message=(
                    f"Installment amounts sum ({sum_installments}) does not reconcile to "
                    f"required invoice amount ({required_amount})."
                ),
                code="PLAN_RECONCILIATION_FAILED",
                details={
                    "invoice_id": str(invoice_id),
                    "invoice_total": str(invoice.total_amount),
                    "already_paid": str(invoice.paid_amount),
                    "required_amount": str(required_amount),
                    "sum_installments": str(sum_installments),
                    "plan_type": payload.plan_type.value,
                },
            )

        # 2. Evaluate Anti-Structuring Heuristic Guardrail
        cls.check_structuring_pattern(
            db=db,
            merchant_id=invoice.merchant_id,
            invoice_id=invoice.id,
            installments=payload.installments,
        )

        # 3. Create PaymentPlan record
        plan = PaymentPlan(
            merchant_id=invoice.merchant_id,
            invoice_id=invoice.id,
            customer_id=invoice.customer_id,
            plan_type=payload.plan_type,
            total_amount=sum_installments,
            status=PaymentPlanStatus.ACTIVE,
        )
        db.add(plan)
        db.flush()

        # 4. Create ordered PaymentPlanInstallment records
        for idx, inst_data in enumerate(payload.installments, start=1):
            installment = PaymentPlanInstallment(
                payment_plan_id=plan.id,
                installment_number=idx,
                label=inst_data.label or f"Installment {idx}",
                amount=inst_data.amount,
                paid_amount=Decimal("0.00"),
                due_date=inst_data.due_date,
                status=InstallmentStatus.PENDING,
            )
            db.add(installment)

        record_audit(
            db=db,
            action=AuditAction.CREATE,
            entity_name="payment_plans",
            entity_id=plan.id,
            merchant_id=plan.merchant_id,
            before=None,
            after={
                "plan_type": plan.plan_type.value,
                "total_amount": str(plan.total_amount),
                "installments_count": len(payload.installments),
            },
        )

        db.commit()
        db.refresh(plan)
        return plan

    @classmethod
    def initiate_installment_payment(
        cls,
        db: Session,
        plan_id: uuid.UUID,
        installment_id: uuid.UUID,
        payload: InitiateInstallmentPaymentRequest,
        idempotency_key: str,
    ) -> PaymentTransactionResponse:
        """Initiates an independent payment transaction linked to an installment.

        Reuses Phase 8's PaymentService.initiate_payment flow.
        """
        plan = (
            db.query(PaymentPlan)
            .options(joinedload(PaymentPlan.installments))
            .filter(PaymentPlan.id == plan_id)
            .first()
        )
        if not plan:
            raise EntityNotFoundException("PaymentPlan", plan_id)

        installment = (
            db.query(PaymentPlanInstallment)
            .filter(
                PaymentPlanInstallment.id == installment_id,
                PaymentPlanInstallment.payment_plan_id == plan_id,
            )
            .first()
        )
        if not installment:
            raise EntityNotFoundException("PaymentPlanInstallment", installment_id)

        if installment.status == InstallmentStatus.PAID:
            raise BadRequestException(
                message="Installment is already paid.",
                code="INSTALLMENT_ALREADY_PAID",
                details={"installment_id": str(installment_id)},
            )

        invoice = db.query(Invoice).filter(Invoice.id == plan.invoice_id).first() if plan.invoice_id else None

        # Build InitiatePaymentRequest reusing Phase 8
        payment_request = InitiatePaymentRequest(
            merchant_id=plan.merchant_id,
            amount=installment.amount,
            currency=invoice.currency if invoice else "INR",
            invoice_id=plan.invoice_id,
            customer_id=plan.customer_id,
            payment_method=payload.payment_method,
            payer_vpa=payload.payer_vpa,
            installment_id=installment.id,
            scenario=payload.scenario,
        )

        tx, is_new = PaymentService.initiate_payment(
            db=db,
            payload=payment_request,
            idempotency_key=idempotency_key,
        )

        return tx

    @staticmethod
    def get_payment_plans_for_invoice(
        db: Session,
        invoice_id: uuid.UUID,
    ) -> List[PaymentPlan]:
        """Retrieves all payment plans and installments for an invoice."""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise EntityNotFoundException("Invoice", invoice_id)

        return (
            db.query(PaymentPlan)
            .options(joinedload(PaymentPlan.installments))
            .filter(PaymentPlan.invoice_id == invoice_id)
            .order_by(PaymentPlan.created_at.desc())
            .all()
        )
