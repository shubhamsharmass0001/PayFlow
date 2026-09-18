import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payment_requests.models import PaymentRequest, PaymentRequestStatus
from app.modules.payment_requests.schemas import PaymentRequestCreate
from app.shared.exceptions import BadRequestException, EntityNotFoundException


def get_payment_request_by_id(db: Session, payment_request_id: uuid.UUID) -> PaymentRequest:
    """Retrieves an active payment request by ID."""
    pr = db.query(PaymentRequest).filter(PaymentRequest.id == payment_request_id).first()
    if not pr:
        raise EntityNotFoundException("PaymentRequest", payment_request_id)
    return pr


def create_payment_request(
    db: Session,
    invoice_id: uuid.UUID,
    request: PaymentRequestCreate,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PaymentRequest:
    """Creates a payment request against an invoice.

    Multiple payment requests can legitimately exist against one invoice for partial/installment payments.
    Enforces that amount <= remaining invoice balance (total_amount - paid_amount).
    """
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.deleted_at.is_(None))
        .first()
    )
    if not invoice:
        raise EntityNotFoundException("Invoice", invoice_id)

    if invoice.status == InvoiceStatus.CANCELLED:
        raise BadRequestException(
            message="Cannot create payment requests for a CANCELLED invoice.",
            code="INVOICE_CANCELLED",
        )
    if invoice.status == InvoiceStatus.PAID:
        raise BadRequestException(
            message="Invoice is already fully PAID. Remaining balance is 0.00.",
            code="INVOICE_ALREADY_PAID",
        )

    remaining_balance = Decimal(str(invoice.total_amount)) - Decimal(str(invoice.paid_amount))
    if request.amount > remaining_balance:
        raise BadRequestException(
            message=(
                f"Requested amount ({request.amount}) exceeds invoice remaining balance "
                f"({remaining_balance})."
            ),
            code="AMOUNT_EXCEEDS_BALANCE",
            details={
                "remaining_balance": str(remaining_balance),
                "requested_amount": str(request.amount),
                "total_amount": str(invoice.total_amount),
                "paid_amount": str(invoice.paid_amount),
            },
        )

    expires_at = request.expires_at or (datetime.now(timezone.utc) + timedelta(days=1))

    payment_request = PaymentRequest(
        merchant_id=invoice.merchant_id,
        invoice_id=invoice.id,
        customer_id=invoice.customer_id,
        amount=request.amount,
        purpose=request.purpose,
        status=PaymentRequestStatus.PENDING,
        expires_at=expires_at,
        payer_vpa=request.payer_vpa,
    )
    db.add(payment_request)
    db.commit()
    db.refresh(payment_request)

    # Record audit log
    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="payment_requests",
        entity_id=payment_request.id,
        actor_id=actor.id,
        merchant_id=invoice.merchant_id,
        before=None,
        after={
            "invoice_id": str(invoice.id),
            "amount": str(payment_request.amount),
            "purpose": payment_request.purpose,
            "status": payment_request.status.value,
            "expires_at": payment_request.expires_at.isoformat(),
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return payment_request
