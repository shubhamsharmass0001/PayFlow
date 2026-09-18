"""Shared Pydantic schemas across modules."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard PayFlow JSON error response envelope."""
    code: str = Field(..., example="VALIDATION_ERROR", description="Machine-readable error code")
    message: str = Field(..., example="Invalid request payload or parameters.", description="Human-readable error description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured contextual error details or validation violations")
