# PayFlow Database Schema Specification

This document details the complete database schema for the PayFlow UPI & payments orchestration platform.

## Design Principles

1. **UUID Primary Keys**: Every table uses a PostgreSQL UUID primary key generated using `uuid.uuid4`.
2. **Timestamps**: `created_at` and `updated_at` timestamps with UTC timezone (`DateTime(timezone=True)`) are present on all stateful tables.
3. **Soft-Delete Architecture**: Core business domain entities (`users`, `merchants`, `stores`, `customers`, `invoices`, `invoice_items`, `payment_links`, `payment_plans`) incorporate `deleted_at` timestamps.
4. **Referential Integrity & Financial Safety**:
   - `ON DELETE RESTRICT` is enforced across financial ledgers, payments, refunds, settlements, customers, and invoices to protect audit trails and accounting integrity.
   - `ON DELETE CASCADE` is strictly reserved for dependent child items whose lifecycle is tied directly to their parent container (e.g. `invoice_items`, `payment_plan_installments`, `settlement_line_items`, `webhook_deliveries`, `role_permissions`).
5. **High-Performance Indexing**:
   - `merchant_id` is indexed across every table where it appears for multi-tenant isolation.
   - `idempotency_key` is enforced with a unique index on `payment_transactions`.
   - `status` is indexed on high-throughput query targets (`invoices`, `payment_transactions`, `payment_requests`).
   - `phone` is indexed on `customers` for fast checkout lookup.

---

## Entity Relationship Overview

```
                      +-------------------+
                      |      merchants    |
                      +---------+---------+
                                |
       +------------------------+------------------------+------------------------+
       |                        |                        |                        |
       v                        v                        v                        v
+--------------+         +--------------+         +--------------+         +--------------+
|    stores    |         |  customers   |         |   invoices   |         | payment_links|
+--------------+         +--------------+         +-------+------+         +-------+------+
                                                          |                        |
                                            +-------------+                        |
                                            v                                      v
                                     +--------------+                       +--------------+
                                     |invoice_items |                       | payment_plans|
                                     +--------------+                       +-------+------+
                                                                                    |
                                                                                    v
                                                                   +------------------------------+
                                                                   |  payment_plan_installments   |
                                                                   +--------------+---------------+
                                                                                  |
       +--------------------------------------------------------------------------+
       v
+-------------------------------+       +-------------------------------+
|     payment_transactions      +------>+          refunds              |
+---------------+---------------+       +-------------------------------+
                |
                +---------------------->+-------------------------------+
                |                       |          settlements          |
                |                       +---------------+---------------+
                |                                       |
                |                                       v
                |                       +-------------------------------+
                |                       |     settlement_line_items     |
                |                       +-------------------------------+
                v
+-------------------------------+
|  transaction_status_history   |
+-------------------------------+
```

---

## Tables and Schema Definitions

### 1. Authentication & Identity (`app/modules/auth`)

#### `users`
Represents administrative, merchant, and operator user accounts.
- **Columns**:
  - `id` (`UUID`, PK): Unique user identifier.
  - `email` (`VARCHAR(255)`, UNIQUE, Indexed, NOT NULL): User email address used for authentication.
  - `hashed_password` (`VARCHAR(255)`, NOT NULL): Bcrypt-hashed password.
  - `full_name` (`VARCHAR(255)`, NOT NULL): Full legal name.
  - `phone` (`VARCHAR(20)`, Indexed, Nullable): Mobile contact number.
  - `is_active` (`BOOLEAN`, NOT NULL, Default: `TRUE`): Account operational status.
  - `is_superuser` (`BOOLEAN`, NOT NULL, Default: `FALSE`): Global platform superuser flag.
  - `created_at` (`TIMESTAMPTZ`, NOT NULL): Record creation time.
  - `updated_at` (`TIMESTAMPTZ`, NOT NULL): Record update time.
  - `deleted_at` (`TIMESTAMPTZ`, Nullable): Soft-delete timestamp.

#### `refresh_tokens`
Stores active session refresh tokens.
- **Columns**:
  - `id` (`UUID`, PK): Unique token record identifier.
  - `user_id` (`UUID`, FK -> `users.id`, ON DELETE CASCADE, Indexed, NOT NULL): Owner user account.
  - `token_hash` (`VARCHAR(255)`, UNIQUE, Indexed, NOT NULL): SHA256 hash of the issued refresh token.
  - `expires_at` (`TIMESTAMPTZ`, NOT NULL): Token expiration deadline.
  - `is_revoked` (`BOOLEAN`, NOT NULL, Default: `FALSE`): Revocation flag.
  - `created_at` (`TIMESTAMPTZ`, NOT NULL): Token issuance timestamp.

---

### 2. Role-Based Access Control (`app/modules/rbac`)

#### `roles`
Defines operational roles available in the platform.
- **Columns**:
  - `id` (`UUID`, PK): Role identifier.
  - `name` (`VARCHAR(50)`, UNIQUE, NOT NULL): Unique role name (e.g., `MERCHANT_ADMIN`, `CASHIER`).
  - `description` (`VARCHAR(255)`, Nullable): Human-readable role description.
  - `is_system_role` (`BOOLEAN`, NOT NULL, Default: `FALSE`): Indicates immutable system roles.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `permissions`
Granular functional permission definitions.
- **Columns**:
  - `id` (`UUID`, PK): Permission identifier.
  - `code` (`VARCHAR(100)`, UNIQUE, Indexed, NOT NULL): Permission code (e.g., `invoices:create`, `settlements:approve`).
  - `name` (`VARCHAR(100)`, NOT NULL): Short name.
  - `description` (`VARCHAR(255)`, Nullable): Scope description.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `role_permissions`
Many-to-many junction between roles and permissions.
- **Columns**:
  - `role_id` (`UUID`, PK, FK -> `roles.id`, ON DELETE CASCADE): Target role.
  - `permission_id` (`UUID`, PK, FK -> `permissions.id`, ON DELETE CASCADE): Target permission.
  - `created_at` (`TIMESTAMPTZ`, NOT NULL).

#### `user_roles`
Merchant-scoped user role bindings.
- **Columns**:
  - `user_id` (`UUID`, PK, FK -> `users.id`, ON DELETE CASCADE): Assigned user.
  - `role_id` (`UUID`, PK, FK -> `roles.id`, ON DELETE CASCADE): Assigned role.
  - `merchant_id` (`UUID`, PK, FK -> `merchants.id`, ON DELETE CASCADE, Indexed): Scope merchant.
  - `created_at` (`TIMESTAMPTZ`, NOT NULL).

---

### 3. Merchants & Store Management (`app/modules/merchants`, `app/modules/stores`)

#### `merchants`
Master merchant entity profile.
- **Columns**:
  - `id` (`UUID`, PK): Merchant identifier.
  - `business_name` (`VARCHAR(255)`, NOT NULL): Brand/trade name.
  - `legal_name` (`VARCHAR(255)`, NOT NULL): Registered legal corporate name.
  - `email` (`VARCHAR(255)`, UNIQUE, Indexed, NOT NULL): Primary communication email.
  - `phone` (`VARCHAR(20)`, Indexed, NOT NULL): Registered business contact number.
  - `kyc_status` (`ENUM merchant_kyc_status`, NOT NULL, Default: `PENDING`): `PENDING`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`.
  - `upi_vpa` (`VARCHAR(100)`, Nullable): Default merchant virtual payment address.
  - `mcc_code` (`VARCHAR(4)`, Nullable): 4-digit Merchant Category Code.
  - `risk_tier` (`ENUM merchant_risk_tier`, NOT NULL, Default: `MEDIUM`): `LOW`, `MEDIUM`, `HIGH`, `PROHIBITED`.
  - `is_active` (`BOOLEAN`, NOT NULL, Default: `TRUE`): Operational toggle.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable): Soft-delete timestamp.

#### `merchant_kyc_documents`
Regulatory KYC compliance document repository.
- **Columns**:
  - `id` (`UUID`, PK): Document record identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE CASCADE, Indexed, NOT NULL): Target merchant.
  - `document_type` (`ENUM kyc_document_type`, NOT NULL): `PAN`, `GSTIN`, `INCORPORATION_CERT`, `BANK_STATEMENT`, `AADHAAR`, `OTHER`.
  - `document_number` (`VARCHAR(100)`, NOT NULL): Document identification number.
  - `file_url` (`VARCHAR(1024)`, NOT NULL): Secure storage object URL.
  - `status` (`ENUM kyc_document_status`, NOT NULL, Default: `SUBMITTED`): `SUBMITTED`, `VERIFIED`, `REJECTED`.
  - `verified_at` (`TIMESTAMPTZ`, Nullable): Verification timestamp.
  - `notes` (`TEXT`, Nullable): Compliance officer comments.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `stores`
Individual retail outlets or digital storefronts under a merchant.
- **Columns**:
  - `id` (`UUID`, PK): Store identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE CASCADE, Indexed, NOT NULL): Parent merchant.
  - `name` (`VARCHAR(255)`, NOT NULL): Store location display name.
  - `code` (`VARCHAR(50)`, NOT NULL): Unique store code per merchant.
  - `address_line1` / `city` / `state` / `postal_code` (`VARCHAR`, Nullable): Physical store address.
  - `is_active` (`BOOLEAN`, NOT NULL, Default: `TRUE`).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable): Soft-delete timestamp.
- **Constraints**: `UNIQUE (merchant_id, code)`.

#### `merchant_staff`
Staff members assigned to specific merchant accounts and store locations.
- **Columns**:
  - `id` (`UUID`, PK): Staff record identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE CASCADE, Indexed, NOT NULL).
  - `user_id` (`UUID`, FK -> `users.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `store_id` (`UUID`, FK -> `stores.id`, ON DELETE SET NULL, Indexed, Nullable): Optional store assignment.
  - `role` (`ENUM merchant_staff_role`, NOT NULL, Default: `CASHIER`): `OWNER`, `ADMIN`, `MANAGER`, `CASHIER`, `ACCOUNTANT`.
  - `is_active` (`BOOLEAN`, NOT NULL, Default: `TRUE`).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

---

### 4. Customers (`app/modules/customers`)

#### `customers`
Customer profiles engaged in transactions across merchants.
- **Columns**:
  - `id` (`UUID`, PK): Customer identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `name` (`VARCHAR(255)`, NOT NULL): Customer name.
  - `email` (`VARCHAR(255)`, Indexed, Nullable): Email address.
  - `phone` (`VARCHAR(20)`, Indexed, NOT NULL): Customer telephone number.
  - `upi_vpa` (`VARCHAR(100)`, Nullable): Default payer UPI ID.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable): Soft-delete timestamp.
- **Indexes**: Composite index on `(merchant_id, phone)`.

---

### 5. Invoices & Line Items (`app/modules/invoices`, `app/modules/invoice_items`)

#### `invoices`
Invoicing and bill generation.
- **Columns**:
  - `id` (`UUID`, PK): Invoice identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `store_id` (`UUID`, FK -> `stores.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `customer_id` (`UUID`, FK -> `customers.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `invoice_number` (`VARCHAR(100)`, NOT NULL): Unique invoice number per merchant.
  - `total_amount` (`NUMERIC(12, 2)`, NOT NULL): Total bill amount.
  - `paid_amount` (`NUMERIC(12, 2)`, NOT NULL, Default: `0.00`): Cumulative settled payments.
  - `currency` (`VARCHAR(3)`, NOT NULL, Default: `'INR'`).
  - `status` (`ENUM invoice_status`, NOT NULL, Default: `DRAFT`, Indexed): `DRAFT`, `ISSUED`, `PARTIALLY_PAID`, `PAID`, `CANCELLED`, `OVERDUE`, `REFUNDED`.
  - `allow_partial_payment` (`BOOLEAN`, NOT NULL, Default: `FALSE`).
  - `allow_split_payment` (`BOOLEAN`, NOT NULL, Default: `FALSE`).
  - `due_date` (`TIMESTAMPTZ`, Nullable): Invoice payment deadline.
  - `notes` (`TEXT`, Nullable): Public or private notes.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable): Soft-delete timestamp.
- **Constraints & Indexes**: `UNIQUE (merchant_id, invoice_number)`, Index on `(merchant_id, status)`.

#### `invoice_items`
Detailed line items for an invoice.
- **Columns**:
  - `id` (`UUID`, PK): Item identifier.
  - `invoice_id` (`UUID`, FK -> `invoices.id`, ON DELETE CASCADE, Indexed, NOT NULL).
  - `name` (`VARCHAR(255)`, NOT NULL): Item or service title.
  - `description` (`TEXT`, Nullable): Item description.
  - `quantity` (`NUMERIC(10, 2)`, NOT NULL, Default: `1.00`).
  - `unit_price` (`NUMERIC(12, 2)`, NOT NULL).
  - `tax_rate` (`NUMERIC(5, 2)`, NOT NULL, Default: `0.00`): Percentage tax.
  - `line_total` (`NUMERIC(12, 2)`, NOT NULL): Net calculated total (`qty * unit_price * (1 + tax_rate / 100)`).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable).

---

### 6. Payment Channels (`app/modules/payment_requests`, `app/modules/upi_qr`, `app/modules/payment_links`)

#### `payment_requests`
Direct collect requests pushed to customer UPI VPAs.
- **Columns**:
  - `id` (`UUID`, PK): Payment request identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `invoice_id` (`UUID`, FK -> `invoices.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `customer_id` (`UUID`, FK -> `customers.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `status` (`ENUM payment_request_status`, NOT NULL, Default: `PENDING`, Indexed): `PENDING`, `COMPLETED`, `EXPIRED`, `CANCELLED`, `FAILED`.
  - `expires_at` (`TIMESTAMPTZ`, NOT NULL): Collect request validity duration.
  - `payer_vpa` (`VARCHAR(100)`, Nullable): Destination VPA.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `upi_qr_codes`
Static and dynamic UPI QR code generation.
- **Columns**:
  - `id` (`UUID`, PK): QR record identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `store_id` (`UUID`, FK -> `stores.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `invoice_id` (`UUID`, FK -> `invoices.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `qr_type` (`ENUM qr_type`, NOT NULL, Default: `DYNAMIC`): `STATIC`, `DYNAMIC`.
  - `upi_string` (`VARCHAR(1024)`, NOT NULL): Standardized UPI intent URI string (`upi://pay?...`).
  - `image_url` (`VARCHAR(1024)`, Nullable): Pre-rendered QR code PNG/SVG artifact.
  - `amount` (`NUMERIC(12, 2)`, Nullable): Mandatory for dynamic, optional for static.
  - `status` (`ENUM qr_status`, NOT NULL, Default: `ACTIVE`): `ACTIVE`, `INACTIVE`, `EXPIRED`.
  - `expires_at` (`TIMESTAMPTZ`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `payment_links`
Shareable checkout URLs.
- **Columns**:
  - `id` (`UUID`, PK): Link identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `invoice_id` (`UUID`, FK -> `invoices.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `customer_id` (`UUID`, FK -> `customers.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `short_code` (`VARCHAR(50)`, UNIQUE, Indexed, NOT NULL): URL-safe slug.
  - `amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `status` (`ENUM payment_link_status`, NOT NULL, Default: `ACTIVE`): `ACTIVE`, `PAID`, `EXPIRED`, `CANCELLED`.
  - `expires_at` (`TIMESTAMPTZ`, NOT NULL).
  - `allow_partial` (`BOOLEAN`, NOT NULL, Default: `FALSE`).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable).

---

### 7. Splits & Payment Plans (`app/modules/splits`)

#### `payment_plans`
Multi-party, installment, or milestone payment plans.
- **Columns**:
  - `id` (`UUID`, PK): Plan identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `invoice_id` (`UUID`, FK -> `invoices.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `customer_id` (`UUID`, FK -> `customers.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `plan_type` (`ENUM plan_type`, NOT NULL): `DEPOSIT`, `INSTALLMENT`, `MILESTONE`, `CUSTOM_SPLIT`.
  - `total_amount` (`NUMERIC(12, 2)`, NOT NULL): Aggregate scheduled sum.
  - `status` (`ENUM payment_plan_status`, NOT NULL, Default: `ACTIVE`): `ACTIVE`, `COMPLETED`, `CANCELLED`, `DEFAULTED`.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
  - `deleted_at` (`TIMESTAMPTZ`, Nullable).

#### `payment_plan_installments`
Individual installment slices under a payment plan.
- **Columns**:
  - `id` (`UUID`, PK): Installment slice identifier.
  - `payment_plan_id` (`UUID`, FK -> `payment_plans.id`, ON DELETE CASCADE, Indexed, NOT NULL).
  - `installment_number` (`INTEGER`, NOT NULL): Sequence index (1, 2, ...).
  - `amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `paid_amount` (`NUMERIC(12, 2)`, NOT NULL, Default: `0.00`).
  - `due_date` (`TIMESTAMPTZ`, NOT NULL).
  - `status` (`ENUM installment_status`, NOT NULL, Default: `PENDING`): `PENDING`, `PARTIALLY_PAID`, `PAID`, `OVERDUE`, `CANCELLED`.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

---

### 8. Core Payments & Transactions (`app/modules/payments`)

#### `payment_transactions`
The central financial ledger table representing all payment attempts and settled funds.
- **Columns**:
  - `id` (`UUID`, PK): Primary transaction identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `invoice_id` (`UUID`, FK -> `invoices.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `customer_id` (`UUID`, FK -> `customers.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `payment_link_id` (`UUID`, FK -> `payment_links.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `upi_qr_id` (`UUID`, FK -> `upi_qr_codes.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `installment_id` (`UUID`, FK -> `payment_plan_installments.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `idempotency_key` (`VARCHAR(255)`, UNIQUE, Indexed, NOT NULL): Client-supplied token preventing duplicate processing.
  - `amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `currency` (`VARCHAR(3)`, NOT NULL, Default: `'INR'`).
  - `status` (`ENUM transaction_status`, NOT NULL, Default: `INITIATED`, Indexed): `INITIATED`, `PENDING`, `SUCCESS`, `FAILED`, `TIMEOUT`, `REFUNDED`, `PARTIALLY_REFUNDED`.
  - `payment_method` (`ENUM payment_method`, NOT NULL, Default: `UPI_QR`): `UPI_COLLECT`, `UPI_INTENT`, `UPI_QR`, `CARD`, `NET_BANKING`, `WALLET`.
  - `mock_scenario` (`VARCHAR(50)`, Nullable): Simulator control flag for testing (e.g. `SUCCESS`, `FAILURE_INSUFFICIENT_FUNDS`, `TIMEOUT`).
  - `provider_ref_id` (`VARCHAR(100)`, Indexed, Nullable): Bank/NPCI retrieval reference number (RRN).
  - `payer_vpa` / `payee_vpa` (`VARCHAR(100)`, Nullable): Originating and receiving UPI addresses.
  - `failure_reason` (`VARCHAR(255)`, Nullable): Detailed gateway error message.
  - `completed_at` (`TIMESTAMPTZ`, Nullable): Terminal timestamp.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).
- **Indexes**:
  - `UNIQUE (idempotency_key)`
  - Index on `(merchant_id, status)`
  - Index on `(merchant_id, created_at)`

#### `transaction_status_history`
Immutable audit log of all transaction state changes.
- **Columns**:
  - `id` (`UUID`, PK): History entry identifier.
  - `transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `from_status` (`VARCHAR(50)`, Nullable): Previous state.
  - `to_status` (`VARCHAR(50)`, NOT NULL): New state.
  - `reason` (`TEXT`, Nullable): Trigger reason (webhook, polling, user cancel).
  - `created_at` (`TIMESTAMPTZ`, NOT NULL): Event timestamp.

---

### 9. Webhooks (`app/modules/webhooks`)

#### `webhook_events_inbound`
Raw incoming webhook payloads received from UPI switches and acquiring banks.
- **Columns**:
  - `id` (`UUID`, PK): Event identifier.
  - `provider` (`VARCHAR(50)`, NOT NULL): Sender gateway (e.g. `NPCI`, `HDFC`, `MOCK_PROVIDER`).
  - `event_type` (`VARCHAR(100)`, NOT NULL): Gateway event type.
  - `payload` (`JSONB`, NOT NULL): Full raw payload.
  - `headers` (`JSONB`, Nullable): HTTP headers (including signatures).
  - `status` (`ENUM webhook_inbound_status`, NOT NULL, Default: `RECEIVED`): `RECEIVED`, `PROCESSED`, `FAILED`, `IGNORED`.
  - `processed_at` (`TIMESTAMPTZ`, Nullable).
  - `error_message` (`TEXT`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `webhook_subscriptions`
Outbound merchant webhook destination configuration.
- **Columns**:
  - `id` (`UUID`, PK): Subscription identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `target_url` (`VARCHAR(1024)`, NOT NULL): HTTP POST endpoint.
  - `secret_key` (`VARCHAR(255)`, NOT NULL): HMAC signing secret.
  - `subscribed_events` (`JSONB`, NOT NULL, Default: `[]`): Array of event topics.
  - `is_active` (`BOOLEAN`, NOT NULL, Default: `TRUE`).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `webhook_deliveries`
Outbound delivery attempt history and dispatch logs.
- **Columns**:
  - `id` (`UUID`, PK): Delivery attempt identifier.
  - `subscription_id` (`UUID`, FK -> `webhook_subscriptions.id`, ON DELETE CASCADE, Indexed, NOT NULL).
  - `event_type` (`VARCHAR(100)`, NOT NULL).
  - `payload` (`JSONB`, NOT NULL).
  - `response_status_code` (`INTEGER`, Nullable): Received HTTP response status code.
  - `response_body` (`TEXT`, Nullable): Response snippet.
  - `attempt_count` (`INTEGER`, NOT NULL, Default: `1`).
  - `status` (`ENUM webhook_delivery_status`, NOT NULL, Default: `PENDING`): `PENDING`, `DELIVERED`, `FAILED`, `RETRYING`.
  - `next_retry_at` (`TIMESTAMPTZ`, Nullable): Exponential backoff schedule.
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

---

### 10. Reconciliation & Duplicate Detection (`app/modules/reconciliation`, `app/modules/duplicate_detection`)

#### `reconciliation_batches`
Daily and on-demand bank settlement reconciliation batches.
- **Columns**:
  - `id` (`UUID`, PK): Batch identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `batch_date` (`DATE`, NOT NULL): Statement date.
  - `status` (`ENUM reconciliation_status`, NOT NULL, Default: `PENDING`): `PENDING`, `PROCESSING`, `MATCHED`, `DISCREPANCIES_FOUND`, `COMPLETED`.
  - `total_records` / `matched_records` / `mismatched_records` (`INTEGER`, NOT NULL, Default: `0`).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `reconciliation_entries`
Line-by-line comparison between internal payment transactions and provider settlement files.
- **Columns**:
  - `id` (`UUID`, PK): Entry identifier.
  - `batch_id` (`UUID`, FK -> `reconciliation_batches.id`, ON DELETE CASCADE, Indexed, NOT NULL).
  - `transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `provider_ref_id` (`VARCHAR(100)`, Indexed, Nullable).
  - `expected_amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `actual_amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `status` (`ENUM reconciliation_entry_status`, NOT NULL, Default: `MATCHED`): `MATCHED`, `AMOUNT_MISMATCH`, `STATUS_MISMATCH`, `MISSING_IN_INTERNAL`, `MISSING_IN_PROVIDER`.
  - `notes` (`TEXT`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `duplicate_transaction_flags`
Algorithmic duplicate payment detection flags.
- **Columns**:
  - `id` (`UUID`, PK): Flag identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `original_transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `duplicate_transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `confidence_score` (`NUMERIC(5, 4)`, NOT NULL): 0.0000 to 1.0000 probability.
  - `flag_reason` (`ENUM duplicate_flag_reason`, NOT NULL): `IDENTICAL_IDEMPOTENCY_KEY`, `IDENTICAL_AMOUNT_AND_VPA`, `TIMEFRAME_BURST`, `PROVIDER_RRN_COLLISION`.
  - `status` (`ENUM duplicate_flag_status`, NOT NULL, Default: `SUSPECTED`): `SUSPECTED`, `CONFIRMED_DUPLICATE`, `FALSE_POSITIVE`, `RESOLVED`.
  - `resolved_by` (`UUID`, FK -> `users.id`, ON DELETE RESTRICT, Nullable).
  - `resolved_at` (`TIMESTAMPTZ`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

---

### 11. Refunds & Settlements (`app/modules/refunds`, `app/modules/settlements`)

#### `refunds`
Full and partial refunds credited back to customers.
- **Columns**:
  - `id` (`UUID`, PK): Refund identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `amount` (`NUMERIC(12, 2)`, NOT NULL).
  - `status` (`ENUM refund_status`, NOT NULL, Default: `INITIATED`): `INITIATED`, `PENDING`, `SUCCESS`, `FAILED`.
  - `reason` (`VARCHAR(255)`, NOT NULL).
  - `provider_refund_id` (`VARCHAR(100)`, Indexed, Nullable).
  - `failure_reason` (`VARCHAR(255)`, Nullable).
  - `completed_at` (`TIMESTAMPTZ`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `settlements`
Net payouts credited to merchant bank accounts.
- **Columns**:
  - `id` (`UUID`, PK): Settlement identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `settlement_cycle` (`ENUM settlement_cycle`, NOT NULL, Default: `T_PLUS_1`): `T_PLUS_0`, `T_PLUS_1`, `T_PLUS_2`, `ON_DEMAND`.
  - `gross_amount` (`NUMERIC(12, 2)`, NOT NULL): Gross transaction volume in batch.
  - `deduction_amount` (`NUMERIC(12, 2)`, NOT NULL, Default: `0.00`): Fees, MDR, refunds, or reserve holds.
  - `net_amount` (`NUMERIC(12, 2)`, NOT NULL): Final payout disbursed.
  - `status` (`ENUM settlement_status`, NOT NULL, Default: `PENDING`): `PENDING`, `PROCESSING`, `SETTLED`, `FAILED`.
  - `bank_account_ref` (`VARCHAR(100)`, NOT NULL): Masked destination bank account identifier.
  - `payout_ref_id` (`VARCHAR(100)`, Indexed, Nullable): UTR / bank reference number.
  - `settled_at` (`TIMESTAMPTZ`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `settlement_line_items`
Individual transaction ledger entries included in a settlement batch.
- **Columns**:
  - `id` (`UUID`, PK): Line item identifier.
  - `settlement_id` (`UUID`, FK -> `settlements.id`, ON DELETE CASCADE, Indexed, NOT NULL).
  - `transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `amount` (`NUMERIC(12, 2)`, NOT NULL): Transaction gross.
  - `fee_amount` (`NUMERIC(12, 2)`, NOT NULL, Default: `0.00`): Processing fee.
  - `tax_amount` (`NUMERIC(12, 2)`, NOT NULL, Default: `0.00`): GST on fee.
  - `net_amount` (`NUMERIC(12, 2)`, NOT NULL): Net credited amount.
  - `created_at` (`TIMESTAMPTZ`, NOT NULL).

---

### 12. Risk, Notifications, & Auditing (`app/modules/risk`, `app/modules/notifications`, `app/modules/audit`)

#### `risk_signals`
Real-time risk scoring and fraud evaluation records.
- **Columns**:
  - `id` (`UUID`, PK): Signal identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, NOT NULL).
  - `transaction_id` (`UUID`, FK -> `payment_transactions.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `risk_score` (`NUMERIC(5, 2)`, NOT NULL): Numerical score from 0.00 to 100.00.
  - `risk_level` (`ENUM risk_level`, NOT NULL, Default: `LOW`): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  - `rule_triggered` (`VARCHAR(100)`, NOT NULL): Rule engine identifier.
  - `action_taken` (`ENUM risk_action`, NOT NULL, Default: `ALLOW`): `ALLOW`, `FLAG_FOR_REVIEW`, `CHALLENGE_2FA`, `BLOCK`.
  - `metadata_json` (`JSONB`, Nullable): Contextual fraud indicators (IP, device fingerprint, velocity).
  - `created_at` (`TIMESTAMPTZ`, NOT NULL).

#### `notifications`
Customer and merchant multi-channel dispatch logs.
- **Columns**:
  - `id` (`UUID`, PK): Notification identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `recipient` (`VARCHAR(255)`, NOT NULL): Email, phone number, or target user UUID.
  - `channel` (`ENUM notification_channel`, NOT NULL, Default: `IN_APP`): `SMS`, `EMAIL`, `WHATSAPP`, `WEBHOOK`, `IN_APP`.
  - `title` (`VARCHAR(255)`, NOT NULL).
  - `content` (`TEXT`, NOT NULL).
  - `status` (`ENUM notification_status`, NOT NULL, Default: `QUEUED`): `QUEUED`, `SENT`, `DELIVERED`, `FAILED`.
  - `sent_at` (`TIMESTAMPTZ`, Nullable).
  - `created_at` / `updated_at` (`TIMESTAMPTZ`, NOT NULL).

#### `audit_logs`
Immutable compliance and security audit trail tracking platform mutations.
- **Columns**:
  - `id` (`UUID`, PK): Audit log entry identifier.
  - `merchant_id` (`UUID`, FK -> `merchants.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `user_id` (`UUID`, FK -> `users.id`, ON DELETE RESTRICT, Indexed, Nullable).
  - `entity_name` (`VARCHAR(100)`, Indexed, NOT NULL): Target entity class/table name.
  - `entity_id` (`UUID`, Indexed, NOT NULL): Target entity primary key.
  - `action` (`ENUM audit_action`, NOT NULL): `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT`, `STATUS_CHANGE`, `REFUND_TRIGGER`.
  - `changes` (`JSONB`, Nullable): JSON diff showing before/after field changes.
  - `ip_address` (`VARCHAR(45)`, Nullable): Client IPv4/IPv6 address.
  - `user_agent` (`VARCHAR(512)`, Nullable): Client browser/device agent.
  - `created_at` (`TIMESTAMPTZ`, NOT NULL): Timestamp of operation.
- **Indexes**:
  - Index on `(entity_name, entity_id)`
  - Index on `(created_at)`
