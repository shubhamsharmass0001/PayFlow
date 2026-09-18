"""add_settlement_fields_and_line_items

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-18 16:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add missing fields to settlements
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("settlements")]

    if "reconciliation_batch_id" not in columns:
        op.add_column(
            "settlements",
            sa.Column("reconciliation_batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_foreign_key(
            "fk_settlements_reconciliation_batch_id",
            "settlements",
            "reconciliation_batches",
            ["reconciliation_batch_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        op.create_index(
            op.f("ix_settlements_reconciliation_batch_id"),
            "settlements",
            ["reconciliation_batch_id"],
            unique=False,
        )

    if "settlement_date" not in columns:
        op.add_column("settlements", sa.Column("settlement_date", sa.Date(), nullable=True))
        op.create_index(op.f("ix_settlements_settlement_date"), "settlements", ["settlement_date"], unique=False)

    if "transaction_count" not in columns:
        op.add_column("settlements", sa.Column("transaction_count", sa.Integer(), server_default="0", nullable=False))

    if "mdr_amount" not in columns:
        op.add_column("settlements", sa.Column("mdr_amount", sa.Numeric(14, 2), server_default="0.00", nullable=False))

    if "tax_on_mdr" not in columns:
        op.add_column("settlements", sa.Column("tax_on_mdr", sa.Numeric(14, 2), server_default="0.00", nullable=False))

    if "utr_reference" not in columns:
        op.add_column("settlements", sa.Column("utr_reference", sa.String(50), nullable=True))
        op.create_index(op.f("ix_settlements_utr_reference"), "settlements", ["utr_reference"], unique=False)

    # Make deduction_amount & bank_account_ref nullable
    op.alter_column("settlements", "deduction_amount", nullable=True, server_default="0.00")
    op.alter_column("settlements", "bank_account_ref", nullable=True)

    # 2. Create settlement_line_items table if not exists
    tables = inspector.get_table_names()
    if "settlement_line_items" not in tables:
        op.create_table(
            "settlement_line_items",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("settlement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("settlements.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment_transactions.id", ondelete="RESTRICT"), nullable=False, index=True),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("fee_amount", sa.Numeric(12, 2), server_default="0.00", nullable=False),
            sa.Column("tax_amount", sa.Numeric(12, 2), server_default="0.00", nullable=False),
            sa.Column("net_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("settlement_line_items")
    op.drop_column("settlements", "utr_reference")
    op.drop_column("settlements", "tax_on_mdr")
    op.drop_column("settlements", "mdr_amount")
    op.drop_column("settlements", "transaction_count")
    op.drop_column("settlements", "settlement_date")
    op.drop_constraint("fk_settlements_reconciliation_batch_id", "settlements", type_="foreignkey")
    op.drop_column("settlements", "reconciliation_batch_id")
