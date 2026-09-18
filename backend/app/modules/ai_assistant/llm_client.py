"""LLM Client for PayFlow AI Assistant.

Integrates with Anthropic Claude (Messages API) when an API key is provided,
and seamlessly provides a deterministic, grounded synthesizer fallback for
testing, offline development, and zero-downtime reliability.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional, Tuple
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.modules.ai_assistant.prompts import FIXED_SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.modules.ai_assistant.retriever import IntentType
from app.modules.ai_assistant.schemas import SourceCitation

MUTATION_KEYWORDS = [
    "refund",
    "initiate refund",
    "cancel invoice",
    "delete",
    "create payment",
    "send money",
    "pay out",
    "charge customer",
]


class LLMClient:
    """Client for generating grounded natural-language responses."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL

    def is_action_request(self, question: str) -> bool:
        """Detects if the user is attempting to perform an action/mutation via the Q&A endpoint."""
        q = question.lower()
        # Checks if user is commanding an action rather than querying
        action_verbs = ["issue a refund", "initiate a refund", "make a payment", "charge", "refund customer", "process refund", "cancel this invoice", "delete invoice"]
        return any(verb in q for verb in action_verbs)

    async def generate_answer(
        self,
        merchant_id: str,
        question: str,
        intent: str,
        underlying_data: Dict[str, Any],
        citations: List[SourceCitation],
    ) -> Tuple[str, str]:
        """Generates answer using Anthropic if configured, otherwise using grounded local synthesizer.

        Returns:
            Tuple[answer_text, model_used_identifier]
        """
        # Read-only guardrail check
        if self.is_action_request(question):
            answer = (
                "Action Refused: The PayFlow AI Assistant is strictly read-only and cannot initiate refunds, "
                "process payments, cancel invoices, or alter merchant records. "
                "Please use the dedicated Refunds or Invoices management screens in your PayFlow dashboard to perform this action."
            )
            return answer, "payflow-safety-guardrail"

        # Try Anthropic API if key is present
        if self.api_key and self.api_key.strip():
            try:
                answer = await self._call_anthropic(merchant_id, question, intent, underlying_data)
                return answer, self.model
            except Exception as exc:
                logger.warning("anthropic_api_call_failed_fallback_to_local", error=str(exc))
                # Fallback to deterministic synthesizer

        # Deterministic Grounded Synthesizer
        answer = self._synthesize_grounded_answer(question, intent, underlying_data, citations)
        return answer, "deterministic-grounded-synthesizer"

    async def _call_anthropic(
        self,
        merchant_id: str,
        question: str,
        intent: str,
        underlying_data: Dict[str, Any],
    ) -> str:
        """Dispatches request to Anthropic's Messages API."""
        user_prompt = USER_PROMPT_TEMPLATE.format(
            merchant_id=merchant_id,
            intent=intent,
            current_time_utc=datetime.now(timezone.utc).isoformat(),
            question=question,
            underlying_data_json=json.dumps(underlying_data, indent=2, default=str),
        )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "system": FIXED_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Extract content text from Anthropic response
            content_blocks = data.get("content", [])
            text_parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
            return "\n".join(text_parts).strip()

    def _synthesize_grounded_answer(
        self,
        question: str,
        intent: str,
        underlying_data: Dict[str, Any],
        citations: List[SourceCitation],
    ) -> str:
        """Deterministic, grounded synthesizer that structures an auditable answer directly from data."""
        if intent == IntentType.OVERDUE_INVOICES:
            invoices_data = underlying_data.get("overdue_invoices", {})
            count = invoices_data.get("count", 0)
            total_amt = invoices_data.get("total_overdue_amount", 0.0)
            items = invoices_data.get("items", [])

            if count == 0:
                return "Good news! You have no overdue or past-due invoices currently recorded for your merchant account."

            lines = [
                f"You currently have {count} overdue invoice(s) totaling ₹{total_amt:,.2f}.",
                "Here are the details for each overdue account:",
            ]
            for item in items:
                lines.append(
                    f"• {item['invoice_number']}: Customer {item['customer_name']} "
                    f"(Phone: {item['customer_phone']}) owes ₹{item['balance_due']:,.2f} "
                    f"(Total: ₹{item['total_amount']:,.2f}), which was due on {item['due_date']}."
                )
            return "\n".join(lines)

        elif intent == IntentType.REVENUE_ANALYTICS:
            rev_data = underlying_data.get("revenue_analytics", {})
            overview = rev_data.get("overview", {})
            today_coll = overview.get("today_collections", "0.00")
            success_rate = overview.get("success_rate", 100.0)
            avg_rev = rev_data.get("average_daily_revenue", 0.0)
            lowest = rev_data.get("lowest_day")
            highest = rev_data.get("highest_day")
            failed_txs = rev_data.get("recent_failed_transactions", [])

            lines = [
                f"Here is the revenue trend analysis for your merchant account:",
                f"• Average Daily Revenue: ₹{avg_rev:,.2f}.",
                f"• Today's Collections: ₹{float(today_coll):,.2f} with a {success_rate}% success rate.",
            ]
            if lowest:
                low_label = lowest.get("label") or lowest.get("period", "N/A")
                lines.append(
                    f"• Lowest Revenue Day: {low_label} with collections of ₹{lowest['amount']:,.2f} across {lowest['transaction_count']} transaction(s)."
                )
            if highest:
                high_label = highest.get("label") or highest.get("period", "N/A")
                lines.append(
                    f"• Highest Revenue Day: {high_label} with collections of ₹{highest['amount']:,.2f} across {highest['transaction_count']} transaction(s)."
                )
            if failed_txs:
                lines.append(
                    f"• Failures Identified: There were {len(failed_txs)} failed transaction(s) recorded in the recent window, which contributed to lower cleared collections."
                )
            return "\n".join(lines)

        elif intent == IntentType.SETTLEMENTS_SUMMARY:
            settlements_data = underlying_data.get("settlements", {})
            total_records = settlements_data.get("total_records", 0)
            items = settlements_data.get("recent_settlements", [])

            if total_records == 0:
                return "No settlement records were found for your merchant account yet. Settlements are created following matched bank reconciliation batches."

            latest = items[0]
            lines = [
                f"Found {total_records} settlement record(s) for your merchant account.",
                f"• Latest Settlement: ₹{latest['net_amount']:,.2f} net payout (Gross: ₹{latest['gross_amount']:,.2f}, MDR Fee: ₹{latest['mdr_amount']:,.2f}, Tax: ₹{latest['tax_on_mdr']:,.2f}).",
                f"• Settlement Date: {latest['settlement_date']}, Status: {latest['status']}.",
                f"• Bank UTR Reference: {latest['utr_reference']}.",
            ]
            if len(items) > 1:
                lines.append("Previous settlements:")
                for s in items[1:4]:
                    lines.append(
                        f"  - {s['settlement_date']}: ₹{s['net_amount']:,.2f} ({s['status']}, UTR: {s['utr_reference']})"
                    )
            return "\n".join(lines)

        elif intent == IntentType.PAYMENT_METHODS:
            pm_data = underlying_data.get("payment_methods_breakdown", {})
            methods_summary = pm_data.get("methods_summary", [])
            breakdown = pm_data.get("breakdown", [])

            if not methods_summary and not breakdown:
                return "No payment methods volume breakdown is currently available for your transactions."

            lines = ["Here is the payment methods breakdown for your collections:"]
            if methods_summary:
                for m in methods_summary:
                    lines.append(
                        f"• {m['payment_method']}: {m['success_count']} successful transactions totaling ₹{float(m['success_amount']):,.2f} "
                        f"({m['volume_percentage']}% of collections, {m['failed_count']} failed)."
                    )
            else:
                for b in breakdown:
                    lines.append(
                        f"• {b['payment_method']} ({b['status']}): {b['count']} transactions totaling ₹{float(b['total_amount']):,.2f}."
                    )
            return "\n".join(lines)

        elif intent == IntentType.TRANSACTIONS_SUMMARY:
            tx_data = underlying_data.get("transactions_summary", {})
            success_rate = tx_data.get("success_rate", 100.0)
            atv = tx_data.get("average_transaction_value", 0.0)
            pending_count = tx_data.get("pending_count", 0)
            recent_txs = tx_data.get("recent_transactions", [])

            lines = [
                f"Transaction Performance Summary:",
                f"• Overall Success Rate: {success_rate}%.",
                f"• Average Transaction Value (ATV): ₹{atv:,.2f}.",
                f"• Currently Pending Transactions: {pending_count}.",
            ]
            if recent_txs:
                lines.append("Recent Transactions:")
                for tx in recent_txs[:5]:
                    lines.append(
                        f"  - TXN {tx['transaction_id'][:8]}...: ₹{tx['amount']:,.2f} via {tx['payment_method']} (Status: {tx['status']})"
                    )
            return "\n".join(lines)

        else:  # GENERAL_OVERVIEW
            overview = underlying_data.get("overview", {})
            today_coll = overview.get("today_collections", "0.00")
            week_coll = overview.get("this_week_collections", "0.00")
            month_coll = overview.get("this_month_collections", "0.00")
            success_rate = overview.get("success_rate", 100.0)
            atv = overview.get("average_transaction_value", "0.00")
            overdue_count = underlying_data.get("overdue_invoices_count", 0)
            latest_settlement = underlying_data.get("latest_settlement")

            lines = [
                "Here is an overview of your merchant operations:",
                f"• Today's Collections: ₹{float(today_coll):,.2f}",
                f"• This Week's Collections: ₹{float(week_coll):,.2f}",
                f"• This Month's Collections: ₹{float(month_coll):,.2f}",
                f"• Average Transaction Value: ₹{float(atv):,.2f}",
                f"• Transaction Success Rate: {success_rate}%",
                f"• Overdue Invoices: {overdue_count} invoice(s) awaiting payment.",
            ]
            if latest_settlement:
                lines.append(
                    f"• Latest Settlement: ₹{latest_settlement['net_amount']:,.2f} on {latest_settlement['date']} (UTR: {latest_settlement['utr_reference']})."
                )
            return "\n".join(lines)
