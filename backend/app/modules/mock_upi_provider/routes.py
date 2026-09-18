import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.mock_upi_provider.schemas import (
    DirectInitiateRequest,
    MockPaymentResult,
    SimulatePaymentRequest,
)
from app.modules.mock_upi_provider.service import MockUPIProvider
from app.modules.payments.models import PaymentTransaction
from app.modules.rbac.dependencies import verify_merchant_permission
from app.shared.exceptions import EntityNotFoundException

router = APIRouter(tags=["Mock UPI Provider (Simulator)"])


@router.post(
    "/payments/{id}/simulate",
    response_model=MockPaymentResult,
    status_code=status.HTTP_200_OK,
    summary="[Dev/Test Sandbox] Simulate a payment lifecycle scenario against a transaction",
)
def simulate_payment_transaction(
    id: uuid.UUID,
    payload: SimulatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dev-only endpoint to simulate UPI payment scenarios.

    EXPLICIT NOTICE:
      This is a simulator endpoint for development and testing. No real banking rails are touched.
      Supported scenarios: SUCCESS, FAILED, PENDING, TIMEOUT, DUPLICATE, PARTIAL_PAYMENT, REFUND.
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

    result = MockUPIProvider.initiate_payment(
        db=db,
        amount=tx.amount,
        vpa=tx.payer_vpa or tx.payee_vpa or "payer@mockupi",
        idempotency_key=tx.idempotency_key,
        scenario=payload.scenario,
        transaction_id=tx.id,
        merchant_id=tx.merchant_id,
    )
    return result


@router.post(
    "/mock-upi/initiate",
    response_model=MockPaymentResult,
    status_code=status.HTTP_200_OK,
    summary="[Sandbox Simulator] Directly trigger simulated payment with chosen scenario",
)
def direct_mock_initiate(
    payload: DirectInitiateRequest,
    db: Session = Depends(get_db),
):
    """Direct standalone invocation of the Mock UPI Provider simulator."""
    return MockUPIProvider.initiate_payment(
        db=db,
        amount=payload.amount,
        vpa=payload.vpa,
        idempotency_key=payload.idempotency_key,
        scenario=payload.scenario,
        merchant_id=payload.merchant_id,
    )
