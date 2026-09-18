import uuid
from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.invoice_items.models import InvoiceItem
from app.modules.invoices.models import InvoiceStatus
from app.modules.invoices.schemas import (
    InvoiceCreateRequest,
    InvoiceFilterParams,
    InvoiceItemCreateRequest,
    InvoiceResponse,
    InvoiceUpdateRequest,
)
from app.modules.invoices.service import (
    add_invoice_item,
    create_invoice,
    get_invoice_by_id,
    list_invoices,
    remove_invoice_item,
    update_invoice,
)
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Invoices"])


@router.post(
    "/merchants/{merchant_id}/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new draft invoice with collision-safe sequential number and server-computed totals",
)
def post_invoice(
    merchant_id: uuid.UUID,
    payload: InvoiceCreateRequest,
    request: Request,
    user: User = Depends(require_permission("invoices:write")),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    invoice = create_invoice(
        db=db,
        merchant_id=merchant_id,
        request=payload,
        actor=user,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return InvoiceResponse.model_validate(invoice)


@router.get(
    "/merchants/{merchant_id}/invoices",
    response_model=PaginatedResponse[InvoiceResponse],
    summary="List merchant invoices with filters, search, and pagination",
)
def get_merchant_invoices(
    merchant_id: uuid.UUID,
    status: Optional[InvoiceStatus] = Query(None, description="Filter by status (DRAFT, SENT, PAID, etc.)"),
    from_date: Optional[datetime] = Query(None, description="Created on or after timestamp"),
    to_date: Optional[datetime] = Query(None, description="Created on or before timestamp"),
    search: Optional[str] = Query(None, description="Search invoice_number or customer name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Literal["created_at", "total_amount", "invoice_number", "due_date"] = Query(
        "created_at", description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort direction"),
    user: User = Depends(require_permission("invoices:read")),
    db: Session = Depends(get_db),
):
    filters = InvoiceFilterParams(
        status=status,
        from_date=from_date,
        to_date=to_date,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pagination = PaginationParams(page=page, page_size=page_size)
    return list_invoices(db=db, merchant_id=merchant_id, filters=filters, pagination=pagination)


@router.get(
    "/invoices/{id}",
    response_model=InvoiceResponse,
    summary="Get invoice details by ID",
)
def get_invoice(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = get_invoice_by_id(db=db, invoice_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="invoices:read",
    )
    return InvoiceResponse.model_validate(invoice)


@router.patch(
    "/invoices/{id}",
    response_model=InvoiceResponse,
    summary="Update invoice details and execute controlled status transitions",
)
def patch_invoice(
    id: uuid.UUID,
    payload: InvoiceUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = get_invoice_by_id(db=db, invoice_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="invoices:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = update_invoice(
        db=db,
        invoice_id=id,
        request=payload,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return InvoiceResponse.model_validate(updated)


@router.post(
    "/invoices/{id}/items",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a line item to a DRAFT invoice and recompute totals",
)
def add_item_to_invoice(
    id: uuid.UUID,
    payload: InvoiceItemCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = get_invoice_by_id(db=db, invoice_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="invoices:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = add_invoice_item(
        db=db,
        invoice_id=id,
        request=payload,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return InvoiceResponse.model_validate(updated)


@router.delete(
    "/invoice-items/{id}",
    response_model=InvoiceResponse,
    summary="Delete a line item from a DRAFT invoice and recompute totals",
)
def delete_item_from_invoice(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(InvoiceItem)
        .filter(InvoiceItem.id == id, InvoiceItem.deleted_at.is_(None))
        .first()
    )
    if not item:
        raise EntityNotFoundException("InvoiceItem", id)

    invoice = get_invoice_by_id(db=db, invoice_id=item.invoice_id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=invoice.merchant_id,
        permission_code="invoices:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = remove_invoice_item(
        db=db,
        item_id=id,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return InvoiceResponse.model_validate(updated)
