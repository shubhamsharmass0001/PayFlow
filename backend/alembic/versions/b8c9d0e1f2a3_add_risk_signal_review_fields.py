"""add_risk_signal_review_fields

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-09-18 17:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("risk_signals")]

    if "is_reviewed" not in columns:
        op.add_column(
            "risk_signals",
            sa.Column("is_reviewed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        )
        op.create_index(
            op.f("ix_risk_signals_is_reviewed"),
            "risk_signals",
            ["is_reviewed"],
            unique=False,
        )

    if "reviewed_by" not in columns:
        op.add_column(
            "risk_signals",
            sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_foreign_key(
            "fk_risk_signals_reviewed_by",
            "risk_signals",
            "users",
            ["reviewed_by"],
            ["id"],
            ondelete="SET NULL",
        )

    if "reviewed_at" not in columns:
        op.add_column(
            "risk_signals",
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        )

    if "resolution_note" not in columns:
        op.add_column(
            "risk_signals",
            sa.Column("resolution_note", sa.String(length=500), nullable=True),
        )

    # Composite index for filtering
    indexes = [idx["name"] for idx in inspector.get_indexes("risk_signals")]
    if "ix_risk_signals_merchant_reviewed" not in indexes:
        op.create_index(
            "ix_risk_signals_merchant_reviewed",
            "risk_signals",
            ["merchant_id", "is_reviewed", "created_at"],
            unique=False,
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("risk_signals")]

    if "ix_risk_signals_merchant_reviewed" in [idx["name"] for idx in inspector.get_indexes("risk_signals")]:
        op.drop_index("ix_risk_signals_merchant_reviewed", table_name="risk_signals")

    if "resolution_note" in columns:
        op.drop_column("risk_signals", "resolution_note")

    if "reviewed_at" in columns:
        op.drop_column("risk_signals", "reviewed_at")

    if "reviewed_by" in columns:
        op.drop_constraint("fk_risk_signals_reviewed_by", "risk_signals", type_="foreignkey")
        op.drop_column("risk_signals", "reviewed_by")

    if "is_reviewed" in columns:
        op.drop_index(op.f("ix_risk_signals_is_reviewed"), table_name="risk_signals")
        op.drop_column("risk_signals", "is_reviewed")
