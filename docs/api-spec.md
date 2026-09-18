# PayFlow API Specification

> [!IMPORTANT]
> **PROTOTYPE ARCHITECTURE & MOCK PROVIDER NOTICE:**
> The UPI QR code strings and payment links generated in PayFlow are strictly for triggering the **Mock Payment Provider** in this prototype sandbox. They do **NOT** connect directly to the NPCI, bank switches, or live UPI PSP rails. Any payment attempts initiated via these endpoints simulate mock transaction lifecycles and settlement routines.

---

## 1. Authentication & RBAC

- `POST /api/v1/auth/register`: Register user account.
- `POST /api/v1/auth/login`: Authenticate credentials (rate-limited via Redis).
- `POST /api/v1/auth/refresh`: Strictly rotated refresh tokens with replay protection.
- `POST /api/v1/auth/logout`: Revoke active session.

### Permission Codes
- `invoices:read`, `invoices:write`: View and generate invoices.
- `payments:read`, `payments:write`: Collect payment requests, generate QR codes, and issue payment links.
- `customers:read`, `customers:write`: Read and manage merchant customer directory.
- `staff:read`, `staff:write`: Staff account invites and role assignments.
- `merchants:read`, `merchants:write`: Organization profile updates and KYC submissions.

---

## 2. Invoices & Line Items

- `POST /api/v1/merchants/{id}/invoices`: Create draft invoice.
  - Server generates sequential, collision-safe invoice number (`INV-{merchant_short_code}-{year}-{sequence:05d}`).
- `POST /api/v1/invoices/{id}/items`: Add line item with quantity, unit price, tax rate, and discount.
  - Subtotal, tax total, discount total, and grand total are strictly calculated server-side.
- `DELETE /api/v1/invoice-items/{id}`: Delete line item and trigger automatic recalculation.
- `PATCH /api/v1/invoices/{id}`: Controlled status transitions (`DRAFT → SENT → CANCELLED`).

---

## 3. Payment Requests, UPI QR & Payment Links

### Payment Requests (Multi-Payment / Installment Path)
- **`POST /api/v1/invoices/{id}/payment-requests`**
  - **Permissions Required**: `payments:write`
  - **Request Body**:
    ```json
    {
      "amount": 500.00,
      "purpose": "Installment 1 of 2",
      "expires_at": "2026-09-25T12:00:00Z",
      "payer_vpa": "customer@okhdfcbank"
    }
    ```
  - **Business Rules**:
    - `amount` must be `≤ (invoice.total_amount - invoice.paid_amount)`.
    - Multiple payment requests can be created against the same invoice to support partial payments and installment plans.
  - **Response**: `201 Created` with `PaymentRequestResponse`.

---

### UPI Intent QR Code Generation
- **`POST /api/v1/payment-requests/{id}/qr`**
  - **Permissions Required**: `payments:write`
  - **Mock Mode Notice**: Generates UPI intent string formatted as:
    ```text
    pa=<vpa>&pn=<merchant>&am=<amount>&tr=<request_id>&cu=INR
    ```
  - **Image Rendering**: Uses Python `qrcode` library to render a high-resolution PNG image, saved locally to `/backend/uploads/qr/qr_{id}.png` and returned as a Base64 Data URI (`qr_data_url`) for immediate frontend display.
  - **Response**: `201 Created` with `UpiQrResponse`.

---

### Payment Links & Public Checkout Page
- **`POST /api/v1/payment-requests/{id}/link`**
  - **Permissions Required**: `payments:write`
  - **Request Body**:
    ```json
    {
      "expires_at": "2026-09-25T12:00:00Z",
      "max_uses": 1
    }
    ```
  - **Response**: `201 Created` with unique 8-character slug (e.g. `/pay/X7k9Lm2Q`).

- **`GET /pay/{slug}` (Public Checkout Endpoint)**
  - **Authentication**: None required (public customer endpoint).
  - **Tamper-Proof Guarantee**:
    - The payable amount is **strictly bound to the server-side `PaymentRequest`**.
    - No client-supplied query parameters, headers, or request bodies can alter or tamper with the required amount.
  - **Response**:
    ```json
    {
      "slug": "X7k9Lm2Q",
      "merchant_name": "Apex Electronics",
      "store_name": "Apex Flagship Store",
      "invoice_number": "INV-APEXEL-2026-00001",
      "amount": "500.00",
      "currency": "INR",
      "purpose": "Installment 1 of 2",
      "status": "ACTIVE",
      "expires_at": "2026-09-25T12:00:00Z",
      "upi_string": "pa=apex@icici&pn=Apex Electronics&am=500.00&tr=...&cu=INR",
      "is_mock_provider": true,
      "disclaimer": "Notice: Prototype Mock Mode. Triggering payment simulates mock settlement."
    }
    ```

---

## 4. Mock UPI Provider Simulator (`app/modules/mock_upi_provider`)

> [!WARNING]
> **SIMULATOR ONLY**: This module is a standalone simulator. Never refer to it as real UPI network connectivity in code, docs, or UI copy.

### Supported Simulation Scenarios
1. **`SUCCESS`**: Immediate successful transaction clearance with mock reference ID.
2. **`FAILED`**: Simulated failure/decline with failure reason (`PSP_DECLINED`, `INSUFFICIENT_FUNDS`).
3. **`PENDING`**: Processing delay simulation. Asynchronously triggers a Celery task that resolves to `SUCCESS` after a delay and emits an inbound webhook event (`payment.success`).
4. **`TIMEOUT`**: Acquiring gateway timeout. Asynchronously resolves to `FAILED` and emits an inbound webhook event.
5. **`DUPLICATE`**: Replay attack / identical parameter simulation. Links to existing transaction and creates a `DuplicateTransactionFlag` entry.
6. **`PARTIAL_PAYMENT`**: Partial clearance simulation (`settled_amount = amount * 0.50`).
7. **`REFUND`**: Payment reversal/refund execution simulation (`status = REFUNDED`).

### Probability Distribution
When `scenario` is omitted, the simulator selects from a weighted distribution:
- `SUCCESS`: **80%**
- `FAILED`: **6%**
- `PENDING`: **5%**
- `TIMEOUT`: **3%**
- `DUPLICATE`: **2%**
- `PARTIAL_PAYMENT`: **2%**
- `REFUND`: **2%**

### Simulation Endpoints
- **`POST /api/v1/payments/{id}/simulate`**
  - Dev/testing endpoint allowing explicit scenario override on an existing transaction.
  - Body: `{"scenario": "SUCCESS" | "FAILED" | "PENDING" | "TIMEOUT" | "DUPLICATE" | "PARTIAL_PAYMENT" | "REFUND"}`
- **`POST /api/v1/mock-upi/initiate`**
  - Direct simulation invocation without a pre-existing transaction.

---

## 5. Payments Module (Core Financial Ledger) (`app/modules/payments`)

### Finite State Machine
Transitions are strictly validated:
```text
CREATED → INITIATED → {SUCCESS | FAILED | PENDING | TIMEOUT | DUPLICATE}
                         ↓
                  REFUND_INITIATED → REFUND_PENDING → {REFUNDED | REFUND_FAILED}
```
- Disallowed transitions are rejected with `409 Conflict` (`INVALID_STATUS_TRANSITION`).
- Immutable status change records are appended to `transaction_status_history` for every transition.

### Derived Invoice Status
- On `SUCCESS`, parent invoice status (`PARTIALLY_PAID` vs `PAID`) is automatically derived from the sum of settled transactions:
  - If `sum(settled_amount) >= invoice.total_amount`: `invoice.status = PAID`
  - Else if `sum(settled_amount) > 0`: `invoice.status = PARTIALLY_PAID`
  - Invoice status is never set directly for these two states.

### Core Endpoints

#### `POST /api/v1/payments/initiate` (or `/payments/initiate`)
- **Header**: `Idempotency-Key` (required string/UUID).
- **Idempotency Guarantee**: If a transaction with the given key already exists, returns the existing record immediately (`200 OK`) without re-initiating.
- **New Transaction Execution**: If new (`201 Created`), wraps creation in an atomic Postgres transaction:
  1. Creates record with status `CREATED` and writes status history.
  2. Transitions to `INITIATED` and writes status history.
  3. Executes `MockUPIProvider.initiate_payment`.
  4. Transitions `INITIATED` → outcome status (`SUCCESS`, `FAILED`, `PENDING`, `TIMEOUT`, `DUPLICATE`).
  5. If `SUCCESS`, recomputes invoice status.
  6. Commits transaction atomically.

#### `GET /api/v1/payments/{id}` (or `/payments/{id}`)
- Returns full transaction details including chronological `status_history`.

#### `GET /api/v1/merchants/{id}/transactions` (or `/merchants/{id}/transactions`)
- **Authentication**: Bearer JWT with `payments:read` permission.
- **Query Filters**:
  - `status`: Filter by `TransactionStatus`.
  - `method`: Filter by `PaymentMethod`.
  - `from_date` / `to_date`: ISO datetime range.
  - `search`: Substring search matching `provider_ref_id`, `invoice_number`, or `customer.name`.
  - `page` / `page_size`: Standard pagination parameters.

---

## 6. Splits & Payment Plans Module (`app/modules/splits`)

### Overview
Allows invoices to be broken into structured installments (`DEPOSIT`, `INSTALLMENT`, `MILESTONE`, `CUSTOM_SPLIT`).

### Endpoints

#### `POST /api/v1/invoices/{id}/payment-plans` (or `/invoices/{id}/payment-plans`)
- **Authentication**: Bearer JWT with `invoices:write` permission.
- **Reconciliation Rule**: The sum of installment amounts must reconcile exactly to:
  - `invoice.total_amount - invoice.paid_amount` for `plan_type == DEPOSIT`.
  - `invoice.total_amount` for all other plan types.
  - Mismatches are rejected with `400 BAD_REQUEST` (`PLAN_RECONCILIATION_FAILED`).
- **Anti-Structuring Heuristic Guardrail**:
  - If a plan is submitted with >3 installments in the narrow band ₹1,800.00–₹1,999.99 all on the same calendar day, the plan is **not** blocked, but an auditable `RiskSignal` is emitted with `rule_triggered="STRUCTURING_PATTERN"`. Full details in [docs/anti-structuring.md](file:///Users/shubhamsharma/Desktop/transaction/docs/anti-structuring.md).

#### `GET /api/v1/invoices/{id}/payment-plans` (or `/invoices/{id}/payment-plans`)
- **Authentication**: Bearer JWT with `invoices:read` permission.
- Returns list of payment plans and each installment's status (`PENDING`, `PARTIALLY_PAID`, `PAID`, `OVERDUE`, `CANCELLED`).

#### `POST /api/v1/payment-plans/{id}/installments/{installment_id}/initiate` (or `/payment-plans/...`)
- **Header**: `Idempotency-Key` (required string/UUID).
- Reuses the core ledger payment flow (`PaymentService.initiate_payment`), linking the resulting `PaymentTransaction` to `installment_id`.
- On `SUCCESS`, automatically marks the installment `PAID`, checks if all installments are settled to transition plan status to `COMPLETED`, and derives invoice aggregate status (`PARTIALLY_PAID` vs `PAID`).

---

## 7. Webhooks Module (`app/modules/webhooks`)

### Overview
Manages secure asynchronous inbound event ingestion from the UPI provider simulator and outbound dispatch to merchant-configured listener endpoints with HMAC signing, replay protection, and resilient Celery-driven retries.

### Inbound Webhooks (From Mock Provider)

#### `POST /webhooks/upi-mock/inbound` (or `/api/v1/webhooks/upi-mock/inbound`)
- **Signature Verification**:
  - Requires `X-Webhook-Signature` header containing the HMAC-SHA256 hex digest of the raw request payload computed against the shared secret (`settings.WEBHOOK_SECRET`).
  - Missing or mismatched signature returns `401 Unauthorized`.
- **Distributed Concurrency Lock**:
  - Uses Redis `SETNX` on `payflow:lock:webhook:{provider_event_id}` with a 30-second TTL.
  - If a concurrent duplicate delivery is in progress, immediately aborts with `409 Conflict` (`CONCURRENT_WEBHOOK_DELIVERY`).
- **Replay Protection**:
  - `provider_event_id` is enforced unique in the `webhook_events_inbound` ledger table.
  - Subsequent duplicate deliveries are safely ignored with `{"status": "ignored", "message": "Duplicate event already processed (replay ignored)"}`.
- **State Machine Updates**:
  - On first receipt, matches the target transaction by `transaction_id`, `provider_ref_id`, or `idempotency_key`.
  - Transitions `payment_transactions` status via `PaymentService.transition_status` and records an immutable transition entry in `transaction_status_history`.

### Outbound Webhooks (To Merchant Endpoints)

#### `POST /api/v1/merchants/{id}/webhook-subscriptions` (or `/merchants/{id}/webhook-subscriptions`)
- **Authentication**: Bearer JWT with `staff:write` (Owner / Manager) permission.
- **Request Payload**:
  - `target_url` (valid HTTPS URL)
  - `secret_key` (optional; auto-generates 48-char hex secret if omitted)
  - `subscribed_events`: Array of event pattern strings (e.g. `["payment.success", "payment.failed", "invoice.paid", "refund.*"]` or `["*"]`).

#### `GET /api/v1/merchants/{id}/webhook-subscriptions` (or `/merchants/{id}/webhook-subscriptions`)
- **Authentication**: Bearer JWT with `staff:read` (Owner / Manager / Auditor) permission.
- **Returns**: List of configured webhook subscriptions.

#### `POST /api/v1/webhook-subscriptions/{id}/test` (or `/webhook-subscriptions/{id}/test`)
- Sends a synthetic `test.ping` event to the merchant endpoint to verify connectivity and signature verification setup.

#### Automatic Event Dispatch & Retry Policy
- **Trigger Events**:
  - `payment.success`: Dispatched upon successful transaction capture.
  - `payment.failed`: Dispatched upon transaction failure.
  - `invoice.paid`: Dispatched when an invoice's aggregate collected balance satisfies `grand_total`.
  - `refund.*`: Dispatched upon refund initiation, completion, or failure.
- **Payload Signing**:
  - Every outbound HTTP POST includes:
    - `X-PayFlow-Signature`: HMAC-SHA256 hex digest of the payload computed with the subscription's `secret_key`.
    - `X-PayFlow-Event`: Name of the triggering event (e.g. `payment.success`).
    - `X-PayFlow-Delivery`: UUID of the delivery record in `webhook_deliveries`.
- **Delivery Ledger & Retry Backoff**:
  - Each delivery attempt records `attempt_count`, `response_status_code`, and `response_body` in `webhook_deliveries`.
  - Failures (HTTP 4xx/5xx or network exceptions) retry with exponential backoff: $2^{\text{attempt}}$ seconds.
  - **Max Retries**: Capped at 3 attempts. When 3 attempts are exhausted, the delivery status transitions permanently to `FAILED` and is never retried again.

---

## 8. Reconciliation Module (`app/modules/reconciliation`)

### Overview
Automated cross-referencing ledger and settlement engine. Compares captured `SUCCESS` transactions against actual banking/provider payouts recorded in `settlement_line_items` to ensure financial integrity, detect variances, and detect missing payouts.

### Illustrative Mock MDR Notice
> [!NOTE]
> The MDR (Merchant Discount Rate) calculations performed across this module (default 1.5% / `0.015`) are strictly for mock prototype simulation and illustrative settlement cross-referencing. They do **not** reflect real bank interchange or NPCI fee schedules.

### Reconciliation Matching Rules & Thresholds
- **Expected Settlement Amount**:
  $$\text{Expected Net} = \text{Transaction Amount} \times (1 - \text{MDR Rate})$$
- **MATCHED**:
  - A `SettlementLineItem` exists for the transaction.
  - Variance $|\text{Expected} - \text{Actual}| \le \text{Tolerance}$ (default tolerance: ₹0.05).
- **MANUAL_REVIEW**:
  - A `SettlementLineItem` exists, but variance $|\text{Expected} - \text{Actual}| > \text{Tolerance}$.
  - Or a transaction is awaiting settlement within the allowable grace period.
- **UNMATCHED**:
  - No `SettlementLineItem` exists for a `SUCCESS` transaction whose age exceeds the grace period (default: 24 hours).

### Endpoints

#### `POST /api/v1/merchants/{id}/reconciliation/run` (or `/merchants/{id}/reconciliation/run`)
- **Authentication**: Bearer JWT with `settlements:write` (Owner) permission.
- **Optional Request Payload (`ReconciliationRunRequest`)**:
  - `period_start` (ISO datetime; defaults to last 24h)
  - `period_end` (ISO datetime; defaults to current time)
  - `mdr_rate` (Decimal, e.g. `0.015` for 1.5%)
  - `tolerance` (Decimal in INR; defaults to `0.05`)
  - `grace_period_hours` (Integer hours; defaults to `24`)
- **Returns (`ReconciliationBatchResponse`)**:
  - `id`, `merchant_id`, `batch_date`, `period_start`, `period_end`, `mdr_rate`, `status` (`MATCHED`, `DISCREPANCIES_FOUND`, `COMPLETED`), `total_records`, `matched_records`, `mismatched_records`, `discrepancy_count`.
- **Audit Logging**: Generates an immutable audit trail entry in `audit_logs` under entity `reconciliation_batches`.

#### `GET /api/v1/merchants/{id}/reconciliation/batches` (or `/merchants/{id}/reconciliation/batches`)
- **Authentication**: Bearer JWT with `settlements:read` (Owner, Manager, Auditor) permission.
- **Query Parameters**:
  - `page` (integer, default 1)
  - `page_size` (integer, default 20)
  - `from_date` / `to_date` (date `YYYY-MM-DD`)
  - `status` (`ReconciliationStatus` enum filter)
- **Returns**: Paginated list of reconciliation batches.

#### `GET /api/v1/reconciliation/batches/{id}/entries` (or `/reconciliation/batches/{id}/entries`)
- **Authentication**: Bearer JWT with `settlements:read` permission on the batch's merchant.
- **Query Parameters**:
  - `page` (integer, default 1)
  - `page_size` (integer, default 20)
  - `match_status`: Filter by `MATCHED`, `UNMATCHED`, `MANUAL_REVIEW`.
- **Returns**: Paginated list of transaction reconciliation entries with `expected_amount`, `actual_amount`, `match_status`, and discrepancy notes.

### Scheduled Nightly Beat Job
- Configured in `celery_app.conf.beat_schedule`:
  - **Task**: `reconciliation.run_nightly_reconciliation`
  - **Schedule**: Nightly at 01:00 UTC (`crontab(hour=1, minute=0)`).
  - Iterates over all active merchants, reconciles the previous calendar day's window `[00:00:00 UTC, 23:59:59 UTC]`, and records batches.

---

## 8. Duplicate Detection & Flag Resolution

Automated detection and operational resolution of suspected duplicate payments across invoices, customers, and provider duplicate states.

### Detection Mechanism & Celery Task
- **Trigger**: Every time a transaction enters `SUCCESS`, `PENDING`, or a provider-reported `DUPLICATE` state, the background task `duplicate_detection.detect_duplicate_transaction(transaction_id)` is dispatched.
- **Rules Evaluated**:
  1. **Provider-Reported DUPLICATE**: Transaction received a DUPLICATE response code or mock scenario from the payment switch / provider simulator.
  2. **Same Invoice Burst**: Another transaction on the same invoice within a 15-minute window with matching amount and payment method.
  3. **Same Customer Duplicate**: Another transaction for the same customer (across invoices) within a 15-minute window with matching amount and payment method.
- **Deduplication**: Flagging avoids duplicate rows for the same transaction pair (`original_transaction_id`, `duplicate_transaction_id`).
- **Audit Logging**: Flag creation and resolution operations are recorded in `audit_logs`.

### Endpoints

#### `GET /api/v1/merchants/{id}/transactions?flag=duplicate` (or `/merchants/{id}/transactions?flag=duplicate`)
- **Authentication**: Bearer JWT with `payments:read`.
- **Query Parameter**:
  - `flag=duplicate`: Filters the transaction list to return only transactions that have been flagged as duplicate.
- **Returns**: Paginated list of `PaymentTransactionResponse` records.

#### `PATCH /duplicate-flags/{id}/resolve` (or `/api/v1/duplicate-flags/{id}/resolve`)
- **Authentication**: Bearer JWT with `payments:write` (Owner, Manager).
- **Request Body (`ResolveDuplicateFlagRequest`)**:
  ```json
  {
    "reason": "Customer confirmed intentional multiple installments.",
    "resolved_by": "optional-user-uuid"
  }
  ```
- **Behavior**: Sets flag status to `RESOLVED`, records `resolved_by`, `resolved_at`, and `resolution_reason`, and logs an audit update.
- **Returns**: `200 OK` with `DuplicateFlagResponse`.

#### `GET /api/v1/merchants/{id}/duplicate-flags` (or `/merchants/{id}/duplicate-flags`)
- **Authentication**: Bearer JWT with `payments:read`.
- **Query Parameters**:
  - `status`: Optional filter (`SUSPECTED`, `CONFIRMED_DUPLICATE`, `FALSE_POSITIVE`, `RESOLVED`).
  - `page`, `page_size`: Pagination parameters.
- **Returns**: Paginated list of `DuplicateFlagResponse` items.

#### `GET /api/v1/merchants/{id}/duplicate-flags/summary` (or `/merchants/{id}/duplicate-flags/summary`)
- **Authentication**: Bearer JWT with `payments:read`.
- **Purpose**: Surfaces the count of active unresolved duplicate flags for settlement/analytics overviews.
- **Returns**:
  ```json

---

## 13. Risk Signals & Fraud Auditing

For full algorithmic explanations and compliance rationale, see [docs/risk-rules.md](file:///Users/shubhamsharma/Desktop/transaction/docs/risk-rules.md).

#### `GET /api/v1/merchants/{id}/risk/signals` (or `/merchants/{id}/risk/signals`)
- **Authentication**: Bearer JWT (`payments:read` or `merchants:read`).
- **Query Parameters**:
  - `severity`: Filter by `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  - `reviewed`: Filter by boolean (`true` or `false`).
  - `rule_triggered`: Filter by `VELOCITY_SPIKE`, `ODD_HOUR`, `STRUCTURING_PATTERN`.
  - `page`, `page_size`: Pagination parameters.
- **Returns**: Paginated list of `RiskSignalResponse` records.

#### `PATCH /api/v1/risk/signals/{id}/review` (or `/risk/signals/{id}/review`)
- **Authentication**: Bearer JWT with `refunds:approve` / risk management privilege (Manager, Owner).
- **Request Body (`ReviewRiskSignalRequest`)**:
  ```json
  {
    "resolution_note": "Investigated customer activity; verified genuine high-value order.",
    "action_taken": "ALLOW"
  }
  ```
- **Behavior**: Sets `is_reviewed = true`, `reviewed_by = current_user.id`, `reviewed_at = utcnow()`, `resolution_note`, updates `action_taken`, and records an immutable audit log entry.
- **Returns**: `200 OK` with updated `RiskSignalResponse`.

#### `GET /api/v1/risk/rules` (or `/risk/rules`)
- **Authentication**: Public / Read documentation endpoint.
- **Returns**: Explanations of all deterministic rules, threshold parameters, formulas, and omission notices for auditors.

---

## 14. AI Assistant Read-Only Financial Q&A

#### `POST /api/v1/merchants/{id}/ai-assistant/query` (or `/merchants/{id}/ai-assistant/query`)
- **Authentication**: Bearer JWT (`payments:read`).
- **Read-Only Scope**: Strictly restricted to read-only queries over the merchant's own analytics, transaction, settlement, and invoice data. **Cannot execute mutations, initiate refunds, or alter payments**.
- **Request Body (`AIAssistantQueryRequest`)**:
  ```json
  {
    "question": "Which customers have overdue invoices?"
  }
  ```
- **Response (`AIAssistantQueryResponse`)**:
  ```json
  {
    "merchant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "question": "Which customers have overdue invoices?",
    "intent": "OVERDUE_INVOICES",
    "answer": "You currently have 1 overdue invoice totaling ₹3,500.00.\n• INV-AI-2026-0001: Customer Ramesh Sharma owes ₹3,500.00, which was due on 2026-09-13.",
    "sources_cited": [
      {
        "entity_type": "invoice",
        "id": "7b79a5fa-4404-453a-9669-930335eb24f2",
        "reference": "INV-AI-2026-0001",
        "details": {
          "customer": "Ramesh Sharma",
          "balance_due": 3500.0,
          "due_date": "2026-09-13"
        }
      }
    ],
    "underlying_data": {
      "merchant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "intent": "OVERDUE_INVOICES",
      "overdue_invoices": {
        "count": 1,
        "total_overdue_amount": 3500.0,
        "items": [...]
      }
    },
    "model_used": "claude-3-5-sonnet-20241022",
    "created_at": "2026-09-18T11:58:14.650163Z"
  }
  ```
- **System Prompt & Anti-Hallucination Guarantees**:
  - The model is constrained by a fixed system prompt restricting it to explaining provided data only.
  - Numbers, amounts, and dates are strictly retrieved from real database rows prior to prompt assembly.
  - In offline / test execution where `ANTHROPIC_API_KEY` is not set, a deterministic grounded synthesizer generates verified responses using the identical citation model.



