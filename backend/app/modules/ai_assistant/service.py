"""Service layer for the AI Assistant Module."""

import uuid
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.modules.ai_assistant.llm_client import LLMClient
from app.modules.ai_assistant.retriever import StructuredDataRetriever
from app.modules.ai_assistant.schemas import AIAssistantQueryResponse
from app.modules.merchants.models import Merchant
from app.shared.exceptions import EntityNotFoundException


class AIAssistantService:
    """Orchestrates query processing, data retrieval, and grounded Q&A generation."""

    @classmethod
    async def process_query(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        question: str,
        llm_client: LLMClient | None = None,
    ) -> AIAssistantQueryResponse:
        """Processes a natural language question over the merchant's operational data."""
        # 1. Verify merchant existence
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            raise EntityNotFoundException(
                entity_name="Merchant",
                entity_id=str(merchant_id),
            )

        logger.info(
            "ai_assistant_query_received",
            merchant_id=str(merchant_id),
            question_length=len(question),
        )

        # 2. Retrieve grounded structured data
        retriever = StructuredDataRetriever(db, merchant_id)
        intent, underlying_data, citations = retriever.retrieve_context(question)

        # 3. Generate grounded answer
        client = llm_client or LLMClient()
        answer, model_used = await client.generate_answer(
            merchant_id=str(merchant_id),
            question=question,
            intent=intent,
            underlying_data=underlying_data,
            citations=citations,
        )

        logger.info(
            "ai_assistant_query_answered",
            merchant_id=str(merchant_id),
            intent=intent,
            citations_count=len(citations),
            model_used=model_used,
        )

        return AIAssistantQueryResponse(
            merchant_id=merchant_id,
            question=question,
            intent=intent,
            answer=answer,
            sources_cited=citations,
            underlying_data=underlying_data,
            model_used=model_used,
        )
