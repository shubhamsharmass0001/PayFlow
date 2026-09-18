"""add_payment_requests_qr_links_fields

Revision ID: 8f7e6d5c4b3a
Revises: 9a8b7c6d5e4f
Create Date: 2026-09-18 10:24:45.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '8f7e6d5c4b3a'
down_revision: Union[str, None] = '9a8b7c6d5e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add purpose to payment_requests
    op.add_column(
        'payment_requests',
        sa.Column('purpose', sa.String(length=255), nullable=True)
    )

    # 2. Add payment_request_id to upi_qr_codes
    op.add_column(
        'upi_qr_codes',
        sa.Column('payment_request_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        'fk_upi_qr_codes_payment_request_id',
        'upi_qr_codes',
        'payment_requests',
        ['payment_request_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_index(
        'ix_upi_qr_codes_payment_request_id',
        'upi_qr_codes',
        ['payment_request_id'],
        unique=False
    )

    # 3. Add payment_request_id, max_uses, use_count to payment_links
    op.add_column(
        'payment_links',
        sa.Column('payment_request_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        'payment_links',
        sa.Column('max_uses', sa.Integer(), server_default='1', nullable=False)
    )
    op.add_column(
        'payment_links',
        sa.Column('use_count', sa.Integer(), server_default='0', nullable=False)
    )
    op.create_foreign_key(
        'fk_payment_links_payment_request_id',
        'payment_links',
        'payment_requests',
        ['payment_request_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_index(
        'ix_payment_links_payment_request_id',
        'payment_links',
        ['payment_request_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_constraint('fk_payment_links_payment_request_id', 'payment_links', type_='foreignkey')
    op.drop_index('ix_payment_links_payment_request_id', table_name='payment_links')
    op.drop_column('payment_links', 'use_count')
    op.drop_column('payment_links', 'max_uses')
    op.drop_column('payment_links', 'payment_request_id')

    op.drop_constraint('fk_upi_qr_codes_payment_request_id', 'upi_qr_codes', type_='foreignkey')
    op.drop_index('ix_upi_qr_codes_payment_request_id', table_name='upi_qr_codes')
    op.drop_column('upi_qr_codes', 'payment_request_id')

    op.drop_column('payment_requests', 'purpose')
