"""Audit Module Pydantic Schemas."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.audit.models import AuditAction


class AuditChangeDiff(BaseModel):
    """Represents the diff for a single modified, added, or removed attribute."""
    before: Optional[Any] = None
    after: Optional[Any] = None
    status: str = Field(
        ...,
        description="Diff status: ADDED, MODIFIED, REMOVED, or UNCHANGED",
    )


class AuditLogListItemResponse(BaseModel):
    """Compact summary of an audit trail entry for table / feed listings."""
    id: uuid.UUID
    merchant_id: Optional[uuid.UUID] = None
    actor_user_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    actor_email: Optional[str] = None
    entity_type: str
    entity_name: str
    entity_id: uuid.UUID
    action: AuditAction
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogDetailResponse(BaseModel):
    """Detailed audit trail entry with full before/after states and structured diff."""
    id: uuid.UUID
    merchant_id: Optional[uuid.UUID] = None
    actor_user_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    actor_email: Optional[str] = None
    entity_type: str
    entity_name: str
    entity_id: uuid.UUID
    action: AuditAction
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    diff: Dict[str, AuditChangeDiff] = Field(default_factory=dict)
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
