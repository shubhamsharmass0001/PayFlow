"""Risk Module Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.risk.models import RiskAction, RiskLevel


class ReviewRiskSignalRequest(BaseModel):
    """Payload to review and resolve a raised risk signal."""
    reviewed_by: Optional[uuid.UUID] = Field(
        None,
        description="UUID of reviewer (defaults to authenticated user if omitted)",
    )
    resolution_note: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Auditable explanation of the review outcome or dismissal reason",
    )
    action_taken: Optional[RiskAction] = Field(
        None,
        description="Optional updated action (e.g. ALLOW or BLOCK)",
    )


class RiskSignalResponse(BaseModel):
    """Full detail of a recorded risk signal."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    transaction_id: Optional[uuid.UUID] = None
    risk_score: Decimal
    risk_level: RiskLevel
    rule_triggered: str
    action_taken: RiskAction
    metadata_json: Optional[Dict[str, Any]] = None
    is_reviewed: bool
    reviewed_by: Optional[uuid.UUID] = None
    reviewed_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime

    @property
    def severity(self) -> RiskLevel:
        return self.risk_level

    @property
    def reviewed(self) -> bool:
        return self.is_reviewed

    model_config = ConfigDict(from_attributes=True)


class RiskRuleDefinition(BaseModel):
    """Auditable documentation for a single risk detection rule."""
    rule_name: str
    description: str
    evaluation_trigger: str
    thresholds: Dict[str, Any]
    default_severity: RiskLevel
    default_action: RiskAction
    rationale: str


class RiskRulesDocumentationResponse(BaseModel):
    """Collection of explainable, transparent risk rules deployed in the engine."""
    module: str = "PayFlow Fraud & Anomaly Risk Engine"
    version: str = "1.0.0"
    auditable: bool = True
    rules: List[RiskRuleDefinition]
