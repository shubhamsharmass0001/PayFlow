"""FastAPI routes for the AI Assistant Module."""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.ai_assistant.schemas import AIAssistantQueryRequest, AIAssistantQueryResponse
from app.modules.ai_assistant.service import AIAssistantService
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission

router = APIRouter(tags=["AI Assistant"])


@router.post(
    "/merchants/{id}/ai-assistant/query",
    response_model=AIAssistantQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Natural-Language Merchant Analytics Q&A",
    description=(
        "Accepts a natural-language question, retrieves relevant ground-truth structured "
        "records (invoices, analytics trends, settlements, transactions), and generates an "
        "auditable, grounded natural-language answer with explicit citations and the underlying data. "
        "Strictly read-only — cannot perform mutations, refunds, or payments."
    ),
)
async def query_ai_assistant(
    id: uuid.UUID,
    payload: AIAssistantQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("payments:read")),
) -> AIAssistantQueryResponse:
    """Answers merchant queries grounded strictly in real database records."""
    return await AIAssistantService.process_query(
        db=db,
        merchant_id=id,
        question=payload.question,
    )
