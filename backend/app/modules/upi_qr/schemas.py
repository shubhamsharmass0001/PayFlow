import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.upi_qr.models import QrStatus, QrType


class UpiQrResponse(BaseModel):
    id: uuid.UUID
    merchant_id: uuid.UUID
    store_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None
    payment_request_id: Optional[uuid.UUID] = None
    qr_type: QrType
    upi_string: str
    image_url: Optional[str] = None
    qr_data_url: Optional[str] = Field(None, description="Base64 encoded data URI (data:image/png;base64,...)")
    amount: Optional[Decimal] = None
    status: QrStatus
    expires_at: Optional[datetime] = None
    note: str = Field(
        default="FOR PROTOTYPE MOCK PROVIDER TESTING ONLY - NOT CONNECTED TO NPCI/UPI RAILS",
        description="Notice indicating mock environment"
    )

    model_config = ConfigDict(from_attributes=True)
