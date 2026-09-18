import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.merchants.models import Merchant
from app.modules.stores.models import Store
from app.modules.stores.schemas import (
    StoreCreateRequest,
    StoreResponse,
    StoreUpdateRequest,
)
from app.shared.exceptions import (
    ConflictException,
    EntityNotFoundException,
)


def create_store(
    db: Session,
    merchant_id: uuid.UUID,
    request: StoreCreateRequest,
    actor: User,
) -> StoreResponse:
    """Creates a new store location with optional custom UPI VPA override."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None)).first()
    if not merchant:
        raise EntityNotFoundException("Merchant", merchant_id)

    existing_code = (
        db.query(Store)
        .filter(
            Store.merchant_id == merchant_id,
            Store.code == request.code,
            Store.deleted_at.is_(None),
        )
        .first()
    )
    if existing_code:
        raise ConflictException(
            message=f"Store code '{request.code}' already exists for this merchant.",
            code="STORE_CODE_EXISTS",
            details={"code": request.code},
        )

    store = Store(
        merchant_id=merchant_id,
        name=request.name,
        code=request.code,
        address_line1=request.address_line1,
        city=request.city,
        state=request.state,
        postal_code=request.postal_code,
        upi_vpa=request.upi_vpa,
        is_active=True,
    )
    db.add(store)
    db.flush()

    record_audit(
        db=db,
        action=AuditAction.CREATE,
        entity_name="stores",
        entity_id=store.id,
        actor_id=actor.id,
        merchant_id=merchant_id,
        after={
            "id": str(store.id),
            "name": store.name,
            "code": store.code,
            "upi_vpa": store.upi_vpa,
        },
    )

    db.commit()
    db.refresh(store)
    return StoreResponse.model_validate(store)


def list_stores(db: Session, merchant_id: uuid.UUID) -> List[StoreResponse]:
    """Lists all active stores for a merchant."""
    stores = (
        db.query(Store)
        .filter(
            Store.merchant_id == merchant_id,
            Store.deleted_at.is_(None),
        )
        .order_by(Store.created_at.asc())
        .all()
    )
    return [StoreResponse.model_validate(s) for s in stores]


def update_store(
    db: Session,
    store_id: uuid.UUID,
    request: StoreUpdateRequest,
    actor: User,
) -> StoreResponse:
    """Updates an existing store, allowing overrides for UPI VPA and address."""
    store = db.query(Store).filter(Store.id == store_id, Store.deleted_at.is_(None)).first()
    if not store:
        raise EntityNotFoundException("Store", store_id)

    before_state = {
        "name": store.name,
        "address_line1": store.address_line1,
        "city": store.city,
        "state": store.state,
        "postal_code": store.postal_code,
        "upi_vpa": store.upi_vpa,
        "is_active": store.is_active,
    }

    if request.name is not None:
        store.name = request.name
    if request.address_line1 is not None:
        store.address_line1 = request.address_line1
    if request.city is not None:
        store.city = request.city
    if request.state is not None:
        store.state = request.state
    if request.postal_code is not None:
        store.postal_code = request.postal_code
    if request.upi_vpa is not None:
        store.upi_vpa = request.upi_vpa
    if request.is_active is not None:
        store.is_active = request.is_active

    db.flush()

    after_state = {
        "name": store.name,
        "address_line1": store.address_line1,
        "city": store.city,
        "state": store.state,
        "postal_code": store.postal_code,
        "upi_vpa": store.upi_vpa,
        "is_active": store.is_active,
    }

    record_audit(
        db=db,
        action=AuditAction.UPDATE,
        entity_name="stores",
        entity_id=store.id,
        actor_id=actor.id,
        merchant_id=store.merchant_id,
        before=before_state,
        after=after_state,
    )

    db.commit()
    db.refresh(store)
    return StoreResponse.model_validate(store)
