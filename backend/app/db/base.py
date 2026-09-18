import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


# Import all models to register them on Base.metadata for Alembic migrations
def _register_all_models():
    import app.modules.auth.models  # noqa: F401
    import app.modules.rbac.models  # noqa: F401
    import app.modules.merchants.models  # noqa: F401
    import app.modules.stores.models  # noqa: F401
    import app.modules.customers.models  # noqa: F401
    import app.modules.invoices.models  # noqa: F401
    import app.modules.invoice_items.models  # noqa: F401
    import app.modules.payment_requests.models  # noqa: F401
    import app.modules.upi_qr.models  # noqa: F401
    import app.modules.payment_links.models  # noqa: F401
    import app.modules.splits.models  # noqa: F401
    import app.modules.payments.models  # noqa: F401
    import app.modules.webhooks.models  # noqa: F401
    import app.modules.reconciliation.models  # noqa: F401
    import app.modules.duplicate_detection.models  # noqa: F401
    import app.modules.refunds.models  # noqa: F401
    import app.modules.settlements.models  # noqa: F401
    import app.modules.risk.models  # noqa: F401
    import app.modules.notifications.models  # noqa: F401
    import app.modules.audit.models  # noqa: F401


_register_all_models()
