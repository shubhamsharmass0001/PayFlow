"""add_invoice_totals_and_sent_status

Revision ID: 9a8b7c6d5e4f
Revises: 71ff79d17572
Create Date: 2026-09-18 10:20:15.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '9a8b7c6d5e4f'
down_revision: Union[str, None] = '71ff79d17572'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add 'SENT' to invoice_status enum if not present
    op.execute("ALTER TYPE invoice_status ADD VALUE IF NOT EXISTS 'SENT'")

    # 2. Add subtotal, tax_total, discount_total to invoices table
    op.add_column(
        'invoices',
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), server_default='0.00', nullable=False)
    )
    op.add_column(
        'invoices',
        sa.Column('tax_total', sa.Numeric(precision=12, scale=2), server_default='0.00', nullable=False)
    )
    op.add_column(
        'invoices',
        sa.Column('discount_total', sa.Numeric(precision=12, scale=2), server_default='0.00', nullable=False)
    )

    # 3. Add discount_amount to invoice_items table
    op.add_column(
        'invoice_items',
        sa.Column('discount_amount', sa.Numeric(precision=12, scale=2), server_default='0.00', nullable=False)
    )


def downgrade() -> None:
    op.drop_column('invoice_items', 'discount_amount')
    op.drop_column('invoices', 'discount_total')
    op.drop_column('invoices', 'tax_total')
    op.drop_column('invoices', 'subtotal')
