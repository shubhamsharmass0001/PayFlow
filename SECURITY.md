# Security Policy & Architecture Disclosure

**Project:** PayFlow Payment Orchestration & Merchant Billing Platform  
**Version:** Prototype / Development Build  

---

## 1. Prototype Notice & Mock UPI Isolation

**PayFlow is an engineering prototype and reference architecture.** 

- **Not Connected to Live UPI**: This system is **not** connected to the National Payments Corporation of India (NPCI) production switch, live bank Payment Service Providers (PSPs), or any real money settlement rails.
- **Mock UPI Provider**: All UPI VPA lookups, intent QR code generation, transaction authorizations, and webhook callbacks are executed through an internal simulation engine (`MockUPIProvider`). 
- **No Real Currency Transferred**: Account balances, VPAs, transaction reference numbers, UTR numbers, and bank settlement credits are synthetic test artifacts generated strictly for software validation and demonstration.

---

## 2. Legitimate Split-Payment Use Cases & Anti-Structuring Controls

PayFlow supports multi-payment and installment workflows, but strictly distinguishes legitimate business billing from illegal transaction structuring:

### 2.1 Legitimate Business Use Cases
The split-payment capabilities in PayFlow are designed and restricted to valid commercial payment arrangements:
- **Advance Booking & Deposits**: Paying a 20% upfront deposit to confirm a purchase, followed by the remaining balance upon delivery.
- **Scheduled Installment Plans**: Splitting a high-value purchase (e.g., electronics, furniture, educational courses) across 3, 6, or 12 pre-defined installment dates.
- **Project Delivery Milestones**: B2B consulting or development invoices where payments are unlocked upon agreed milestone sign-offs.

### 2.2 Anti-Structuring & Smurfing Detection
To protect against financial structuring (splitting high-value transactions into smaller tranches to evade mandatory regulatory reporting thresholds such as the ₹1,00,000 threshold under Indian AML regulations):
- **Automated Structuring Heuristics**: The system actively monitors payment velocity, payer VPA repetition, and amounts clustered just below regulatory thresholds (e.g., multiple ₹99,000 payments).
- **Risk Escalation**: Detected structuring patterns automatically generate `HIGH` severity `RiskSignal` entries, block instant approval, and route transactions into a mandatory compliance review queue.
- **Auditor Access**: Auditors and compliance staff have dedicated, tamper-proof read-only interfaces to inspect transaction status histories, client IP addresses, and behavioral metadata.

---

## 3. Core Security & Defensive Controls

PayFlow incorporates end-to-end defenses throughout the stack:

| Defensive Layer | Implementation Details |
| :--- | :--- |
| **Server-Locked Amounts** | Amounts are computed and verified entirely on the server based on database records (`invoices`, `payment_requests`). Client payloads, query params, or QR string modifications cannot alter the payable amount. |
| **Idempotency Enforcement** | All mutating and money-moving endpoints require and enforce the `Idempotency-Key` HTTP header. Replayed keys return the cached transaction response without double-processing. |
| **Public Rate Limiting** | Public endpoints—including `GET /pay/{slug}` (60 req/min) and `POST /webhooks/upi-mock/inbound` (120 req/min)—are protected by Redis token bucket rate limiting to prevent enumeration and denial-of-service. |
| **HMAC-SHA256 Webhooks** | Inbound and outbound webhook callbacks verify cryptographic HMAC-SHA256 signatures via the `X-Webhook-Signature` header to guarantee authenticity and prevent replay attacks. |
| **Mobile Credential Storage** | The Flutter mobile client stores JWT access and refresh tokens exclusively in `FlutterSecureStorage` (iOS Keychain / Android EncryptedSharedPreferences). Plain `SharedPreferences` is strictly prohibited. |
| **Role-Based Access Control** | Fine-grained RBAC (`Owner`, `Manager`, `Cashier`, `Auditor`) gates sensitive actions such as staff management, refund approvals, and audit log inspection. |
| **Immutable Audit Logging** | Platform state mutations and refund events record immutable before/after JSON diffs, actor IDs, client IP addresses, and UTC timestamps. |

---

## 4. Reporting Security Vulnerabilities

If you discover a security issue or architectural defect within this codebase, please contact the development team or file an issue flagged as `security`. Do not publicly disclose vulnerabilities until they have been addressed.
