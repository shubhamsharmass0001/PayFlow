"""Notifications Module Routes.

Provides endpoints for the mobile notification center (Flutter Phase 23/24):
  - GET   /merchants/{id}/notifications (paginated list with read-status filter)
  - PATCH /notifications/{id}/read       (mark single notification as read)
"""

from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import MarkReadResponse, NotificationResponse
from app.modules.notifications.service import NotificationService
from app.modules.rbac.dependencies import require_permission, verify_merchant_permission
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(tags=["Notifications"])


@router.get(
    "/merchants/{id}/notifications",
    response_model=PaginatedResponse[NotificationResponse],
    summary="List merchant notifications (paginated)",
    description=(
        "Returns paginated notifications for the specified merchant. "
        "Filterable by is_read boolean for the mobile notification center."
    ),
)
def list_merchant_notifications(
    id: uuid.UUID,
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("payments:read")),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return NotificationService.list_merchant_notifications(
        db=db,
        merchant_id=id,
        pagination=pagination,
        is_read=is_read,
    )


@router.patch(
    "/notifications/{id}/read",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark a notification as read",
    description="Marks the notification as read with a timestamp for the mobile notification center.",
)
def mark_notification_read(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(Notification.id == id).first()
    if not notification:
        raise EntityNotFoundException("Notification", id)

    if notification.merchant_id:
        verify_merchant_permission(
            db=db,
            user=current_user,
            merchant_id=notification.merchant_id,
            permission_code="payments:read",
        )

    return NotificationService.mark_as_read(db=db, notification_id=id)
