"""add_transaction_status_enum_values

Revision ID: a1b2c3d4e5f6
Revises: 8f7e6d5c4b3a
Create Date: 2026-09-18 10:36:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "8f7e6d5c4b3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE transaction_status ADD VALUE IF NOT EXISTS 'CREATED'")
    op.execute("ALTER TYPE transaction_status ADD VALUE IF NOT EXISTS 'DUPLICATE'")
    op.execute("ALTER TYPE transaction_status ADD VALUE IF NOT EXISTS 'REFUND_INITIATED'")
    op.execute("ALTER TYPE transaction_status ADD VALUE IF NOT EXISTS 'REFUND_PENDING'")
    op.execute("ALTER TYPE transaction_status ADD VALUE IF NOT EXISTS 'REFUND_FAILED'")


def downgrade() -> None:
    pass
