# Anti-Structuring (Smurfing) Heuristic Specification

## Overview

In the Indian payment ecosystem, regulatory and compliance thresholds (such as reporting thresholds or simplified verification for low-value transactions below ₹2,000) can sometimes be targeted by actors attempting to fragment a large single-purchase transaction into multiple micro-transactions. This practice is formally known as **Structuring** or **Smurfing**.

PayFlow includes an **auditable, non-blocking compliance guardrail** within the **Splits Module** (`app/modules/splits`) that detects potential structuring patterns during payment plan creation and creates a real-time risk signal (`RiskSignal`) for compliance auditing and subsequent risk evaluation (Phase 19).

---

## Heuristic Criteria

A payment plan triggers the `STRUCTURING_PATTERN` risk signal if **all** of the following conditions are met:

| Parameter | Trigger Condition | Rationale |
| :--- | :--- | :--- |
| **Installment Count** | `> 3` installments | Legitimate milestone or deposit plans rarely fragment into 4+ equal near-₹2,000 tranches without date spread. |
| **Amount Band** | `₹1,800.00 <= amount < ₹2,000.00` for all installments | Target range just under the ₹2,000 verification/reporting boundary. |
| **Temporal Distribution** | `same calendar day` across all installments (`len(set(due_dates)) == 1`) | Absence of temporal distribution (weekly, monthly, milestone) suggests intentional division of a single lump sum rather than a legitimate installment schedule. |

---

## Behavior & Auditability

> [!IMPORTANT]
> **Non-Blocking Execution**: To preserve merchant conversion and avoid false-positive disruption to legitimate rush orders, the plan creation request is **NOT** rejected outright.
> Instead, the plan is created successfully, and a high-priority risk signal is persisted to `risk_signals`.

### Emitted Risk Signal Record

- **Table**: `risk_signals`
- **`rule_triggered`**: `"STRUCTURING_PATTERN"`
- **`risk_level`**: `RiskLevel.HIGH`
- **`risk_score`**: `80.00`
- **`action_taken`**: `RiskAction.FLAG_FOR_REVIEW`
- **`metadata_json`**:
  ```json
  {
    "signal_type": "STRUCTURING_PATTERN",
    "invoice_id": "<INVOICE_UUID>",
    "installment_count": 4,
    "amounts": ["1950.00", "1950.00", "1950.00", "1950.00"],
    "due_date": "2026-09-18",
    "rationale": "Detected >3 installments near ₹2,000 on the same date with no temporal distribution (anti-structuring guardrail triggered)."
  }
  ```

---

## Downstream Consumers

1. **Compliance Dashboard & Audit Logs**: Allows compliance officers and auditors to review flagged payment plans.
2. **Merchant Risk Profiling (Phase 19)**: Ingested into merchant risk scoring to adjust risk tiering and settlement rolling reserve requirements.
