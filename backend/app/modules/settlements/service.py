"""Settlements Module Service.

IMPORTANT — MDR / fee notice:
  All fee computations in this module use an illustrative mock MDR rate (default 1.5%)
  and a mock 18% GST-on-MDR rate. These do NOT represent live NPCI fee schedules,
  interchange tariffs, or any real banking rate card. They exist purely for
  prototype simulation and financial reporting demos.

Core responsibility:
  - Group MATCHED reconciliation entries into one Settlement per merchant per date.
  - Compute gross / mdr / tax_on_mdr / net per transaction and in aggregate.
  - Generate a mock UTR reference (format: UTR{YYYYMMDD}-{random}).
  - Expose chart-ready list and detail endpoints.
"""

import secrets
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.logging import logger
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.modules.reconciliation.models import (
    MatchStatus,
    ReconciliationBatch,
    ReconciliationEntry,
    ReconciliationStatus,
)
from app.modules.settlements.models import (
    Settlement,
    SettlementCycle,
    SettlementLineItem,
    SettlementStatus,
)
from app.modules.settlements.schemas import (
    SettlementChartPoint,
    SettlementDetailResponse,
    SettlementListResponse,
    SettlementSummaryResponse,
)
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginationParams, paginate_query

# Illustrative GST rate applied to MDR fee — mock only.
_MOCK_GST_ON_MDR_RATE = Decimal("0.18")


def _mock_utr(settlement_date: date) -> str:
    """Generates a mock UTR reference string.

    Format: UTR{YYYYMMDD}-{8 random hex chars}
    This is NOT a real NEFT/IMPS UTR. It is a simulated reference for the
    prototype settlement screen only.
    """
    return f"UTR{settlement_date.strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"


class SettlementService:
    """Manages the full settlement lifecycle: creation from MATCHED batches,
    retrieval, and chart-ready list responses.
    """

    # MDR defaults pulled from settings (illustrative, same as reconciliation)
    DEFAULT_MDR_RATE = Decimal(str(settings.DEFAULT_RECONCILIATION_MDR_RATE))

    # ------------------------------------------------------------------
    # Create settlement from a MATCHED reconciliation batch
    # ------------------------------------------------------------------

    @classmethod
    def create_from_matched_batch(
        cls,
        db: Session,
        batch: ReconciliationBatch,
        mdr_rate: Optional[Decimal] = None,
    ) -> Optional[Settlement]:
        """Creates a Settlement (with SettlementLineItems) from a MATCHED batch.

        Skips if:
          - Batch status is not MATCHED.
          - A Settlement already exists for this batch (idempotent).
          - No MATCHED entries exist in the batch.

        MDR and tax computations are ILLUSTRATIVE MOCK values only.
        """
        if batch.status != ReconciliationStatus.MATCHED:
            logger.info(
                "settlement_skipped_non_matched_batch",
                batch_id=str(batch.id),
                batch_status=batch.status.value,
            )
            return None

        # Idempotency: skip if settlement already exists for this batch
        existing = (
            db.query(Settlement)
            .filter(Settlement.reconciliation_batch_id == batch.id)
            .first()
        )
        if existing:
            logger.info(
                "settlement_already_exists_for_batch",
                batch_id=str(batch.id),
                settlement_id=str(existing.id),
            )
            return existing

        # Fetch all MATCHED entries in this batch that have a transaction
        matched_entries: List[ReconciliationEntry] = (
            db.query(ReconciliationEntry)
            .filter(
                ReconciliationEntry.batch_id == batch.id,
                ReconciliationEntry.match_status == MatchStatus.MATCHED,
                ReconciliationEntry.transaction_id.isnot(None),
            )
            .all()
        )

        if not matched_entries:
            logger.info(
                "settlement_skipped_no_matched_entries",
                batch_id=str(batch.id),
            )
            return None

        effective_mdr = mdr_rate if mdr_rate is not None else cls.DEFAULT_MDR_RATE
        settlement_date = batch.batch_date
        now = datetime.now(timezone.utc)

        # Compute per-transaction fees and running totals
        total_gross = Decimal("0.00")
        total_mdr = Decimal("0.00")
        total_tax = Decimal("0.00")
        line_item_data = []

        # Fetch transaction amounts in bulk
        tx_ids = [e.transaction_id for e in matched_entries]
        txs = (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.id.in_(tx_ids))
            .all()
        )
        tx_by_id = {t.id: t for t in txs}

        for entry in matched_entries:
            tx = tx_by_id.get(entry.transaction_id)
            if not tx:
                continue

            gross = tx.amount
            # Illustrative MDR fee per transaction
            mdr_fee = (gross * effective_mdr).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # Illustrative 18% GST on MDR fee
            tax = (mdr_fee * _MOCK_GST_ON_MDR_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            net = gross - mdr_fee - tax

            total_gross += gross
            total_mdr += mdr_fee
            total_tax += tax
            line_item_data.append((tx.id, gross, mdr_fee, tax, net))

        if not line_item_data:
            return None

        total_net = total_gross - total_mdr - total_tax

        # Create the parent Settlement row
        settlement = Settlement(
            merchant_id=batch.merchant_id,
            reconciliation_batch_id=batch.id,
            settlement_date=settlement_date,
            settlement_cycle=SettlementCycle.T_PLUS_1,
            transaction_count=len(line_item_data),
            gross_amount=total_gross.quantize(Decimal("0.01")),
            mdr_amount=total_mdr.quantize(Decimal("0.01")),
            tax_on_mdr=total_tax.quantize(Decimal("0.01")),
            deduction_amount=(total_mdr + total_tax).quantize(Decimal("0.01")),
            net_amount=total_net.quantize(Decimal("0.01")),
            status=SettlementStatus.SETTLED,
            utr_reference=_mock_utr(settlement_date),
            bank_account_ref=f"MOCK_ACCT_{str(batch.merchant_id)[:8].upper()}",
            settled_at=now,
        )
        db.add(settlement)
        db.flush()

        # Create child SettlementLineItems
        for (tx_id, gross, mdr_fee, tax, net) in line_item_data:
            line_item = SettlementLineItem(
                settlement_id=settlement.id,
                transaction_id=tx_id,
                amount=gross,
                fee_amount=mdr_fee,
                tax_amount=tax,
                net_amount=net,
            )
            db.add(line_item)

        db.commit()
        db.refresh(settlement)

        logger.info(
            "settlement_created_from_batch",
            settlement_id=str(settlement.id),
            batch_id=str(batch.id),
            merchant_id=str(batch.merchant_id),
            gross=str(total_gross),
            net=str(total_net),
            transaction_count=len(line_item_data),
            utr=settlement.utr_reference,
        )
        return settlement

    # ------------------------------------------------------------------
    # List: chart-ready + paginated
    # ------------------------------------------------------------------

    @classmethod
    def list_merchant_settlements(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        pagination: PaginationParams,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status: Optional[SettlementStatus] = None,
    ) -> SettlementListResponse:
        """Returns paginated settlements plus a pre-aggregated chart series
        and window totals — so the Flutter settlement screen needs only one call.
        """
        query = (
            db.query(Settlement)
            .filter(Settlement.merchant_id == merchant_id)
        )

        if from_date:
            query = query.filter(Settlement.settlement_date >= from_date)
        if to_date:
            query = query.filter(Settlement.settlement_date <= to_date)
        if status:
            query = query.filter(Settlement.status == status)

        query = query.order_by(Settlement.settlement_date.desc())
        items, total = paginate_query(query, pagination)

        # Build paginated item list (summary shape)
        summary_items = [SettlementSummaryResponse.model_validate(s) for s in items]

        # Build chart series: aggregate by date across the PAGE (not just window)
        # Group items by settlement_date for the chart
        series_by_date: dict = {}
        for s in items:
            key = s.settlement_date
            if key not in series_by_date:
                series_by_date[key] = SettlementChartPoint(
                    settlement_date=key,
                    gross_amount=Decimal("0.00"),
                    net_amount=Decimal("0.00"),
                    mdr_amount=Decimal("0.00"),
                    transaction_count=0,
                )
            pt = series_by_date[key]
            series_by_date[key] = SettlementChartPoint(
                settlement_date=key,
                gross_amount=pt.gross_amount + s.gross_amount,
                net_amount=pt.net_amount + s.net_amount,
                mdr_amount=pt.mdr_amount + s.mdr_amount,
                transaction_count=pt.transaction_count + s.transaction_count,
            )
        series = sorted(series_by_date.values(), key=lambda p: p.settlement_date)

        # Window totals (sum across the current page)
        window_gross = sum((s.gross_amount for s in items), Decimal("0.00"))
        window_net = sum((s.net_amount for s in items), Decimal("0.00"))
        window_mdr = sum((s.mdr_amount for s in items), Decimal("0.00"))
        window_txn_count = sum(s.transaction_count for s in items)

        return SettlementListResponse(
            items=summary_items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            series=series,
            window_gross=window_gross,
            window_net=window_net,
            window_mdr=window_mdr,
            window_transaction_count=window_txn_count,
        )

    # ------------------------------------------------------------------
    # Get detail: includes line items
    # ------------------------------------------------------------------

    @staticmethod
    def get_settlement_by_id(
        db: Session,
        settlement_id: uuid.UUID,
    ) -> SettlementDetailResponse:
        """Returns full settlement detail including per-transaction line items."""
        settlement = (
            db.query(Settlement)
            .options(joinedload(Settlement.line_items))
            .filter(Settlement.id == settlement_id)
            .first()
        )
        if not settlement:
            raise EntityNotFoundException("Settlement", settlement_id)
        return SettlementDetailResponse.model_validate(settlement)
