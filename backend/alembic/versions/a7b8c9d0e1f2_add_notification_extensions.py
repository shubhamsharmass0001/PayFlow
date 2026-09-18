"""add_notification_extensions

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-18 16:39:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("notifications")]

    # Add PUSH to notification_channel enum if not present
    try:
        op.execute("ALTER TYPE notification_channel ADD VALUE IF NOT EXISTS 'PUSH'")
    except Exception:
        pass

    if "user_id" not in columns:
        op.add_column(
            "notifications",
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_foreign_key(
            "fk_notifications_user_id",
            "notifications",
            "users",
            ["user_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index(
            op.f("ix_notifications_user_id"),
            "notifications",
            ["user_id"],
            unique=False,
        )

    if "template" not in columns:
        op.add_column("notifications", sa.Column("template", sa.String(100), nullable=True))

    if "payload" not in columns:
        op.add_column("notifications", sa.Column("payload", postgresql.JSONB(), nullable=True))

    if "is_read" not in columns:
        op.add_column(
            "notifications",
            sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        )
        op.create_index(op.f("ix_notifications_is_read"), "notifications", ["is_read"], unique=False)

    if "read_at" not in columns:
        op.add_column("notifications", sa.Column("read_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("notifications", "read_at")
    op.drop_column("notifications", "is_read")
    op.drop_column("notifications", "payload")
    op.drop_column("notifications", "template")
    op.drop_constraint("fk_notifications_user_id", "notifications", type_="foreignkey")
    op.drop_column("notifications", "user_id")
