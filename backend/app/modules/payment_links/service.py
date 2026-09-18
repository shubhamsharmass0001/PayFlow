import secrets
import string
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.invoices.models import Invoice
from app.modules.merchants.models import Merchant
from app.modules.payment_links.models import PaymentLink, PaymentLinkStatus
from app.modules.payment_links.schemas import (
    PaymentLinkCreateRequest,
    PaymentLinkResponse,
    PublicPayPageResponse,
)
from app.modules.payment_requests.models import PaymentRequest
from app.modules.payment_requests.service import get_payment_request_by_id
from app.modules.stores.models import Store
from app.modules.upi_qr.models import UpiQrCode
from app.shared.exceptions import BadRequestException, EntityNotFoundException


def generate_unique_slug(db: Session, length: int = 8) -> str:
    """Generates a short, collision-safe, URL-safe alphanumeric slug for public payment links."""
    alphabet = string.ascii_letters + string.digits
    for _ in range(10):
        slug = "".join(secrets.choice(alphabet) for _ in range(length))
        exists = db.query(PaymentLink.id).filter(PaymentLink.short_code == slug).first()
        if not exists:
            return slug
    return secrets.token_urlsafe(length)[:length]


def create_payment_link(
    db: Session,
    payment_request_id: uuid.UUID,
    request: PaymentLinkCreateRequest,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PaymentLink:
    """Creates a short-slug payment link bound to an immutable payment_request."""
    pr = get_payment_request_by_id(db, payment_request_id)

    slug = generate_unique_slug(db)
    expires_at = request.expires_at or pr.expires_at
    max_uses = request.max_uses if request.max_uses is not None else 1

    link = PaymentLink(
        merchant_id=pr.merchant_id,
        invoice_id=pr.invoice_id,
        customer_id=pr.customer_id,
        payment_request_id=pr.id,
        short_code=slug,
        amount=pr.amount,
        status=PaymentLinkStatus.ACTIVE,
        expires_at=expires_at,
        max_uses=max_uses,
        use_count=0,
        allow_partial=False,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    # Audit logging
    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="payment_links",
        entity_id=link.id,
        actor_id=actor.id,
        merchant_id=pr.merchant_id,
        before=None,
        after={
            "payment_request_id": str(pr.id),
            "short_code": link.short_code,
            "amount": str(link.amount),
            "max_uses": link.max_uses,
            "expires_at": link.expires_at.isoformat(),
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return link


def get_public_pay_summary(db: Session, slug: str) -> PublicPayPageResponse:
    """Retrieves checkout information for a customer-facing pay page without authentication.

    TAMPER-PROOF GUARANTEE:
      The payable amount is strictly read from the database record associated with this link.
      No client-supplied query parameters, headers, or request payload can alter the amount.
    """
    link = (
        db.query(PaymentLink)
        .filter(PaymentLink.short_code == slug, PaymentLink.deleted_at.is_(None))
        .first()
    )
    if not link:
        raise EntityNotFoundException("PaymentLink", slug)

    now = datetime.now(timezone.utc)
    if now > link.expires_at:
        if link.status != PaymentLinkStatus.EXPIRED:
            link.status = PaymentLinkStatus.EXPIRED
            db.commit()
        raise BadRequestException(
            message="This payment link has expired.",
            code="PAYMENT_LINK_EXPIRED",
            details={"expires_at": link.expires_at.isoformat()},
        )

    if link.use_count >= link.max_uses:
        raise BadRequestException(
            message="This payment link has reached its maximum allowed uses.",
            code="PAYMENT_LINK_MAX_USES_REACHED",
            details={"max_uses": link.max_uses, "use_count": link.use_count},
        )

    if link.status != PaymentLinkStatus.ACTIVE:
        raise BadRequestException(
            message=f"This payment link is no longer active (status: {link.status.value}).",
            code="PAYMENT_LINK_INACTIVE",
        )

    merchant = db.query(Merchant).filter(Merchant.id == link.merchant_id).first()
    merchant_name = merchant.business_name if merchant else "PayFlow Merchant"

    store_name = None
    invoice_number = None
    if link.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == link.invoice_id).first()
        if invoice:
            invoice_number = invoice.invoice_number
            if invoice.store_id:
                store = db.query(Store).filter(Store.id == invoice.store_id).first()
                if store:
                    store_name = store.name

    purpose = None
    if link.payment_request_id:
        pr = db.query(PaymentRequest).filter(PaymentRequest.id == link.payment_request_id).first()
        if pr:
            purpose = pr.purpose

    # Optional UPI QR string if already generated
    upi_string = None
    qr_data_url = None
    if link.payment_request_id:
        qr = db.query(UpiQrCode).filter(UpiQrCode.payment_request_id == link.payment_request_id).first()
        if qr:
            upi_string = qr.upi_string

    return PublicPayPageResponse(
        slug=link.short_code,
        merchant_name=merchant_name,
        store_name=store_name,
        invoice_number=invoice_number,
        amount=link.amount,
        currency="INR",
        purpose=purpose,
        status=link.status,
        expires_at=link.expires_at,
        upi_string=upi_string,
        qr_data_url=qr_data_url,
        is_mock_provider=True,
    )
