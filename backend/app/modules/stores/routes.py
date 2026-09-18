import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.dependencies import require_permission
from app.modules.stores.models import Store
from app.modules.stores.schemas import (
    StoreCreateRequest,
    StoreResponse,
    StoreUpdateRequest,
)
from app.modules.stores.service import (
    create_store,
    list_stores,
    update_store,
)
from app.shared.exceptions import EntityNotFoundException, ForbiddenException
from app.modules.rbac.models import Permission, Role, RolePermission, UserRole

router = APIRouter(tags=["Stores"])


@router.get(
    "/merchants/{merchant_id}/stores",
    response_model=List[StoreResponse],
    summary="List all stores for a merchant",
)
def get_stores(
    merchant_id: uuid.UUID,
    user: User = Depends(require_permission("staff:read")),
    db: Session = Depends(get_db),
):
    return list_stores(db=db, merchant_id=merchant_id)


@router.post(
    "/merchants/{merchant_id}/stores",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store location under a merchant",
)
def add_store(
    merchant_id: uuid.UUID,
    payload: StoreCreateRequest,
    user: User = Depends(require_permission("staff:write")),
    db: Session = Depends(get_db),
):
    return create_store(db=db, merchant_id=merchant_id, request=payload, actor=user)


@router.patch(
    "/stores/{id}",
    response_model=StoreResponse,
    summary="Update store details, address, or UPI VPA override",
)
def patch_store(
    id: uuid.UUID,
    payload: StoreUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = db.query(Store).filter(Store.id == id, Store.deleted_at.is_(None)).first()
    if not store:
        raise EntityNotFoundException("Store", id)

    # Validate that current_user has staff:write permission for this store's merchant
    if not current_user.is_superuser:
        has_perm = (
            db.query(UserRole)
            .filter(
                UserRole.user_id == current_user.id,
                UserRole.merchant_id == store.merchant_id,
            )
            .join(Role, Role.id == UserRole.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .filter(Permission.code == "staff:write")
            .first()
        )
        if not has_perm:
            raise ForbiddenException(
                message=f"Access denied: permission 'staff:write' required to update store '{id}'",
                code="FORBIDDEN",
                details={"required_permission": "staff:write", "store_id": str(id)},
            )

    return update_store(db=db, store_id=id, request=payload, actor=current_user)
