import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.invoices.service import get_invoice_by_id
from app.modules.payment_links.schemas import (
    PaymentLinkCreateRequest,
    PaymentLinkResponse,
)
from app.modules.payment_links.service import create_payment_link
from app.modules.payment_requests.schemas import (
    PaymentRequestCreate,
    PaymentRequestResponse,
)
from app.modules.payment_requests.service import (
    create_payment_request,
    get_payment_request_by_id,
)
from app.modules.rbac.dependencies import verify_merchant_permission
from app.modules.upi_qr.schemas import UpiQrResponse
from app.modules.upi_qr.service import generate_payment_request_qr

router = APIRouter(tags=["Payment Requests, UPI QR & Links"])


@router.post(
    "/invoices/{id}/payment-requests",
    response_model=PaymentRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a payment request / installment against an invoice",
)
def post_payment_request(
    id: uuid.UUID,
    payload: PaymentRequestCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = get_invoice_by_id(db=db, invoice_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="payments:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    pr = create_payment_request(
        db=db,
        invoice_id=id,
        request=payload,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return PaymentRequestResponse.model_validate(pr)


@router.post(
    "/payment-requests/{id}/qr",
    response_model=UpiQrResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a UPI-intent QR payload and rendered image (MOCK provider trigger)",
)
def post_payment_request_qr(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pr = get_payment_request_by_id(db=db, payment_request_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=pr.merchant_id,
        permission_code="payments:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    qr_resp = generate_payment_request_qr(
        db=db,
        payment_request_id=id,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return qr_resp


@router.post(
    "/payment-requests/{id}/link",
    response_model=PaymentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a short unique slug payment link for public checkout",
)
def post_payment_request_link(
    id: uuid.UUID,
    payload: PaymentLinkCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pr = get_payment_request_by_id(db=db, payment_request_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=pr.merchant_id,
        permission_code="payments:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    link = create_payment_link(
        db=db,
        payment_request_id=id,
        request=payload,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    payment_url = f"/pay/{link.short_code}"
    res = PaymentLinkResponse(
        id=link.id,
        merchant_id=link.merchant_id,
        invoice_id=link.invoice_id,
        customer_id=link.customer_id,
        payment_request_id=link.payment_request_id,
        short_code=link.short_code,
        payment_url=payment_url,
        amount=link.amount,
        status=link.status,
        expires_at=link.expires_at,
        max_uses=link.max_uses,
        use_count=link.use_count,
        created_at=link.created_at,
    )
    return res
