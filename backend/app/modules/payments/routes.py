import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.payment_requests.schemas import PaymentRequestResponse
from app.modules.payments.models import PaymentMethod, PaymentTransaction, TransactionStatus
from app.modules.payments.schemas import (
    InitiatePaymentRequest,
    PaymentTransactionResponse,
)
from app.modules.payments.service import PaymentService
from app.core.security import get_current_user
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Payments"])


@router.post(
    "/payments/initiate",
    response_model=PaymentTransactionResponse,
    summary="Initiate payment transaction with idempotency guarantee",
)
def initiate_payment(
    payload: InitiatePaymentRequest,
    response: Response,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        description="Unique client idempotency key (UUID or random string)",
    ),
    db: Session = Depends(get_db),
):
    """Initiates a payment transaction with strict idempotency and finite state machine tracking.

    If a transaction with the given Idempotency-Key exists, returns the existing record
    without re-initiating. Otherwise initiates the payment via MockUPIProvider simulator,
    updating status history immutably within an atomic Postgres transaction.
    """
    tx, is_new = PaymentService.initiate_payment(
        db=db,
        payload=payload,
        idempotency_key=idempotency_key,
    )
    if is_new:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return tx


@router.get(
    "/payments/{id}",
    response_model=PaymentTransactionResponse,
    summary="Get payment transaction by ID",
)
def get_payment_transaction(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Retrieves full details for a payment transaction, including status history."""
    return PaymentService.get_transaction_by_id(db=db, transaction_id=id)


@router.get(
    "/merchants/{id}/transactions",
    response_model=PaginatedResponse[PaymentTransactionResponse],
    summary="List merchant transactions with filters and search",
)
def list_merchant_transactions(
    id: uuid.UUID,
    status: Optional[str] = Query(None, description="Filter by transaction status (e.g. pending, success, failed)"),
    method: Optional[PaymentMethod] = Query(None, alias="method", description="Filter by payment method"),
    from_date: Optional[datetime] = Query(None, description="Start date filter"),
    to_date: Optional[datetime] = Query(None, description="End date filter"),
    search: Optional[str] = Query(None, description="Search by provider_ref_id, invoice number, or customer name"),
    flag: Optional[str] = Query(None, description="Filter by transaction flag (e.g. 'duplicate')"),
    stuck: Optional[bool] = Query(None, description="Filter stuck transactions in PENDING/INITIATED past threshold"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payments:read")),
):
    """Retrieves paginated transactions for a merchant.

    Requires 'payments:read' permission for the merchant.
    """
    return PaymentService.list_merchant_transactions(
        db=db,
        merchant_id=id,
        pagination=pagination,
        status=status,
        payment_method=method,
        from_date=from_date,
        to_date=to_date,
        search=search,
        flag=flag,
        stuck=stuck,
    )


@router.post(
    "/payments/{id}/regenerate-request",
    response_model=PaymentRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Regenerate payment request for a failed/timed-out transaction",
)
def regenerate_payment_request(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generates a new payment request for a FAILED or TIMEOUT transaction against the same invoice.

    Reuses Phase 6 payment_requests logic and enforces remaining balance without mutating the failed transaction.
    """
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == id).first()
    if not tx:
        raise EntityNotFoundException("PaymentTransaction", id)

    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=tx.merchant_id,
        permission_code="payments:write",
    )

    return PaymentService.regenerate_payment_request_for_failed_transaction(
        db=db,
        transaction_id=id,
        actor=current_user,
    )
