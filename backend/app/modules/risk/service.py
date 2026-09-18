"""Risk Module Service.

Provides:
  - Auditable and explainable risk rule evaluations (VELOCITY_SPIKE, ODD_HOUR, STRUCTURING_PATTERN)
  - Recording and deduplication of risk signals
  - Querying merchant signals with severity and review status filters
  - Review / resolution workflow with audit logging
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.logging import logger
from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.modules.refunds.models import Refund
from app.modules.risk.models import RiskAction, RiskLevel, RiskSignal
from app.modules.risk.schemas import (
    RiskRuleDefinition,
    RiskRulesDocumentationResponse,
    RiskSignalResponse,
)
from app.shared.exceptions import EntityNotFoundException
from app.shared.pagination import PaginationParams, paginate_query

# Indian Standard Time offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


class RiskService:
    """Core domain service for fraud prevention, velocity monitoring, and risk governance."""

    @classmethod
    def record_risk_signal(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        rule_triggered: str,
        risk_score: Decimal,
        risk_level: RiskLevel = RiskLevel.HIGH,
        action_taken: RiskAction = RiskAction.FLAG_FOR_REVIEW,
        transaction_id: Optional[uuid.UUID] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> RiskSignal:
        """Records a RiskSignal (deduplicated per transaction + rule) and dispatches alert."""
        # Deduplication check
        if transaction_id:
            existing = (
                db.query(RiskSignal)
                .filter(
                    RiskSignal.transaction_id == transaction_id,
                    RiskSignal.rule_triggered == rule_triggered,
                )
                .first()
            )
            if existing:
                return existing

        signal = RiskSignal(
            merchant_id=merchant_id,
            transaction_id=transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            rule_triggered=rule_triggered,
            action_taken=action_taken,
            metadata_json=metadata_json,
            is_reviewed=False,
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)

        logger.warning(
            "risk_signal_raised",
            signal_id=str(signal.id),
            merchant_id=str(merchant_id),
            rule=rule_triggered,
            risk_score=str(risk_score),
            level=risk_level.value,
        )

        # Dispatch Notification alert
        try:
            from app.modules.notifications.models import NotificationChannel
            from app.modules.notifications.service import NotificationService

            NotificationService.send_notification(
                merchant_id=merchant_id,
                channel=NotificationChannel.PUSH,
                template="risk_signal_raised",
                payload={
                    "risk_signal_id": str(signal.id),
                    "rule_triggered": rule_triggered,
                    "risk_score": str(risk_score),
                    "risk_level": risk_level.value,
                    "action_taken": action_taken.value,
                    "transaction_id": str(transaction_id) if transaction_id else None,
                },
            )
        except Exception:
            pass

        return signal

    # ==========================================================================
    # EXPLICIT, AUDITABLE RULE EVALUATIONS
    # ==========================================================================

    @classmethod
    def evaluate_velocity_spike(
        cls,
        db: Session,
        tx: PaymentTransaction,
    ) -> Optional[RiskSignal]:
        """Evaluates VELOCITY_SPIKE rule.

        Logic:
          1. Volume/Count Spike:
             - Calculates transaction count for this merchant in the last 1 hour.
             - Compares against the merchant's trailing 7-day hourly baseline (average count/hr).
             - If recent count >= 5 AND (trailing_avg == 0 OR count >= 3.0 * trailing_avg):
               Flag VELOCITY_SPIKE.
          2. Value/Amount Spike:
             - Compares current transaction amount against the merchant's historical average amount.
             - If tx.amount >= 10,000 AND historical average > 0 AND tx.amount >= 5.0 * historical_avg:
               Flag VELOCITY_SPIKE.
        """
        now = tx.created_at or datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        seven_days_ago = now - timedelta(days=7)

        # 1. Count velocity in last 1 hour
        recent_count = (
            db.query(func.count(PaymentTransaction.id))
            .filter(
                PaymentTransaction.merchant_id == tx.merchant_id,
                PaymentTransaction.created_at >= one_hour_ago,
                PaymentTransaction.created_at <= now,
            )
            .scalar()
            or 0
        )

        # Trailing 7-day baseline (excluding the last hour)
        trailing_count = (
            db.query(func.count(PaymentTransaction.id))
            .filter(
                PaymentTransaction.merchant_id == tx.merchant_id,
                PaymentTransaction.created_at >= seven_days_ago,
                PaymentTransaction.created_at < one_hour_ago,
            )
            .scalar()
            or 0
        )
        trailing_hours = Decimal("167.0")  # (7 * 24) - 1
        trailing_hourly_avg = Decimal(trailing_count) / trailing_hours

        is_count_spike = False
        count_multiplier = Decimal("0.0")
        if recent_count >= 5:
            if trailing_hourly_avg > 0:
                count_multiplier = Decimal(recent_count) / trailing_hourly_avg
                if count_multiplier >= Decimal("3.0"):
                    is_count_spike = True
            else:
                is_count_spike = True
                count_multiplier = Decimal(recent_count)

        # 2. Amount velocity
        avg_amount = (
            db.query(func.avg(PaymentTransaction.amount))
            .filter(
                PaymentTransaction.merchant_id == tx.merchant_id,
                PaymentTransaction.created_at < now,
            )
            .scalar()
        )
        is_amount_spike = False
        amount_multiplier = Decimal("0.0")
        if avg_amount and avg_amount > 0 and tx.amount >= Decimal("10000.00"):
            amount_multiplier = tx.amount / Decimal(str(avg_amount))
            if amount_multiplier >= Decimal("5.0"):
                is_amount_spike = True

        if is_count_spike or is_amount_spike:
            return cls.record_risk_signal(
                db=db,
                merchant_id=tx.merchant_id,
                transaction_id=tx.id,
                rule_triggered="VELOCITY_SPIKE",
                risk_score=Decimal("80.00") if (is_count_spike and is_amount_spike) else Decimal("75.00"),
                risk_level=RiskLevel.HIGH,
                action_taken=RiskAction.FLAG_FOR_REVIEW,
                metadata_json={
                    "is_count_spike": is_count_spike,
                    "recent_hourly_count": recent_count,
                    "trailing_hourly_avg": float(round(trailing_hourly_avg, 2)),
                    "count_multiplier": float(round(count_multiplier, 2)),
                    "is_amount_spike": is_amount_spike,
                    "transaction_amount": str(tx.amount),
                    "historical_avg_amount": str(round(avg_amount, 2)) if avg_amount else None,
                    "amount_multiplier": float(round(amount_multiplier, 2)),
                },
            )
        return None

    @classmethod
    def evaluate_odd_hour(
        cls,
        db: Session,
        tx: PaymentTransaction,
    ) -> Optional[RiskSignal]:
        """Evaluates ODD_HOUR rule.

        Logic:
          - Converts transaction UTC timestamp to Indian Standard Time (IST, UTC+5:30).
          - Normal business operating hours in India are defined as 06:00 to 23:00 IST.
          - Odd hours are 01:00 to 04:59 IST (hours 1, 2, 3, 4).
          - If transaction occurs in odd hours, checks merchant historical patterns:
            if < 5% of their total historical transactions happen in this window,
            flags ODD_HOUR.
        """
        tx_time = tx.created_at or datetime.now(timezone.utc)
        if tx_time.tzinfo is None:
            tx_time = tx_time.replace(tzinfo=timezone.utc)
        ist_time = tx_time.astimezone(IST)
        hour = ist_time.hour

        # Check if hour is in midnight/pre-dawn window (01:00 to 04:59 IST)
        if 1 <= hour <= 4:
            total_txs = (
                db.query(func.count(PaymentTransaction.id))
                .filter(PaymentTransaction.merchant_id == tx.merchant_id)
                .scalar()
                or 0
            )
            # If new merchant or low volume, flag by default
            odd_hour_ratio = Decimal("0.0")
            if total_txs > 10:
                # Count historical transactions in odd hours (extract hour in IST)
                odd_hour_count = (
                    db.query(func.count(PaymentTransaction.id))
                    .filter(
                        PaymentTransaction.merchant_id == tx.merchant_id,
                        func.extract("hour", func.timezone("Asia/Kolkata", PaymentTransaction.created_at)).in_([1, 2, 3, 4]),
                    )
                    .scalar()
                    or 0
                )
                odd_hour_ratio = Decimal(odd_hour_count) / Decimal(total_txs)

            if total_txs <= 10 or odd_hour_ratio < Decimal("0.05"):
                return cls.record_risk_signal(
                    db=db,
                    merchant_id=tx.merchant_id,
                    transaction_id=tx.id,
                    rule_triggered="ODD_HOUR",
                    risk_score=Decimal("50.00"),
                    risk_level=RiskLevel.MEDIUM,
                    action_taken=RiskAction.FLAG_FOR_REVIEW,
                    metadata_json={
                        "hour_ist": hour,
                        "ist_timestamp": ist_time.isoformat(),
                        "normal_business_hours": "06:00 - 23:00 IST",
                        "odd_hour_ratio": float(round(odd_hour_ratio, 3)),
                        "threshold_ratio": 0.05,
                    },
                )
        return None

    @classmethod
    def evaluate_structuring_pattern(
        cls,
        db: Session,
        tx: PaymentTransaction,
    ) -> Optional[RiskSignal]:
        """Evaluates STRUCTURING_PATTERN rule.

        Logic:
          1. Sub-₹2,000 threshold avoidance:
             - Indian UPI guidelines feature simplified 2FA / zero-MDR thresholds below ₹2,000.
             - Fraudsters deliberately cluster transactions in the ₹1,800.00 – ₹1,999.99 range.
             - If >= 3 transactions in this range occur against the same customer or invoice
               within a trailing 24-hour window outside a documented installment plan:
               Flag STRUCTURING_PATTERN.
          2. Split payment heuristic:
             - If linked to an invoice, evaluates Phase 9 structuring detector.
        """
        now = tx.created_at or datetime.now(timezone.utc)
        window_start = now - timedelta(hours=24)

        # 1. Sub-2000 clustering
        if Decimal("1800.00") <= tx.amount <= Decimal("1999.99"):
            query = db.query(PaymentTransaction).filter(
                PaymentTransaction.merchant_id == tx.merchant_id,
                PaymentTransaction.created_at >= window_start,
                PaymentTransaction.amount >= Decimal("1800.00"),
                PaymentTransaction.amount <= Decimal("1999.99"),
            )
            if tx.customer_id:
                query = query.filter(PaymentTransaction.customer_id == tx.customer_id)
            elif tx.invoice_id:
                query = query.filter(PaymentTransaction.invoice_id == tx.invoice_id)

            cluster_count = query.count()
            if cluster_count >= 3:
                return cls.record_risk_signal(
                    db=db,
                    merchant_id=tx.merchant_id,
                    transaction_id=tx.id,
                    rule_triggered="STRUCTURING_PATTERN",
                    risk_score=Decimal("85.00"),
                    risk_level=RiskLevel.HIGH,
                    action_taken=RiskAction.FLAG_FOR_REVIEW,
                    metadata_json={
                        "reason": "sub_2000_threshold_clustering",
                        "cluster_count": cluster_count,
                        "time_window_hours": 24,
                        "threshold_target": "2000.00 INR",
                        "customer_id": str(tx.customer_id) if tx.customer_id else None,
                        "invoice_id": str(tx.invoice_id) if tx.invoice_id else None,
                    },
                )

        # 2. Phase 9 Split Structuring Heuristic
        if tx.invoice_id:
            try:
                from app.modules.splits.service import SplitPaymentService
                is_split_structured, split_meta = SplitPaymentService.detect_structuring(
                    db=db,
                    invoice_id=tx.invoice_id,
                )
                if is_split_structured:
                    return cls.record_risk_signal(
                        db=db,
                        merchant_id=tx.merchant_id,
                        transaction_id=tx.id,
                        rule_triggered="STRUCTURING_PATTERN",
                        risk_score=Decimal("90.00"),
                        risk_level=RiskLevel.HIGH,
                        action_taken=RiskAction.FLAG_FOR_REVIEW,
                        metadata_json={
                            "reason": "split_payment_structuring",
                            "split_metadata": split_meta,
                        },
                    )
            except Exception:
                pass

        return None

    @classmethod
    def evaluate_transaction_rules(
        cls,
        db: Session,
        transaction_id: uuid.UUID,
        refund_id: Optional[uuid.UUID] = None,
    ) -> List[RiskSignal]:
        """Evaluates all active risk rules for a given transaction or refund event."""
        tx = (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.id == transaction_id)
            .first()
        )
        if not tx:
            return []

        signals: List[RiskSignal] = []

        # 1. Velocity Spike
        s1 = cls.evaluate_velocity_spike(db, tx)
        if s1:
            signals.append(s1)

        # 2. Odd Hour
        s2 = cls.evaluate_odd_hour(db, tx)
        if s2:
            signals.append(s2)

        # 3. Structuring Pattern
        s3 = cls.evaluate_structuring_pattern(db, tx)
        if s3:
            signals.append(s3)

        # Note on GEO_MISMATCH:
        # Client/device geographic coordinates are not captured at gateway level.
        # Following explicit guidance, GEO_MISMATCH is omitted rather than faked.

        return signals

    # ==========================================================================
    # QUERY & REVIEW INTERFACES
    # ==========================================================================

    @classmethod
    def list_merchant_risk_signals(
        cls,
        db: Session,
        merchant_id: uuid.UUID,
        severity: Optional[RiskLevel] = None,
        reviewed: Optional[bool] = None,
        rule_triggered: Optional[str] = None,
        pagination_params: Optional[PaginationParams] = None,
    ) -> Tuple[List[RiskSignalResponse], int]:
        """Lists risk signals for a merchant with optional filtering and pagination."""
        params = pagination_params or PaginationParams(page=1, page_size=20)
        query = (
            db.query(RiskSignal)
            .filter(RiskSignal.merchant_id == merchant_id)
        )

        if severity is not None:
            query = query.filter(RiskSignal.risk_level == severity)

        if reviewed is not None:
            query = query.filter(RiskSignal.is_reviewed == reviewed)

        if rule_triggered:
            query = query.filter(RiskSignal.rule_triggered == rule_triggered.strip())

        query = query.order_by(RiskSignal.created_at.desc())
        items, total = paginate_query(query, params)

        responses = [RiskSignalResponse.model_validate(item) for item in items]
        return responses, total

    @classmethod
    def review_signal(
        cls,
        db: Session,
        signal_id: uuid.UUID,
        resolution_note: str,
        reviewed_by: Optional[uuid.UUID] = None,
        action_taken: Optional[RiskAction] = None,
        actor: Optional[Any] = None,
    ) -> RiskSignalResponse:
        """Marks a risk signal as reviewed with an auditable resolution note."""
        signal = db.query(RiskSignal).filter(RiskSignal.id == signal_id).first()
        if not signal:
            raise EntityNotFoundException("RiskSignal", signal_id)

        before_state = {
            "is_reviewed": signal.is_reviewed,
            "reviewed_by": str(signal.reviewed_by) if signal.reviewed_by else None,
            "reviewed_at": signal.reviewed_at.isoformat() if signal.reviewed_at else None,
            "resolution_note": signal.resolution_note,
            "action_taken": signal.action_taken.value,
        }

        reviewer_id = reviewed_by or (actor.id if actor else None)
        signal.is_reviewed = True
        signal.reviewed_by = reviewer_id
        signal.reviewed_at = datetime.now(timezone.utc)
        signal.resolution_note = resolution_note
        if action_taken:
            signal.action_taken = action_taken

        db.commit()
        db.refresh(signal)

        after_state = {
            "is_reviewed": signal.is_reviewed,
            "reviewed_by": str(signal.reviewed_by) if signal.reviewed_by else None,
            "reviewed_at": signal.reviewed_at.isoformat() if signal.reviewed_at else None,
            "resolution_note": signal.resolution_note,
            "action_taken": signal.action_taken.value,
        }

        # Audit the review action
        record_audit(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_name="risk_signals",
            entity_id=signal.id,
            actor_id=reviewer_id,
            merchant_id=signal.merchant_id,
            before=before_state,
            after=after_state,
        )

        return RiskSignalResponse.model_validate(signal)

    @classmethod
    def get_documented_rules(cls) -> RiskRulesDocumentationResponse:
        """Returns fully explainable, transparent documentation for all active risk rules."""
        return RiskRulesDocumentationResponse(
            rules=[
                RiskRuleDefinition(
                    rule_name="VELOCITY_SPIKE",
                    description="Detects anomalous bursts in transaction count or transaction value far exceeding trailing merchant baselines.",
                    evaluation_trigger="Post-transaction settlement / status update",
                    thresholds={
                        "count_threshold": "Recent 1-hour count >= 5 AND >= 3.0x trailing 7-day hourly average",
                        "amount_threshold": "Transaction amount >= ₹10,000 AND >= 5.0x historical average transaction amount",
                    },
                    default_severity=RiskLevel.HIGH,
                    default_action=RiskAction.FLAG_FOR_REVIEW,
                    rationale="Velocity spikes indicate card testing, credential stuffing, or unexpected sudden merchant turnover anomalies.",
                ),
                RiskRuleDefinition(
                    rule_name="ODD_HOUR",
                    description="Detects transactions processed during abnormal local hours (01:00 to 04:59 IST) for retail merchants.",
                    evaluation_trigger="Post-transaction settlement",
                    thresholds={
                        "hour_window": "01:00 - 04:59 IST",
                        "historical_odd_hour_ratio": "< 5.0% of merchant historical turnover",
                    },
                    default_severity=RiskLevel.MEDIUM,
                    default_action=RiskAction.FLAG_FOR_REVIEW,
                    rationale="Legitimate retail merchants rarely transact at 03:00 AM; off-hours activity correlates with automated script testing.",
                ),
                RiskRuleDefinition(
                    rule_name="STRUCTURING_PATTERN",
                    description="Detects artificial transaction structuring designed to avoid Indian banking thresholds and 2FA limits.",
                    evaluation_trigger="Post-transaction / split payment detection",
                    thresholds={
                        "sub_2000_threshold": ">= 3 transactions between ₹1,800.00 and ₹1,999.99 in 24 hours against same customer/invoice",
                        "split_heuristic": "Multiple rapid splits summing to invoice total within 15 minutes",
                    },
                    default_severity=RiskLevel.HIGH,
                    default_action=RiskAction.FLAG_FOR_REVIEW,
                    rationale="Under Indian regulations, transactions below ₹2,000 often benefit from relaxed authentication; fraudsters split payments to evade KYC triggers.",
                ),
                RiskRuleDefinition(
                    rule_name="GEO_MISMATCH",
                    description="Omitted. Client geolocation coordinates are not captured at payment gateway level; omitted per architectural policy rather than faking telemetry.",
                    evaluation_trigger="N/A",
                    thresholds={"status": "OMITTED_NO_DEVICE_GEOLOCATION"},
                    default_severity=RiskLevel.LOW,
                    default_action=RiskAction.ALLOW,
                    rationale="Location signals cannot be reliably ascertained without native GPS telemetry on merchant POS devices.",
                ),
            ]
        )
