import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.modules.webhooks.models import WebhookDeliveryStatus, WebhookInboundStatus


class InboundWebhookPayload(BaseModel):
    event_id: Optional[str] = Field(None, description="Unique provider event UUID/identifier")
    event_type: str = Field(default="payment.success", description="Gateway event topic")
    transaction_id: Optional[uuid.UUID] = Field(None, description="Target transaction ID")
    provider_ref_id: Optional[str] = Field(None, description="Bank/provider RRN")
    status: Optional[str] = Field(None, description="Updated transaction status (SUCCESS/FAILED/etc)")
    amount: Optional[Decimal] = Field(None, description="Amount")
    failure_reason: Optional[str] = Field(None, description="Failure reason if declined")
    simulated: Optional[bool] = Field(False, description="Simulator flag")


class InboundWebhookResponse(BaseModel):
    status: str
    event_id: Optional[str] = None
    transaction_id: Optional[str] = None
    message: Optional[str] = None


class WebhookSubscriptionCreate(BaseModel):
    target_url: str = Field(..., max_length=1024, description="Destination webhook HTTP(S) endpoint URL")
    secret_key: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional shared signing HMAC secret (generated automatically if omitted)",
    )
    subscribed_events: List[str] = Field(
        ...,
        min_length=1,
        description="List of event topics (e.g. ['payment.success', 'payment.failed', 'invoice.paid', 'refund.*'])",
    )
    is_active: bool = Field(default=True, description="Active status")


class WebhookSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    target_url: str
    secret_key: str
    subscribed_events: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class WebhookDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subscription_id: uuid.UUID
    event_type: str
    payload: Dict[str, Any]
    response_status_code: Optional[int] = None
    response_body: Optional[str] = None
    attempt_count: int
    status: WebhookDeliveryStatus
    next_retry_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
