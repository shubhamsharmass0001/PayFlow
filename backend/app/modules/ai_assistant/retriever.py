"""Structured Data Retriever for PayFlow AI Assistant.

Fetches ground-truth data exclusively from merchant-scoped PostgreSQL tables
and existing analytical services (AnalyticsService, SettlementsService, Invoices).
Ensures zero data hallucinations by strictly feeding actual records into the prompt.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
import re
from typing import Any, Dict, List, Tuple
import uuid

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from app.modules.analytics.schemas import GranularityEnum
from app.modules.analytics.service import AnalyticsService
from app.modules.customers.models import Customer
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.payments.models import PaymentTransaction, TransactionStatus
from app.modules.settlements.models import Settlement
from app.modules.ai_assistant.schemas import SourceCitation


class IntentType:
    OVERDUE_INVOICES = "OVERDUE_INVOICES"
    REVENUE_ANALYTICS = "REVENUE_ANALYTICS"
    SETTLEMENTS_SUMMARY = "SETTLEMENTS_SUMMARY"
    PAYMENT_METHODS = "PAYMENT_METHODS"
    TRANSACTIONS_SUMMARY = "TRANSACTIONS_SUMMARY"
    GENERAL_OVERVIEW = "GENERAL_OVERVIEW"


def detect_intent(question: str) -> str:
    """Classifies user natural-language question into a primary intent category."""
    q = question.lower()

    if any(k in q for k in ["overdue", "unpaid", "pending invoice", "late invoice", "who owes", "customers owe", "due invoice", "which customer"]):
        return IntentType.OVERDUE_INVOICES
    elif any(k in q for k in ["settle", "payout", "utr", "bank transfer", "mdr", "fees", "deduction"]):
        return IntentType.SETTLEMENTS_SUMMARY
    elif any(k in q for k in ["payment method", "method", "upi vs", "channel", "qr vs", "card vs"]):
        return IntentType.PAYMENT_METHODS
    elif any(k in q for k in ["dip", "drop", "fall", "spike", "trend", "revenue", "sales", "collections", "tuesday", "yesterday", "last week", "last month", "growth"]):
        return IntentType.REVENUE_ANALYTICS
    elif any(k in q for k in ["failed", "failure", "fail", "success rate", "recent transaction", "highest transaction"]):
        return IntentType.TRANSACTIONS_SUMMARY
    else:
        return IntentType.GENERAL_OVERVIEW


class StructuredDataRetriever:
    """Retrieves grounded structured data for a merchant from database services."""

    def __init__(self, db: Session, merchant_id: uuid.UUID):
        self.db = db
        self.merchant_id = merchant_id

    def retrieve_context(self, question: str) -> Tuple[str, Dict[str, Any], List[SourceCitation]]:
        """Determines intent and extracts relevant merchant records."""
        intent = detect_intent(question)
        underlying_data: Dict[str, Any] = {
            "merchant_id": str(self.merchant_id),
            "intent": intent,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        citations: List[SourceCitation] = []

        if intent == IntentType.OVERDUE_INVOICES:
            self._fetch_invoices_context(underlying_data, citations)
        elif intent == IntentType.REVENUE_ANALYTICS:
            self._fetch_revenue_context(underlying_data, citations, question)
        elif intent == IntentType.SETTLEMENTS_SUMMARY:
            self._fetch_settlements_context(underlying_data, citations)
        elif intent == IntentType.PAYMENT_METHODS:
            self._fetch_payment_methods_context(underlying_data, citations)
        elif intent == IntentType.TRANSACTIONS_SUMMARY:
            self._fetch_transactions_context(underlying_data, citations)
        else:
            self._fetch_general_context(underlying_data, citations)

        return intent, underlying_data, citations

    def _fetch_invoices_context(
        self, underlying_data: Dict[str, Any], citations: List[SourceCitation]
    ) -> None:
        """Retrieves overdue and open invoices along with customer details."""
        now_utc = datetime.now(timezone.utc)

        invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.customer))
            .filter(
                Invoice.merchant_id == self.merchant_id,
                Invoice.deleted_at.is_(None),
                Invoice.status.in_([
                    InvoiceStatus.OVERDUE,
                    InvoiceStatus.SENT,
                    InvoiceStatus.ISSUED,
                    InvoiceStatus.PARTIALLY_PAID,
                ]),
            )
            .order_by(Invoice.due_date.asc())
            .all()
        )

        overdue_list = []
        total_overdue = Decimal("0.00")

        for inv in invoices:
            is_overdue = (
                inv.status == InvoiceStatus.OVERDUE
                or (inv.due_date and inv.due_date < now_utc)
            )
            if is_overdue:
                balance = inv.total_amount - inv.paid_amount
                total_overdue += balance
                customer_name = inv.customer.name if inv.customer else "Walk-in Customer"
                customer_phone = inv.customer.phone if inv.customer else "N/A"
                customer_email = inv.customer.email if inv.customer else "N/A"

                item_record = {
                    "invoice_id": str(inv.id),
                    "invoice_number": inv.invoice_number,
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_email": customer_email,
                    "total_amount": float(inv.total_amount),
                    "paid_amount": float(inv.paid_amount),
                    "balance_due": float(balance),
                    "due_date": inv.due_date.strftime("%Y-%m-%d") if inv.due_date else "None",
                    "status": inv.status.value,
                }
                overdue_list.append(item_record)

                citations.append(
                    SourceCitation(
                        entity_type="invoice",
                        id=str(inv.id),
                        reference=inv.invoice_number,
                        details={
                            "customer": customer_name,
                            "balance_due": float(balance),
                            "due_date": inv.due_date.strftime("%Y-%m-%d") if inv.due_date else "None",
                        },
                    )
                )

        underlying_data["overdue_invoices"] = {
            "count": len(overdue_list),
            "total_overdue_amount": float(total_overdue),
            "items": overdue_list,
        }

    def _fetch_revenue_context(
        self, underlying_data: Dict[str, Any], citations: List[SourceCitation], question: str
    ) -> None:
        """Retrieves daily revenue trends and overview metrics to explain dips or spikes."""
        overview = AnalyticsService.get_overview(self.db, self.merchant_id)
        trend = AnalyticsService.get_revenue_trend(
            self.db, self.merchant_id, granularity=GranularityEnum.DAY
        )

        trend_points = [
            {
                "period": p.period,
                "label": p.label,
                "amount": float(p.amount),
                "transaction_count": p.transaction_count,
            }
            for p in trend.points
        ]

        # Identify lowest and highest revenue days
        sorted_by_amount = sorted(trend_points, key=lambda x: x["amount"])
        lowest_day = sorted_by_amount[0] if sorted_by_amount else None
        highest_day = sorted_by_amount[-1] if sorted_by_amount else None
        avg_revenue = (
            sum(p["amount"] for p in trend_points) / len(trend_points)
            if trend_points
            else 0.0
        )

        # Check for failed transactions in the last 7 days that could explain dips
        since_7d = datetime.now(timezone.utc) - timedelta(days=7)
        recent_failures = (
            self.db.query(PaymentTransaction)
            .filter(
                PaymentTransaction.merchant_id == self.merchant_id,
                PaymentTransaction.created_at >= since_7d,
                PaymentTransaction.status == TransactionStatus.FAILED,
            )
            .order_by(PaymentTransaction.created_at.desc())
            .limit(10)
            .all()
        )

        failed_tx_list = [
            {
                "transaction_id": str(tx.id),
                "amount": float(tx.amount),
                "created_at": tx.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "failure_reason": tx.failure_reason or "Bank decline / network failure",
            }
            for tx in recent_failures
        ]

        underlying_data["revenue_analytics"] = {
            "overview": overview.model_dump(),
            "trend_granularity": "day",
            "trend_points": trend_points,
            "lowest_day": lowest_day,
            "highest_day": highest_day,
            "average_daily_revenue": round(avg_revenue, 2),
            "recent_failed_transactions": failed_tx_list,
        }

        citations.append(
            SourceCitation(
                entity_type="analytics_metric",
                reference="revenue_trend_daily",
                details={
                    "total_data_points": len(trend_points),
                    "average_daily_revenue": round(avg_revenue, 2),
                    "lowest_day": lowest_day,
                },
            )
        )
        citations.append(
            SourceCitation(
                entity_type="analytics_metric",
                reference="analytics_overview",
                details={
                    "today_collections": float(overview.today_collections),
                    "this_week_collections": float(overview.this_week_collections),
                    "success_rate": overview.success_rate,
                },
            )
        )

    def _fetch_settlements_context(
        self, underlying_data: Dict[str, Any], citations: List[SourceCitation]
    ) -> None:
        """Retrieves recent merchant settlement batches and payout status."""
        settlements = (
            self.db.query(Settlement)
            .filter(Settlement.merchant_id == self.merchant_id)
            .order_by(Settlement.settlement_date.desc())
            .limit(10)
            .all()
        )

        settlement_items = []
        for s in settlements:
            item = {
                "settlement_id": str(s.id),
                "settlement_date": s.settlement_date.strftime("%Y-%m-%d"),
                "status": s.status.value,
                "gross_amount": float(s.gross_amount),
                "mdr_amount": float(s.mdr_amount),
                "tax_on_mdr": float(s.tax_on_mdr),
                "net_amount": float(s.net_amount),
                "utr_reference": s.utr_reference,
                "transaction_count": s.transaction_count,
            }
            settlement_items.append(item)

            citations.append(
                SourceCitation(
                    entity_type="settlement",
                    id=str(s.id),
                    reference=s.utr_reference,
                    details={
                        "settlement_date": item["settlement_date"],
                        "net_amount": item["net_amount"],
                        "status": item["status"],
                    },
                )
            )

        underlying_data["settlements"] = {
            "total_records": len(settlement_items),
            "recent_settlements": settlement_items,
        }

    def _fetch_payment_methods_context(
        self, underlying_data: Dict[str, Any], citations: List[SourceCitation]
    ) -> None:
        """Retrieves breakdown across payment channels (UPI, Cards, etc.)."""
        methods_response = AnalyticsService.get_payment_methods(self.db, self.merchant_id)
        underlying_data["payment_methods_breakdown"] = methods_response.model_dump()

        citations.append(
            SourceCitation(
                entity_type="analytics_metric",
                reference="payment_methods_breakdown",
                details={
                    "methods_tracked": len(methods_response.breakdown),
                },
            )
        )

    def _fetch_transactions_context(
        self, underlying_data: Dict[str, Any], citations: List[SourceCitation]
    ) -> None:
        """Retrieves recent transactions and success/failure statistics."""
        overview = AnalyticsService.get_overview(self.db, self.merchant_id)

        recent_txs = (
            self.db.query(PaymentTransaction)
            .filter(PaymentTransaction.merchant_id == self.merchant_id)
            .order_by(PaymentTransaction.created_at.desc())
            .limit(10)
            .all()
        )

        tx_list = []
        for tx in recent_txs:
            item = {
                "transaction_id": str(tx.id),
                "amount": float(tx.amount),
                "currency": tx.currency,
                "status": tx.status.value,
                "payment_method": tx.payment_method.value if tx.payment_method else "UPI",
                "payer_vpa": tx.payer_vpa,
                "created_at": tx.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "failure_reason": tx.failure_reason,
            }
            tx_list.append(item)

            citations.append(
                SourceCitation(
                    entity_type="transaction",
                    id=str(tx.id),
                    reference=f"TXN-{str(tx.id)[:8].upper()}",
                    details={
                        "amount": item["amount"],
                        "status": item["status"],
                        "method": item["payment_method"],
                    },
                )
            )

        underlying_data["transactions_summary"] = {
            "success_rate": overview.success_rate,
            "average_transaction_value": float(overview.average_transaction_value),
            "pending_count": overview.pending_count,
            "recent_transactions": tx_list,
        }

    def _fetch_general_context(
        self, underlying_data: Dict[str, Any], citations: List[SourceCitation]
    ) -> None:
        """Assembles high-level operational overview across all domains."""
        overview = AnalyticsService.get_overview(self.db, self.merchant_id)
        underlying_data["overview"] = overview.model_dump()

        citations.append(
            SourceCitation(
                entity_type="analytics_metric",
                reference="analytics_overview",
                details={
                    "today_collections": float(overview.today_collections),
                    "this_week_collections": float(overview.this_week_collections),
                    "this_month_collections": float(overview.this_month_collections),
                    "success_rate": overview.success_rate,
                },
            )
        )

        # Include recent settlement status
        latest_settlement = (
            self.db.query(Settlement)
            .filter(Settlement.merchant_id == self.merchant_id)
            .order_by(Settlement.settlement_date.desc())
            .first()
        )
        if latest_settlement:
            underlying_data["latest_settlement"] = {
                "date": latest_settlement.settlement_date.strftime("%Y-%m-%d"),
                "net_amount": float(latest_settlement.net_amount),
                "utr_reference": latest_settlement.utr_reference,
                "status": latest_settlement.status.value,
            }
            citations.append(
                SourceCitation(
                    entity_type="settlement",
                    id=str(latest_settlement.id),
                    reference=latest_settlement.utr_reference,
                    details={
                        "date": latest_settlement.settlement_date.strftime("%Y-%m-%d"),
                        "net_amount": float(latest_settlement.net_amount),
                    },
                )
            )

        # Include count of overdue invoices
        now_utc = datetime.now(timezone.utc)
        overdue_count = (
            self.db.query(func.count(Invoice.id))
            .filter(
                Invoice.merchant_id == self.merchant_id,
                Invoice.deleted_at.is_(None),
                or_(
                    Invoice.status == InvoiceStatus.OVERDUE,
                    and_(
                        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.ISSUED]),
                        Invoice.due_date < now_utc,
                    ),
                ),
            )
            .scalar()
            or 0
        )
        underlying_data["overdue_invoices_count"] = overdue_count
