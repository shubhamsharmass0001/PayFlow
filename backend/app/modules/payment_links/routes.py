from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rate_limit import rate_limit_dependency
from app.db.session import get_db
from app.modules.payment_links.schemas import PublicPayPageResponse
from app.modules.payment_links.service import get_public_pay_summary

router = APIRouter(tags=["Public Pay Page"])


@router.get(
    "/pay/{slug}",
    response_model=PublicPayPageResponse,
    summary="Public customer-facing checkout page (Tamper-Proof Amount)",
    dependencies=[Depends(rate_limit_dependency(max_requests=60, window_seconds=60, key_prefix="public_pay"))],
)
def get_public_pay_page(
    slug: str,
    db: Session = Depends(get_db),
):
    """Public customer checkout endpoint.

    SECURITY & TAMPER-PROOFING:
      - Does not require user authentication.
      - Amount is server-locked and derived from the PaymentLink / PaymentRequest record in the database.
      - Query parameters or client payloads cannot modify the payable amount.
      - Protected by IP rate limiting (60 req/min).
    """
    return get_public_pay_summary(db=db, slug=slug)

