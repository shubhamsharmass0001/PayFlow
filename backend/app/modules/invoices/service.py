import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.customers.models import Customer
from app.modules.invoice_items.models import InvoiceItem
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.invoices.schemas import (
    InvoiceCreateRequest,
    InvoiceFilterParams,
    InvoiceItemCreateRequest,
    InvoiceResponse,
    InvoiceUpdateRequest,
)
from app.modules.merchants.models import Merchant
from app.modules.stores.models import Store
from app.shared.exceptions import BadRequestException, EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams, paginate_query


def generate_invoice_number(db: Session, merchant: Merchant) -> str:
    """Generates a readable, sequential, collision-safe invoice number per merchant.

    Format: INV-{merchant_short_code}-{year}-{sequence:05d}
    Concurrency: Acquired via pessimistic FOR UPDATE lock on the merchant record.
    """
    # 1. Lock merchant row for update
    db.query(Merchant).filter(Merchant.id == merchant.id).with_for_update().one()

    # 2. Extract clean short code (up to 6 alphanumeric characters)
    raw_code = re.sub(r"[^A-Z0-9]", "", (merchant.business_name or "MERCHANT").upper())
    short_code = raw_code[:6] if raw_code else str(merchant.id.hex[:6]).upper()

    year = datetime.now(timezone.utc).year
    prefix = f"INV-{short_code}-{year}-"

    # 3. Find highest existing sequence for this prefix
    last_inv = (
        db.query(Invoice.invoice_number)
        .filter(
            Invoice.merchant_id == merchant.id,
            Invoice.invoice_number.like(f"{prefix}%"),
        )
        .order_by(Invoice.invoice_number.desc())
        .first()
    )

    if last_inv and last_inv[0]:
        try:
            seq_part = last_inv[0].split("-")[-1]
            next_seq = int(seq_part) + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1

    return f"{prefix}{next_seq:05d}"


def recompute_invoice_totals(invoice: Invoice) -> None:
    """Calculates subtotal, discount_total, tax_total, and total_amount from invoice items.

    Financial Rules:
      - Never trusts client totals.
      - Taxable base = quantity * unit_price - discount_amount
      - Tax = taxable base * (tax_rate / 100)
      - Line total = taxable base + tax
    """
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")
    tax_total = Decimal("0.00")

    for item in invoice.items:
        if item.deleted_at is not None:
            continue

        qty = Decimal(str(item.quantity))
        price = Decimal(str(item.unit_price))
        disc = Decimal(str(item.discount_amount or "0.00"))
        tax_rate = Decimal(str(item.tax_rate or "0.00"))

        base = (qty * price).quantize(Decimal("0.01"))
        item_disc = min(base, disc).quantize(Decimal("0.01"))
        taxable = base - item_disc
        tax = (taxable * tax_rate / Decimal("100.00")).quantize(Decimal("0.01"))
        line_total = taxable + tax

        item.line_total = line_total
        subtotal += base
        discount_total += item_disc
        tax_total += tax

    invoice.subtotal = subtotal
    invoice.discount_total = discount_total
    invoice.tax_total = tax_total
    invoice.total_amount = max(Decimal("0.00"), subtotal - discount_total + tax_total)


def get_invoice_by_id(db: Session, invoice_id: uuid.UUID) -> Invoice:
    """Retrieves an active invoice by ID."""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.deleted_at.is_(None))
        .first()
    )
    if not invoice:
        raise EntityNotFoundException("Invoice", invoice_id)
    return invoice


def create_invoice(
    db: Session,
    merchant_id: uuid.UUID,
    request: InvoiceCreateRequest,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Invoice:
    """Creates a new draft invoice with collision-safe numbering and server-computed totals."""
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None))
        .first()
    )
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    # Validate customer if supplied
    if request.customer_id:
        customer = (
            db.query(Customer)
            .filter(
                Customer.id == request.customer_id,
                Customer.merchant_id == merchant_id,
                Customer.deleted_at.is_(None),
            )
            .first()
        )
        if not customer:
            raise BadRequestException(
                message=f"Customer '{request.customer_id}' not found for this merchant.",
                code="CUSTOMER_NOT_FOUND",
            )

    # Validate store if supplied
    if request.store_id:
        store = (
            db.query(Store)
            .filter(
                Store.id == request.store_id,
                Store.merchant_id == merchant_id,
                Store.deleted_at.is_(None),
            )
            .first()
        )
        if not store:
            raise BadRequestException(
                message=f"Store '{request.store_id}' not found for this merchant.",
                code="STORE_NOT_FOUND",
            )

    invoice_num = generate_invoice_number(db, merchant)

    invoice = Invoice(
        merchant_id=merchant_id,
        store_id=request.store_id,
        customer_id=request.customer_id,
        invoice_number=invoice_num,
        currency=request.currency.upper(),
        status=InvoiceStatus.DRAFT,
        allow_partial_payment=request.allow_partial_payment,
        allow_split_payment=request.allow_split_payment,
        due_date=request.due_date,
        notes=request.notes,
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        paid_amount=Decimal("0.00"),
    )
    db.add(invoice)
    db.flush()

    if request.items:
        for item_in in request.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                name=item_in.name.strip(),
                description=item_in.description,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price,
                tax_rate=item_in.tax_rate,
                discount_amount=item_in.discount_amount,
                line_total=Decimal("0.00"),
            )
            invoice.items.append(item)

    recompute_invoice_totals(invoice)
    db.commit()
    db.refresh(invoice)

    # Record audit log
    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="invoices",
        entity_id=invoice.id,
        actor_id=actor.id,
        merchant_id=merchant_id,
        before=None,
        after={
            "invoice_number": invoice.invoice_number,
            "status": invoice.status.value,
            "total_amount": str(invoice.total_amount),
            "subtotal": str(invoice.subtotal),
            "tax_total": str(invoice.tax_total),
            "discount_total": str(invoice.discount_total),
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return invoice


def add_invoice_item(
    db: Session,
    invoice_id: uuid.UUID,
    request: InvoiceItemCreateRequest,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Invoice:
    """Appends an item to a DRAFT invoice and recomputes all financial totals."""
    invoice = get_invoice_by_id(db, invoice_id)

    if invoice.status != InvoiceStatus.DRAFT:
        raise BadRequestException(
            message=f"Cannot add items to invoice in status '{invoice.status.value}'. Only DRAFT invoices can be edited.",
            code="INVOICE_NOT_EDITABLE",
        )

    item = InvoiceItem(
        invoice_id=invoice.id,
        name=request.name.strip(),
        description=request.description,
        quantity=request.quantity,
        unit_price=request.unit_price,
        tax_rate=request.tax_rate,
        discount_amount=request.discount_amount,
        line_total=Decimal("0.00"),
    )
    db.add(item)
    invoice.items.append(item)
    recompute_invoice_totals(invoice)

    db.commit()
    db.refresh(invoice)

    # Audit log
    record_audit(
        db=db,
        action=AuditAction.UPDATE,
        entity_name="invoices",
        entity_id=invoice.id,
        actor_id=actor.id,
        merchant_id=invoice.merchant_id,
        before=None,
        after={
            "added_item_name": item.name,
            "item_line_total": str(item.line_total),
            "new_total_amount": str(invoice.total_amount),
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return invoice


def remove_invoice_item(
    db: Session,
    item_id: uuid.UUID,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Invoice:
    """Removes an item from a DRAFT invoice and recomputes all financial totals."""
    item = (
        db.query(InvoiceItem)
        .filter(InvoiceItem.id == item_id, InvoiceItem.deleted_at.is_(None))
        .first()
    )
    if not item:
        raise EntityNotFoundException("InvoiceItem", item_id)

    invoice = get_invoice_by_id(db, item.invoice_id)

    if invoice.status != InvoiceStatus.DRAFT:
        raise BadRequestException(
            message=f"Cannot remove items from invoice in status '{invoice.status.value}'. Only DRAFT invoices can be edited.",
            code="INVOICE_NOT_EDITABLE",
        )

    db.delete(item)
    db.flush()

    recompute_invoice_totals(invoice)
    db.commit()
    db.refresh(invoice)

    # Audit log
    record_audit(
        db=db,
        action=AuditAction.UPDATE,
        entity_name="invoices",
        entity_id=invoice.id,
        actor_id=actor.id,
        merchant_id=invoice.merchant_id,
        before={"deleted_item_id": str(item_id)},
        after={"new_total_amount": str(invoice.total_amount)},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return invoice


def update_invoice(
    db: Session,
    invoice_id: uuid.UUID,
    request: InvoiceUpdateRequest,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Invoice:
    """Updates invoice metadata and enforces controlled status transitions."""
    invoice = get_invoice_by_id(db, invoice_id)

    before_state = {
        "status": invoice.status.value,
        "notes": invoice.notes,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "allow_partial_payment": invoice.allow_partial_payment,
        "allow_split_payment": invoice.allow_split_payment,
    }

    if request.status is not None and request.status != invoice.status:
        # Strictly forbid manual transition into payment/system-derived states
        forbidden_manual_statuses = [
            InvoiceStatus.PARTIALLY_PAID,
            InvoiceStatus.PAID,
            InvoiceStatus.OVERDUE,
            InvoiceStatus.REFUNDED,
        ]
        if request.status in forbidden_manual_statuses:
            raise BadRequestException(
                message=f"Manual transition to status '{request.status.value}' is not permitted. This status is system-derived from payment activity.",
                code="INVALID_STATUS_TRANSITION",
            )

        # Enforce state machine rules: DRAFT -> SENT -> CANCELLED
        valid_transitions = {
            InvoiceStatus.DRAFT: [InvoiceStatus.SENT, InvoiceStatus.CANCELLED],
            InvoiceStatus.SENT: [InvoiceStatus.CANCELLED],
            InvoiceStatus.CANCELLED: [],
        }

        allowed_targets = valid_transitions.get(invoice.status, [])
        if request.status not in allowed_targets:
            raise BadRequestException(
                message=f"Cannot transition invoice status from '{invoice.status.value}' to '{request.status.value}'.",
                code="INVALID_STATUS_TRANSITION",
                details={
                    "current_status": invoice.status.value,
                    "attempted_status": request.status.value,
                    "allowed_transitions": [s.value for s in allowed_targets],
                },
            )

        invoice.status = request.status

    if request.notes is not None:
        invoice.notes = request.notes
    if request.due_date is not None:
        invoice.due_date = request.due_date
    if request.allow_partial_payment is not None:
        invoice.allow_partial_payment = request.allow_partial_payment
    if request.allow_split_payment is not None:
        invoice.allow_split_payment = request.allow_split_payment

    db.commit()
    db.refresh(invoice)

    after_state = {
        "status": invoice.status.value,
        "notes": invoice.notes,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "allow_partial_payment": invoice.allow_partial_payment,
        "allow_split_payment": invoice.allow_split_payment,
    }

    record_audit(
        db=db,
        action=AuditAction.STATUS_CHANGE if request.status else AuditAction.UPDATE,
        entity_name="invoices",
        entity_id=invoice.id,
        actor_id=actor.id,
        merchant_id=invoice.merchant_id,
        before=before_state,
        after=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return invoice


def list_invoices(
    db: Session,
    merchant_id: uuid.UUID,
    filters: InvoiceFilterParams,
    pagination: PaginationParams,
) -> PaginatedResponse[InvoiceResponse]:
    """Lists merchant invoices with status filtering, date range, search, and pagination."""
    query = (
        db.query(Invoice)
        .outerjoin(Customer, Customer.id == Invoice.customer_id)
        .filter(
            Invoice.merchant_id == merchant_id,
            Invoice.deleted_at.is_(None),
        )
    )

    # Status filter
    if filters.status:
        query = query.filter(Invoice.status == filters.status)

    # Date range filter
    if filters.from_date:
        query = query.filter(Invoice.created_at >= filters.from_date)
    if filters.to_date:
        query = query.filter(Invoice.created_at <= filters.to_date)

    # Search filter (invoice_number or customer name)
    if filters.search and filters.search.strip():
        term = f"%{filters.search.strip()}%"
        query = query.filter(
            or_(
                Invoice.invoice_number.ilike(term),
                Customer.name.ilike(term),
            )
        )

    # Sorting
    sort_column_map = {
        "created_at": Invoice.created_at,
        "total_amount": Invoice.total_amount,
        "invoice_number": Invoice.invoice_number,
        "due_date": Invoice.due_date,
    }
    sort_col = sort_column_map.get(filters.sort_by, Invoice.created_at)
    if filters.sort_order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    items, total = paginate_query(query, pagination)
    response_items = [InvoiceResponse.model_validate(inv) for inv in items]

    return PaginatedResponse.create(
        items=response_items,
        total=total,
        params=pagination,
    )


def mark_invoice_overdue(db: Session, invoice_id: uuid.UUID) -> Invoice:
    """Transitions an unpaid invoice to OVERDUE and dispatches an alert notification."""
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED):
        return invoice

    invoice.status = InvoiceStatus.OVERDUE
    db.commit()
    db.refresh(invoice)

    # Dispatch Notification on invoice OVERDUE
    try:
        from app.modules.notifications.service import NotificationService
        from app.modules.notifications.models import NotificationChannel
        NotificationService.send_notification(
            merchant_id=invoice.merchant_id,
            channel=NotificationChannel.PUSH,
            template="invoice_overdue",
            payload={
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "amount": str(invoice.total_amount),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else "N/A",
            },
        )
    except Exception:
        pass

    return invoice


def check_overdue_invoices(db: Session, merchant_id: Optional[uuid.UUID] = None) -> list[Invoice]:
    """Sweeps for unpaid invoices whose due_date has elapsed and transitions them to OVERDUE."""
    from datetime import date
    today = date.today()

    query = db.query(Invoice).filter(
        Invoice.status.in_([InvoiceStatus.DRAFT, InvoiceStatus.SENT, InvoiceStatus.PARTIALLY_PAID]),
        Invoice.due_date < today,
    )
    if merchant_id:
        query = query.filter(Invoice.merchant_id == merchant_id)

    overdue_invoices = query.all()
    results = []
    for inv in overdue_invoices:
        results.append(mark_invoice_overdue(db, inv.id))

    return results

