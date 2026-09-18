"""add_duplicate_match_and_resolution_reason

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-18 11:07:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "duplicate_transaction_flags",
        sa.Column("match_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "duplicate_transaction_flags",
        sa.Column("resolution_reason", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("duplicate_transaction_flags", "resolution_reason")
    op.drop_column("duplicate_transaction_flags", "match_reason")
