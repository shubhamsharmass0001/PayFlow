import uuid
from typing import List
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.invoices.service import get_invoice_by_id
from app.modules.payments.schemas import PaymentTransactionResponse
from app.modules.rbac.dependencies import verify_merchant_permission
from app.modules.splits.schemas import (
    CreatePaymentPlanRequest,
    InitiateInstallmentPaymentRequest,
    PaymentPlanResponse,
)
from app.modules.splits.service import SplitsService

router = APIRouter(tags=["Splits & Payment Plans"])


@router.post(
    "/invoices/{id}/payment-plans",
    response_model=PaymentPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a structured payment plan with installments for an invoice",
)
def create_payment_plan(
    id: uuid.UUID,
    payload: CreatePaymentPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a payment plan (DEPOSIT, INSTALLMENT, MILESTONE, CUSTOM_SPLIT)

    whose installments sum exactly to the invoice grand total (or remaining balance if DEPOSIT).
    Evaluates anti-structuring heuristic guardrail (flagging >3 installments near ₹2,000 on the same date).
    """
    invoice = get_invoice_by_id(db=db, invoice_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="invoices:write",
    )

    return SplitsService.create_payment_plan(
        db=db,
        invoice_id=id,
        payload=payload,
    )


@router.get(
    "/invoices/{id}/payment-plans",
    response_model=List[PaymentPlanResponse],
    summary="Get payment plans and installment statuses for an invoice",
)
def get_invoice_payment_plans(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all payment plans and installment progress for an invoice."""
    invoice = get_invoice_by_id(db=db, invoice_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="invoices:read",
    )

    return SplitsService.get_payment_plans_for_invoice(
        db=db,
        invoice_id=id,
    )


@router.post(
    "/payment-plans/{id}/installments/{installment_id}/initiate",
    response_model=PaymentTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate payment transaction for an installment",
)
def initiate_installment_payment(
    id: uuid.UUID,
    installment_id: uuid.UUID,
    payload: InitiateInstallmentPaymentRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        description="Unique client-supplied idempotency key",
    ),
    db: Session = Depends(get_db),
):
    """Initiates an independent payment transaction linked to a specific installment,

    reusing Phase 8's core payment initiation flow.
    On SUCCESS, marks the installment as PAID and recomputes plan and invoice statuses.
    """
    return SplitsService.initiate_installment_payment(
        db=db,
        plan_id=id,
        installment_id=installment_id,
        payload=payload,
        idempotency_key=idempotency_key,
    )
