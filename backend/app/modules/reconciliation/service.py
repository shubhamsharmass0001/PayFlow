"""Reconciliation Module Service.

===========================================================================================
RECONCILIATION & MDR NOTICE:
===========================================================================================
The MDR (Merchant Discount Rate) calculations performed here (e.g. default 1.5% / 0.015)
are for illustrative and mock simulation purposes within this prototype. They do NOT reflect
or connect to live banking schedules, interchange tariffs, or NPCI fee structures.
===========================================================================================
"""
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.logging import logger
from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.merchants.models import Merchant
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.modules.reconciliation.models import (
    MatchStatus,
    ReconciliationBatch,
    ReconciliationEntry,
    ReconciliationEntryStatus,
    ReconciliationStatus,
)
from app.modules.reconciliation.schemas import ReconciliationRunRequest
from app.modules.settlements.models import SettlementLineItem
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginatedResponse, PaginationParams, paginate_query


class ReconciliationService:
    """Service implementing ledger reconciliation, settlement cross-referencing,

    tolerance variance checks, and audit logging.
    """

    @classmethod
    def run_reconciliation(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        request: Optional[ReconciliationRunRequest] = None,
        actor_id: Optional[uuid.UUID] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> ReconciliationBatch:
        """Executes a reconciliation run for the given merchant over the specified window.

        Compares all captured SUCCESS/SETTLED transactions against expected settlement
        amounts (amount minus illustrative MDR rate) and cross-checks actual records
        in settlement_line_items.
        """
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            raise EntityNotFoundException("Merchant", merchant_id)

        now = datetime.now(timezone.utc)

        # Resolve parameters
        req_start = request.period_start if request else None
        req_end = request.period_end if request else None
        p_start = period_start or req_start or (now - timedelta(hours=24))
        p_end = period_end or req_end or now

        mdr_rate_float = (
            float(request.mdr_rate)
            if request and request.mdr_rate is not None
            else settings.DEFAULT_RECONCILIATION_MDR_RATE
        )
        mdr_rate = Decimal(str(mdr_rate_float))

        tolerance_float = (
            float(request.tolerance)
            if request and request.tolerance is not None
            else settings.RECONCILIATION_TOLERANCE
        )
        tolerance = Decimal(str(tolerance_float))

        grace_hours = (
            request.grace_period_hours
            if request and request.grace_period_hours is not None
            else settings.RECONCILIATION_GRACE_PERIOD_HOURS
        )
        grace_cutoff = now - timedelta(hours=grace_hours)

        # 1. Fetch eligible transactions (SUCCESS or SETTLED within the period)
        transactions = (
            db.query(PaymentTransaction)
            .filter(
                PaymentTransaction.merchant_id == merchant_id,
                PaymentTransaction.status.in_([
                    TransactionStatus.SUCCESS,
                    TransactionStatus.COMPLETED if hasattr(TransactionStatus, "COMPLETED") else TransactionStatus.SUCCESS,
                ]),
                PaymentTransaction.created_at >= p_start,
                PaymentTransaction.created_at <= p_end,
            )
            .order_by(PaymentTransaction.created_at.asc())
            .all()
        )

        batch_date = p_end.date()

        # 2. Create the parent ReconciliationBatch
        batch = ReconciliationBatch(
            merchant_id=merchant_id,
            batch_date=batch_date,
            period_start=p_start,
            period_end=p_end,
            mdr_rate=mdr_rate,
            status=ReconciliationStatus.PROCESSING,
            total_records=0,
            matched_records=0,
            mismatched_records=0,
            discrepancy_count=0,
        )
        db.add(batch)
        db.flush()

        # 3. Cross-reference transactions against settlement_line_items
        tx_ids = [tx.id for tx in transactions]
        line_items_by_tx = {}
        if tx_ids:
            line_items = (
                db.query(SettlementLineItem)
                .filter(SettlementLineItem.transaction_id.in_(tx_ids))
                .all()
            )
            for li in line_items:
                line_items_by_tx[li.transaction_id] = li

        entries: List[ReconciliationEntry] = []
        matched_count = 0
        discrepancy_count = 0

        for tx in transactions:
            # Calculate expected settlement: gross amount minus illustrative MDR
            # Expected = Amount * (1 - MDR)
            expected_net = (tx.amount * (Decimal("1.0") - mdr_rate)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            settlement_item = line_items_by_tx.get(tx.id)

            if settlement_item is not None:
                actual_net = settlement_item.net_amount
                variance = abs(expected_net - actual_net)

                if variance <= tolerance:
                    m_status = MatchStatus.MATCHED
                    e_status = ReconciliationEntryStatus.MATCHED
                    notes = None
                    matched_count += 1
                else:
                    m_status = MatchStatus.MANUAL_REVIEW
                    e_status = ReconciliationEntryStatus.AMOUNT_MISMATCH
                    notes = (
                        f"Amount variance of INR {variance:.2f} exceeds tolerance of INR {tolerance:.2f}. "
                        f"(Expected: {expected_net}, Actual: {actual_net})"
                    )
                    discrepancy_count += 1
            else:
                actual_net = Decimal("0.00")
                # Check settlement grace period
                tx_created = tx.created_at
                if tx_created.tzinfo is None:
                    tx_created = tx_created.replace(tzinfo=timezone.utc)

                if tx_created < grace_cutoff:
                    m_status = MatchStatus.UNMATCHED
                    e_status = ReconciliationEntryStatus.MISSING_IN_PROVIDER
                    notes = f"No settlement record found past grace period of {grace_hours} hours."
                    discrepancy_count += 1
                else:
                    m_status = MatchStatus.MANUAL_REVIEW
                    e_status = ReconciliationEntryStatus.MISSING_IN_PROVIDER
                    notes = f"Pending settlement within {grace_hours} hours grace period."
                    discrepancy_count += 1

            entry = ReconciliationEntry(
                batch_id=batch.id,
                transaction_id=tx.id,
                provider_ref_id=tx.provider_ref_id,
                expected_amount=expected_net,
                actual_amount=actual_net,
                match_status=m_status,
                status=e_status,
                notes=notes,
            )
            db.add(entry)
            entries.append(entry)

        total_count = len(entries)
        mismatched_count = total_count - matched_count

        # 4. Finalize batch status
        if discrepancy_count > 0:
            final_status = ReconciliationStatus.DISCREPANCIES_FOUND
        elif total_count > 0:
            final_status = ReconciliationStatus.MATCHED
        else:
            final_status = ReconciliationStatus.COMPLETED

        batch.total_records = total_count
        batch.matched_records = matched_count
        batch.mismatched_records = mismatched_count
        batch.discrepancy_count = discrepancy_count
        batch.status = final_status

        db.commit()
        db.refresh(batch)

        # 5. If the batch is fully MATCHED, enqueue settlement creation.
        #    The Celery task is idempotent — safe to call even if a settlement
        #    was already created (e.g. on retries).
        if final_status == ReconciliationStatus.MATCHED:
            try:
                from app.modules.settlements.tasks import create_settlement_from_batch
                create_settlement_from_batch.apply_async(args=[str(batch.id)], countdown=2)
            except Exception as task_exc:
                # Non-fatal: settlement can be re-triggered manually or by the nightly task.
                logger.warning(
                    "settlement_task_dispatch_failed",
                    batch_id=str(batch.id),
                    error=str(task_exc),
                )

        # 6. Record audit trail
        record_audit(
            db=db,
            actor_id=actor_id,
            merchant_id=merchant_id,
            action=AuditAction.CREATE,
            entity_name="reconciliation_batches",
            entity_id=batch.id,
            after={
                "merchant_id": str(merchant_id),
                "batch_id": str(batch.id),
                "total_records": total_count,
                "matched_records": matched_count,
                "discrepancies": discrepancy_count,
                "status": final_status.value,
                "mdr_rate": str(mdr_rate),
            },
        )
        db.commit()

        logger.info(
            "reconciliation_batch_completed",
            merchant_id=str(merchant_id),
            batch_id=str(batch.id),
            total=total_count,
            matched=matched_count,
            discrepancies=discrepancy_count,
            status=final_status.value,
        )

        return batch

    @staticmethod
    def list_merchant_batches(
        db: Session,
        merchant_id: uuid.UUID,
        pagination_params: PaginationParams,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status: Optional[ReconciliationStatus] = None,
    ):
        """Lists reconciliation batches for a merchant with date and status filters."""
        from app.modules.reconciliation.schemas import ReconciliationBatchResponse

        query = (
            db.query(ReconciliationBatch)
            .filter(ReconciliationBatch.merchant_id == merchant_id)
        )

        if from_date:
            query = query.filter(ReconciliationBatch.batch_date >= from_date)
        if to_date:
            query = query.filter(ReconciliationBatch.batch_date <= to_date)
        if status:
            query = query.filter(ReconciliationBatch.status == status)

        query = query.order_by(ReconciliationBatch.created_at.desc())
        items, total = paginate_query(query, pagination_params)
        response_items = [ReconciliationBatchResponse.model_validate(b) for b in items]
        return PaginatedResponse.create(
            items=response_items,
            total=total,
            params=pagination_params,
        )

    @staticmethod
    def get_batch_entries(
        db: Session,
        batch_id: uuid.UUID,
        pagination_params: PaginationParams,
        match_status: Optional[MatchStatus] = None,
    ):
        """Retrieves paginated entries for a reconciliation batch, optionally filtered by match_status."""
        from app.modules.reconciliation.schemas import ReconciliationEntryResponse

        batch = (
            db.query(ReconciliationBatch)
            .filter(ReconciliationBatch.id == batch_id)
            .first()
        )
        if not batch:
            raise EntityNotFoundException("ReconciliationBatch", batch_id)

        query = (
            db.query(ReconciliationEntry)
            .filter(ReconciliationEntry.batch_id == batch_id)
        )

        if match_status:
            query = query.filter(ReconciliationEntry.match_status == match_status)

        query = query.order_by(ReconciliationEntry.created_at.asc())
        items, total = paginate_query(query, pagination_params)
        response_items = [ReconciliationEntryResponse.model_validate(e) for e in items]
        return batch, PaginatedResponse.create(
            items=response_items,
            total=total,
            params=pagination_params,
        )
