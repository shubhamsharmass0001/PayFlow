"""add_reconciliation_match_status_and_period

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-18 10:59:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add period, mdr_rate, and discrepancy_count to reconciliation_batches
    op.add_column(
        "reconciliation_batches",
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "reconciliation_batches",
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "reconciliation_batches",
        sa.Column("mdr_rate", sa.Numeric(5, 4), server_default="0.0150", nullable=False),
    )
    op.add_column(
        "reconciliation_batches",
        sa.Column("discrepancy_count", sa.Integer(), server_default="0", nullable=False),
    )

    # 2. Create MatchStatus enum type
    match_status_enum = postgresql.ENUM(
        "MATCHED",
        "UNMATCHED",
        "MANUAL_REVIEW",
        name="reconciliation_match_status",
    )
    match_status_enum.create(op.get_bind(), checkfirst=True)

    # 3. Add match_status column to reconciliation_entries
    op.add_column(
        "reconciliation_entries",
        sa.Column(
            "match_status",
            sa.Enum("MATCHED", "UNMATCHED", "MANUAL_REVIEW", name="reconciliation_match_status"),
            server_default="MATCHED",
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_reconciliation_entries_match_status"),
        "reconciliation_entries",
        ["match_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reconciliation_entries_match_status"), table_name="reconciliation_entries")
    op.drop_column("reconciliation_entries", "match_status")
    sa.Enum(name="reconciliation_match_status").drop(op.get_bind(), checkfirst=True)

    op.drop_column("reconciliation_batches", "discrepancy_count")
    op.drop_column("reconciliation_batches", "mdr_rate")
    op.drop_column("reconciliation_batches", "period_end")
    op.drop_column("reconciliation_batches", "period_start")
