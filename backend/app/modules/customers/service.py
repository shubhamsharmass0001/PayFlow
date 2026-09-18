import uuid
from typing import Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.customers.models import Customer
from app.modules.customers.schemas import (
    CustomerCreateRequest,
    CustomerQueryFilter,
    CustomerResponse,
    CustomerUpdateRequest,
)
from app.modules.merchants.models import Merchant
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams, paginate_query


def get_customer_by_id(db: Session, customer_id: uuid.UUID) -> Customer:
    """Retrieves an active customer profile by ID."""
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.deleted_at.is_(None))
        .first()
    )
    if not customer:
        raise EntityNotFoundException("Customer", customer_id)
    return customer


def list_customers(
    db: Session,
    merchant_id: uuid.UUID,
    filters: CustomerQueryFilter,
    pagination: PaginationParams,
) -> PaginatedResponse[CustomerResponse]:
    """Lists customers for a merchant with case-insensitive search, sorting, and pagination."""
    query = db.query(Customer).filter(
        Customer.merchant_id == merchant_id,
        Customer.deleted_at.is_(None),
    )

    # Case-insensitive search on name, phone, or email
    if filters.search and filters.search.strip():
        term = f"%{filters.search.strip()}%"
        query = query.filter(
            or_(
                Customer.name.ilike(term),
                Customer.phone.ilike(term),
                Customer.email.ilike(term),
            )
        )

    # Dynamic sorting
    sort_column_map = {
        "name": Customer.name,
        "phone": Customer.phone,
        "email": Customer.email,
        "created_at": Customer.created_at,
    }
    sort_column = sort_column_map.get(filters.sort_by, Customer.created_at)
    if filters.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    items, total = paginate_query(query, pagination)
    response_items = [CustomerResponse.model_validate(c) for c in items]

    return PaginatedResponse.create(
        items=response_items,
        total=total,
        params=pagination,
    )


def create_customer(
    db: Session,
    merchant_id: uuid.UUID,
    request: CustomerCreateRequest,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[Customer, Optional[str]]:
    """Creates a merchant customer profile.

    Deduplication:
      Checks for existing active customer with matching phone within this merchant.
      Does NOT silently merge or overwrite. Generates a warning notice if duplicate phone is detected.
    """
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None))
        .first()
    )
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    # Deduplication check: phone within merchant
    existing_by_phone = (
        db.query(Customer)
        .filter(
            Customer.merchant_id == merchant_id,
            Customer.phone == request.phone,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    warning_msg = None
    if existing_by_phone:
        warning_msg = (
            f"A customer with phone '{request.phone}' already exists for this merchant "
            f"(Customer ID: {existing_by_phone.id}). Created new customer profile without merging."
        )

    customer = Customer(
        merchant_id=merchant_id,
        name=request.name.strip(),
        phone=request.phone,
        email=str(request.email).lower() if request.email else None,
        upi_vpa=request.upi_vpa.strip() if request.upi_vpa else None,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    # Audit logging
    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="customers",
        entity_id=customer.id,
        actor_id=actor.id,
        merchant_id=merchant_id,
        before=None,
        after={
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "upi_vpa": customer.upi_vpa,
            "duplicate_phone_warning": warning_msg is not None,
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return customer, warning_msg


def update_customer(
    db: Session,
    customer_id: uuid.UUID,
    request: CustomerUpdateRequest,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[Customer, Optional[str]]:
    """Updates an existing customer profile with audit logging."""
    customer = get_customer_by_id(db, customer_id)

    before_state = {
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "upi_vpa": customer.upi_vpa,
    }

    warning_msg = None
    if request.phone and request.phone != customer.phone:
        conflict = (
            db.query(Customer)
            .filter(
                Customer.merchant_id == customer.merchant_id,
                Customer.phone == request.phone,
                Customer.id != customer.id,
                Customer.deleted_at.is_(None),
            )
            .first()
        )
        if conflict:
            warning_msg = (
                f"Another customer profile exists with phone '{request.phone}' "
                f"(Customer ID: {conflict.id})."
            )

    if request.name is not None:
        customer.name = request.name.strip()
    if request.phone is not None:
        customer.phone = request.phone
    if request.email is not None:
        customer.email = str(request.email).lower()
    if request.upi_vpa is not None:
        customer.upi_vpa = request.upi_vpa.strip()

    db.commit()
    db.refresh(customer)

    after_state = {
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "upi_vpa": customer.upi_vpa,
    }

    record_audit(
        db=db,
        action=AuditAction.UPDATE,
        entity_name="customers",
        entity_id=customer.id,
        actor_id=actor.id,
        merchant_id=customer.merchant_id,
        before=before_state,
        after=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return customer, warning_msg
