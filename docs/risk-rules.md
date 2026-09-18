# Risk Rules & Fraud Detection Specification

## Overview

The Risk Module (`app/modules/risk`) provides an auditable, explainable, and non-blocking risk signal evaluation engine. It runs asynchronously via Celery (`evaluate_risk_rules`) after every transaction or refund lifecycle event, evaluating transactions against explicit heuristic rules to detect abnormal velocity, odd operating hours, and structuring (smurfing) patterns.

Because this module exists specifically for regulatory compliance, anti-money laundering (AML), and misuse mitigation, **every rule is deterministic and fully auditable** rather than a black-box machine learning model.

---

## 1. Rule Definitions & Logic

### 1.1 `VELOCITY_SPIKE`
- **Objective**: Detect sudden, anomalous surges in transaction frequency or transaction value that exceed a merchant's established historical baseline.
- **Evaluation Windows**:
  - **Immediate Window**: Rolling 60 minutes prior to and including current event.
  - **Baseline Window**: Trailing 7 days (168 hours) of merchant transaction history.
- **Trigger Conditions**:
  A signal is raised if either of the following thresholds is exceeded:
  1. **Volume Spike (Transaction Count)**:
     $$\text{Hourly Count} \ge 5 \quad \text{AND} \quad \text{Hourly Count} \ge 3.0 \times \text{Baseline Trailing Hourly Average}$$
  2. **Value Spike (Gross Amount)**:
     $$\text{Hourly Volume} \ge ₹10,000.00 \quad \text{AND} \quad \text{Hourly Volume} \ge 5.0 \times \text{Baseline Trailing Hourly Volume}$$
- **Severity & Risk Scoring**:
  - **`CRITICAL`** ($\text{Risk Score} = 90.0$): Hourly count $\ge 5\times$ baseline OR hourly amount $\ge ₹50,000.00$.
  - **`HIGH`** ($\text{Risk Score} = 85.0$): Standard trigger condition satisfied.
- **Action Taken**: `FLAG_FOR_REVIEW`.
- **Explainable Metadata Captured**:
  - `hourly_count`, `baseline_hourly_count_avg`, `count_ratio`
  - `hourly_amount`, `baseline_hourly_amount_avg`, `amount_ratio`
  - `rationale` string detailing the exact arithmetic breach.

---

### 1.2 `ODD_HOUR`
- **Objective**: Identify transactions taking place during unusual, off-peak hours that deviate from the merchant's normal trading profile.
- **Time Zone Standard**: Indian Standard Time (`Asia/Kolkata`, UTC+05:30).
- **Evaluation Window**:
  - Nocturnal hours: **01:00 IST to 04:59 IST** (inclusive).
- **Trigger Conditions**:
  1. Current transaction was initiated between `01:00:00` and `04:59:59` IST.
  2. The merchant's historical transaction profile in that same 01:00–04:59 IST window accounts for **less than 5.0%** of their total transactions (or fewer than 2 total night transactions).
- **Severity & Risk Scoring**:
  - **`MEDIUM`** ($\text{Risk Score} = 60.0$).
- **Action Taken**: `FLAG_FOR_REVIEW`.
- **Explainable Metadata Captured**:
  - `hour_ist`: Local hour of transaction (1 to 4).
  - `historical_night_ratio`: Historical fraction of transactions processed at night.
  - `historical_night_count`: Historical count of night transactions.
  - `rationale`: Human-readable explanation of why this time is abnormal for this merchant.

---

### 1.3 `STRUCTURING_PATTERN`
- **Objective**: Catch smurfing or structuring attempts designed to stay just below Indian statutory thresholds or simplified verification tiers (specifically the ₹2,000 threshold).
- **Monitored Band**: $₹1,800.00 \le \text{amount} < ₹2,000.00$.
- **Trigger Conditions**:
  1. **Phase 9 Split-Plan Structuring**:
     - An invoice installment schedule containing $> 3$ installments, all within $₹1,800.00 \le \text{amount} < ₹2,000.00$, sharing the exact same calendar due date (no temporal separation).
  2. **Post-Transaction Clustering (Phase 19)**:
     - **$\ge 3$ transactions** in the $₹1,800.00$ to $₹1,999.99$ band within a **rolling 24-hour window**.
     - Directed against the **same customer** OR the **same invoice**.
     - Occurring outside a documented, active installment payment plan with distinct milestone dates.
- **Severity & Risk Scoring**:
  - **`CRITICAL`** ($\text{Risk Score} = 90.0$): $\ge 5$ qualifying transactions within 24 hours.
  - **`HIGH`** ($\text{Risk Score} = 80.0$): 3 or 4 qualifying transactions within 24 hours.
- **Action Taken**: `FLAG_FOR_REVIEW`.
- **Explainable Metadata Captured**:
  - `pattern_type`: `"REPEATED_NEAR_THRESHOLD_TRANSACTIONS"`
  - `customer_id` or `invoice_id`
  - `qualifying_tx_count`: Total transactions in the ₹1,800–₹1,999.99 band.
  - `total_volume_in_band`: Sum of amounts.
  - `transaction_ids`: List of involved transaction UUIDs.

---

### 1.4 `GEO_MISMATCH` (Explicitly Omitted)
- **Status**: **OMITTED BY DESIGN**.
- **Rationale**:
  In accordance with development specifications ("if you're capturing any location signal — otherwise omit rather than fake it"), `GEO_MISMATCH` is **not** implemented.
  - UPI intent QR codes, virtual payment addresses (VPAs), and bank switch webhook notifications in this architecture do not capture device GPS coordinates or consumer IP geolocations.
  - Generating fake GPS coordinates or synthetic geolocations would undermine the integrity of the audit logs and give a false sense of compliance.
  - Should mobile device telemetry or POS hardware location be integrated in future phases, a geofence rule can be introduced without disrupting existing rules.

---

## 2. API Surface

### 2.1 List Merchant Risk Signals
- **`GET /api/v1/merchants/{id}/risk/signals`** (also available at `/merchants/{id}/risk/signals`)
- **Query Parameters**:
  - `severity`: Filter by `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
  - `reviewed`: Filter by boolean (`true` or `false`).
  - `rule_triggered`: Filter by rule name (`VELOCITY_SPIKE`, `ODD_HOUR`, `STRUCTURING_PATTERN`).
  - `page`: Page index (default: 1).
  - `page_size`: Items per page (default: 20, max: 100).
- **RBAC**: Requires authenticated merchant staff (`payments:read` or `merchants:read`).

### 2.2 Review and Resolve Risk Signal
- **`PATCH /api/v1/risk/signals/{id}/review`** (also available at `/risk/signals/{id}/review`)
- **RBAC**: Restricted to **Manager** or **Owner** (`refunds:approve` / risk management privilege).
- **Request Body**:
  ```json
  {
    "resolution_note": "Verified customer identity and confirmed legitimate bulk inventory purchase.",
    "action_taken": "ALLOW"
  }
  ```
- **Behavior**:
  - Updates `is_reviewed = true`, `reviewed_by = current_user.id`, `reviewed_at = utcnow()`, and `resolution_note`.
  - Writes an immutable entry to `audit_logs` capturing the reviewer, prior state, resolution note, and action taken.

### 2.3 Rule Explanations & Auditability
- **`GET /api/v1/risk/rules`**
- Returns the complete dictionary of auditable rule definitions, trigger formulas, thresholds, and data inputs for automated compliance auditing.

---

## 3. Event Triggers & Notification Dispatch

When a transaction or refund event occurs:
1. `evaluate_risk_rules.delay(transaction_id, refund_id)` is dispatched asynchronously.
2. The Celery worker instantiates the database session and runs `evaluate_velocity_spike`, `evaluate_odd_hour`, and `evaluate_structuring_pattern`.
3. If any rule triggers, a record is written to `risk_signals` with deduplication against `(transaction_id, rule_triggered)`.
4. High and critical severity signals immediately dispatch an operational notification (`send_notification`) to the merchant's security and owner channels.
