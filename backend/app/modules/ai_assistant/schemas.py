"""Pydantic schemas for the AI Assistant Module."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AIAssistantQueryRequest(BaseModel):
    """Natural language query payload submitted to the AI assistant."""

    question: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="Natural language question about merchant analytics, transactions, settlements, or invoices.",
        examples=["Why did revenue dip last Tuesday?", "Which customers have overdue invoices?"],
    )


class SourceCitation(BaseModel):
    """A citation referencing a specific database record or metric used to ground the answer."""

    entity_type: str = Field(
        ...,
        description="Type of entity cited (e.g. invoice, transaction, settlement, customer, analytics_metric)",
        examples=["invoice", "transaction", "settlement", "analytics_metric"],
    )
    id: Optional[str] = Field(
        None,
        description="UUID or primary key of the cited entity, if applicable.",
    )
    reference: str = Field(
        ...,
        description="Human-readable reference (e.g. invoice number, UTR number, metric label, or customer name).",
        examples=["INV-MKT-2026-00001", "UTR20260918-ABCD1234", "today_collections"],
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key metadata values cited from this record.",
    )


class AIAssistantQueryResponse(BaseModel):
    """Response returned by the AI assistant."""

    merchant_id: uuid.UUID = Field(..., description="Target merchant UUID.")
    question: str = Field(..., description="Original user question.")
    intent: str = Field(
        ...,
        description="Detected Q&A intent category (e.g. OVERDUE_INVOICES, REVENUE_ANALYTICS, SETTLEMENTS_SUMMARY, etc.).",
    )
    answer: str = Field(
        ...,
        description="Grounded natural-language explanation strictly derived from retrieved data.",
    )
    sources_cited: List[SourceCitation] = Field(
        default_factory=list,
        description="List of specific database records or metrics cited in the answer.",
    )
    underlying_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Actual structured JSON data retrieved from services and provided to the model.",
    )
    model_used: Optional[str] = Field(
        default=None,
        description="Model or engine used for synthesis (e.g. 'claude-3-5-sonnet-20241022' or 'deterministic-grounded-synthesizer').",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of Q&A response generation.",
    )

    model_config = ConfigDict(from_attributes=True)
