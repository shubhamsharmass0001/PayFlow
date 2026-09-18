"""add_webhook_provider_event_id

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-18 10:47:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "webhook_events_inbound",
        sa.Column("provider_event_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_webhook_events_inbound_provider_event_id"),
        "webhook_events_inbound",
        ["provider_event_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_webhook_events_inbound_provider_event_id"),
        table_name="webhook_events_inbound",
    )
    op.drop_column("webhook_events_inbound", "provider_event_id")
