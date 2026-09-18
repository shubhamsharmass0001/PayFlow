import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.modules.audit.models import AuditAction, AuditLog
from app.modules.audit.schemas import (
    AuditChangeDiff,
    AuditLogDetailResponse,
    AuditLogListItemResponse,
)
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginationParams, paginate_query


def record_audit(
    db: Session,
    action: AuditAction,
    entity_name: str,
    entity_id: uuid.UUID,
    actor_id: Optional[uuid.UUID] = None,
    merchant_id: Optional[uuid.UUID] = None,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Records an immutable audit trail entry for domain entity mutations.

    Args:
        db: Active SQLAlchemy session.
        action: Type of action executed (CREATE, UPDATE, DELETE, etc.).
        entity_name: Table/class name of the entity (e.g. 'merchants', 'stores').
        entity_id: Primary key of the modified entity.
        actor_id: Optional UUID of the user initiating the action.
        merchant_id: Optional UUID of the affected merchant.
        before: State before mutation (serialized dict).
        after: State after mutation (serialized dict).
        ip_address: Optional client IP address.
        user_agent: Optional client browser / device string.

    Returns:
        The newly created AuditLog instance.
    """
    changes = {}
    if before is not None:
        changes["before"] = before
    if after is not None:
        changes["after"] = after

    audit_entry = AuditLog(
        merchant_id=merchant_id,
        user_id=actor_id,
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        changes=changes if changes else None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_entry)
    db.flush()
    return audit_entry


def compute_audit_diff(
    changes: Optional[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Dict[str, AuditChangeDiff]]:
    """Calculates structured attribute-level diff from stored before/after changes.

    Returns:
        Tuple of (before_dict, after_dict, diff_dict) where diff_dict maps each
        attribute to an AuditChangeDiff(before, after, status).
    """
    if not changes or not isinstance(changes, dict):
        return None, None, {}

    # Extract before and after blocks if present
    if "before" in changes or "after" in changes:
        raw_before = changes.get("before")
        raw_after = changes.get("after")
    else:
        raw_before = None
        raw_after = changes

    before_dict = raw_before if isinstance(raw_before, dict) else {}
    after_dict = raw_after if isinstance(raw_after, dict) else {}

    all_keys = sorted(list(set(before_dict.keys()) | set(after_dict.keys())))
    diff: Dict[str, AuditChangeDiff] = {}

    for key in all_keys:
        val_before = before_dict.get(key)
        val_after = after_dict.get(key)

        if key not in before_dict:
            status = "ADDED"
        elif key not in after_dict:
            status = "REMOVED"
        elif val_before != val_after:
            status = "MODIFIED"
        else:
            status = "UNCHANGED"

        diff[key] = AuditChangeDiff(
            before=val_before,
            after=val_after,
            status=status,
        )

    clean_before = raw_before if isinstance(raw_before, dict) else None
    clean_after = raw_after if isinstance(raw_after, dict) else None

    return clean_before, clean_after, diff


class AuditService:
    """Service providing query and formatting methods for platform audit trails."""

    @classmethod
    def list_merchant_audit_logs(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        actor_user_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        action: Optional[AuditAction] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        pagination_params: Optional[PaginationParams] = None,
    ) -> Tuple[List[AuditLogListItemResponse], int]:
        """Queries and filters merchant audit logs with pagination."""
        params = pagination_params or PaginationParams(page=1, page_size=20)

        query = (
            db.query(AuditLog)
            .options(joinedload(AuditLog.user))
            .filter(AuditLog.merchant_id == merchant_id)
        )

        if actor_user_id:
            query = query.filter(AuditLog.user_id == actor_user_id)

        if entity_type:
            # Case-insensitive match on entity_name
            query = query.filter(func.lower(AuditLog.entity_name) == entity_type.strip().lower())

        if action:
            query = query.filter(AuditLog.action == action)

        if from_date:
            query = query.filter(AuditLog.created_at >= from_date)

        if to_date:
            query = query.filter(AuditLog.created_at <= to_date)

        query = query.order_by(AuditLog.created_at.desc())

        items, total = paginate_query(query, params)

        responses = [
            AuditLogListItemResponse(
                id=item.id,
                merchant_id=item.merchant_id,
                actor_user_id=item.user_id,
                user_id=item.user_id,
                actor_email=item.user.email if item.user else None,
                entity_type=item.entity_name,
                entity_name=item.entity_name,
                entity_id=item.entity_id,
                action=item.action,
                ip_address=item.ip_address,
                user_agent=item.user_agent,
                created_at=item.created_at,
            )
            for item in items
        ]

        return responses, total

    @classmethod
    def get_audit_log_detail(
        cls,
        db: Session,
        audit_id: uuid.UUID,
    ) -> AuditLogDetailResponse:
        """Retrieves single audit log with formatted before/after JSON diff."""
        log = (
            db.query(AuditLog)
            .options(joinedload(AuditLog.user))
            .filter(AuditLog.id == audit_id)
            .first()
        )
        if not log:
            raise EntityNotFoundException("AuditLog", audit_id)

        before, after, diff = compute_audit_diff(log.changes)

        return AuditLogDetailResponse(
            id=log.id,
            merchant_id=log.merchant_id,
            actor_user_id=log.user_id,
            user_id=log.user_id,
            actor_email=log.user.email if log.user else None,
            entity_type=log.entity_name,
            entity_name=log.entity_name,
            entity_id=log.entity_id,
            action=log.action,
            before=before,
            after=after,
            diff=diff,
            changes=log.changes,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
        )
