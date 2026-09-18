"""Notifications Module Schemas.

Pydantic schemas for notification responses, listings, and read-status updates.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.modules.notifications.models import NotificationChannel, NotificationStatus


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    merchant_id: Optional[uuid.UUID] = None
    recipient: str
    channel: NotificationChannel
    template: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    title: str
    content: str
    status: NotificationStatus
    is_read: bool = False
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime


class MarkReadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_read: bool
    read_at: datetime
    message: str = "Notification marked as read"
