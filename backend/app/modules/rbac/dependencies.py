import uuid
from typing import Callable, Optional
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.rbac.models import Permission, Role, RolePermission, UserRole
from app.shared.exceptions import BadRequestException, ForbiddenException


def require_permission(permission_code: str) -> Callable:
    """FastAPI dependency factory enforcing merchant-scoped RBAC authorization.

    Resolves `merchant_id` from:
      1. Path parameters (e.g. `/merchants/{merchant_id}/...`)
      2. Query parameters (e.g. `?merchant_id=...`)
      3. Header (`X-Merchant-ID: ...`)

    Raises:
      - 400 BAD_REQUEST if merchant_id is missing or malformed.
      - 403 FORBIDDEN with standard error envelope if user lacks the permission for the merchant.

    Returns:
      The authenticated User upon authorization success.
    """

    async def _permission_dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        # Superusers bypass merchant-scoped permission checks
        if current_user.is_superuser:
            return current_user

        # Extract merchant_id from path params, query params, or custom header
        raw_merchant_id = (
            request.path_params.get("merchant_id")
            or request.path_params.get("id")
            or request.query_params.get("merchant_id")
            or request.headers.get("X-Merchant-ID")
        )

        if not raw_merchant_id:
            raise BadRequestException(
                message="Operation requires a target merchant_id specified in the path, query parameter, or X-Merchant-ID header",
                code="RBAC_MISSING_MERCHANT_ID",
            )

        try:
            merchant_uuid = (
                raw_merchant_id
                if isinstance(raw_merchant_id, uuid.UUID)
                else uuid.UUID(str(raw_merchant_id))
            )
        except (ValueError, TypeError):
            raise BadRequestException(
                message=f"Invalid merchant_id format: '{raw_merchant_id}' is not a valid UUID",
                code="RBAC_INVALID_MERCHANT_ID",
                details={"provided_merchant_id": str(raw_merchant_id)},
            )

        # Set on request state for structured logging middleware
        request.state.merchant_id = merchant_uuid
        request.state.user_id = current_user.id

        verify_merchant_permission(
            db=db,
            user=current_user,
            merchant_id=merchant_uuid,
            permission_code=permission_code,
        )

        return current_user

    return _permission_dependency


def verify_merchant_permission(
    db: Session,
    user: User,
    merchant_id: uuid.UUID,
    permission_code: str,
) -> None:
    """Verifies that user has permission_code for merchant_id, raising 403 Forbidden if not."""
    if user.is_superuser:
        return

    has_permission = (
        db.query(UserRole)
        .filter(
            UserRole.user_id == user.id,
            UserRole.merchant_id == merchant_id,
        )
        .join(Role, Role.id == UserRole.role_id)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(Permission.code == permission_code)
        .first()
    )

    if not has_permission:
        raise ForbiddenException(
            message=f"Access denied: permission '{permission_code}' is required for merchant '{merchant_id}'",
            code="FORBIDDEN",
            details={
                "required_permission": permission_code,
                "merchant_id": str(merchant_id),
            },
        )


def verify_auditor_or_owner_access(
    db: Session,
    user: User,
    merchant_id: uuid.UUID,
) -> None:
    """Verifies that user has Owner or Auditor role for the given merchant."""
    if user.is_superuser:
        return

    user_role = (
        db.query(UserRole)
        .filter(
            UserRole.user_id == user.id,
            UserRole.merchant_id == merchant_id,
        )
        .join(Role, Role.id == UserRole.role_id)
        .filter(Role.name.in_(["Owner", "Auditor"]))
        .first()
    )

    if not user_role:
        raise ForbiddenException(
            message=f"Access denied: Audit log access is restricted to Owner and Auditor roles for merchant '{merchant_id}'",
            code="FORBIDDEN",
            details={
                "allowed_roles": ["Owner", "Auditor"],
                "merchant_id": str(merchant_id),
            },
        )

