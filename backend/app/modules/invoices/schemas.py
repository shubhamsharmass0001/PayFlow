import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.invoices.models import InvoiceStatus


class InvoiceItemCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product or service name")
    description: Optional[str] = Field(None, description="Line item description")
    quantity: Decimal = Field(default=Decimal("1.00"), gt=0, description="Quantity billed")
    unit_price: Decimal = Field(..., ge=0, description="Unit price per item")
    tax_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Tax rate percentage (e.g. 18.00 for 18% GST)")
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Line item discount amount")


class InvoiceItemResponse(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    name: str
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    discount_amount: Decimal
    line_total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceCreateRequest(BaseModel):
    customer_id: Optional[uuid.UUID] = Field(None, description="Optional target customer UUID")
    store_id: Optional[uuid.UUID] = Field(None, description="Optional store/branch location UUID")
    due_date: Optional[datetime] = Field(None, description="Invoice payment due timestamp")
    allow_partial_payment: bool = Field(default=False, description="Flag allowing customer to pay in installments")
    allow_split_payment: bool = Field(default=False, description="Flag allowing split tender payments")
    currency: str = Field(default="INR", min_length=3, max_length=3, description="ISO currency code")
    notes: Optional[str] = Field(None, description="Optional customer notes or invoice terms")
    items: Optional[List[InvoiceItemCreateRequest]] = Field(default=None, description="Optional initial line items")


class InvoiceUpdateRequest(BaseModel):
    status: Optional[InvoiceStatus] = Field(None, description="Target invoice status (DRAFT -> SENT -> CANCELLED)")
    notes: Optional[str] = Field(None, description="Updated notes")
    due_date: Optional[datetime] = Field(None, description="Updated due date")
    allow_partial_payment: Optional[bool] = Field(None, description="Updated allow partial payment")
    allow_split_payment: Optional[bool] = Field(None, description="Updated allow split payment")


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    merchant_id: uuid.UUID
    store_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    invoice_number: str
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    currency: str
    status: InvoiceStatus
    allow_partial_payment: bool
    allow_split_payment: bool
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceFilterParams(BaseModel):
    status: Optional[InvoiceStatus] = Field(None, description="Filter by invoice status")
    from_date: Optional[datetime] = Field(None, description="Filter invoices created on or after this timestamp")
    to_date: Optional[datetime] = Field(None, description="Filter invoices created on or before this timestamp")
    search: Optional[str] = Field(None, description="Search across invoice_number or customer name")
    sort_by: Literal["created_at", "total_amount", "invoice_number", "due_date"] = Field(
        default="created_at", description="Sort attribute"
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="desc", description="Sort direction"
    )
