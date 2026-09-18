import uuid
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.customers.schemas import (
    CustomerCreateRequest,
    CustomerQueryFilter,
    CustomerResponse,
    CustomerUpdateRequest,
)
from app.modules.customers.service import (
    create_customer,
    get_customer_by_id,
    list_customers,
    update_customer,
)
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Customers"])


@router.get(
    "/merchants/{merchant_id}/customers",
    response_model=PaginatedResponse[CustomerResponse],
    summary="List merchant customers with pagination, search, and sorting",
)
def get_merchant_customers(
    merchant_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Case-insensitive search by name, phone, or email"),
    sort_by: Literal["name", "phone", "email", "created_at"] = Query(
        "created_at", description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort direction"),
    user: User = Depends(require_permission("customers:read")),
    db: Session = Depends(get_db),
):
    filter_params = CustomerQueryFilter(
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pagination = PaginationParams(page=page, page_size=page_size)
    return list_customers(
        db=db,
        merchant_id=merchant_id,
        filters=filter_params,
        pagination=pagination,
    )


@router.post(
    "/merchants/{merchant_id}/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer profile under a merchant (with deduplication check)",
)
def post_customer(
    merchant_id: uuid.UUID,
    payload: CustomerCreateRequest,
    request: Request,
    response: Response,
    user: User = Depends(require_permission("customers:write")),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    customer, warning_msg = create_customer(
        db=db,
        merchant_id=merchant_id,
        request=payload,
        actor=user,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    res = CustomerResponse.model_validate(customer)
    if warning_msg:
        res.warning = warning_msg
        response.headers["X-Warning"] = warning_msg

    return res


@router.get(
    "/customers/{id}",
    response_model=CustomerResponse,
    summary="Get customer profile by ID",
)
def get_customer(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer = get_customer_by_id(db=db, customer_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=customer.merchant_id,
        permission_code="customers:read",
    )
    return CustomerResponse.model_validate(customer)


@router.patch(
    "/customers/{id}",
    response_model=CustomerResponse,
    summary="Update customer profile attributes",
)
def patch_customer(
    id: uuid.UUID,
    payload: CustomerUpdateRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer = get_customer_by_id(db=db, customer_id=id)
    verify_merchant_permission(
        db=db,
        user=current_user,
        merchant_id=customer.merchant_id,
        permission_code="customers:write",
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated, warning_msg = update_customer(
        db=db,
        customer_id=id,
        request=payload,
        actor=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    res = CustomerResponse.model_validate(updated)
    if warning_msg:
        res.warning = warning_msg
        response.headers["X-Warning"] = warning_msg

    return res
