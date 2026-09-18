"""Seed Script for PayFlow Development & Demo Environment.

Creates realistic data across merchants, stores, staff, customers, invoices,
payment plans, transactions, refunds, reconciliation batches, settlements,
risk signals, duplicate flags, notifications, and audit logs.

Idempotent & rerunnable.
Usage:
    python -m seed.seed_data
"""

import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.db.base  # noqa: F401 Ensure all models are registered cleanly before other imports

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal


# Import models
from app.modules.auth.models import User
from app.modules.rbac.models import Permission, Role, RolePermission, UserRole
from app.modules.merchants.models import (
    Merchant,
    KycStatus,
    RiskTier,
    MerchantStaff,
    StaffRole,
    MerchantKycDocument,
    KycDocumentType,
    KycDocumentStatus,
)
from app.modules.stores.models import Store
from app.modules.customers.models import Customer
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.invoice_items.models import InvoiceItem
from app.modules.payment_requests.models import PaymentRequest, PaymentRequestStatus
from app.modules.payment_links.models import PaymentLink, PaymentLinkStatus
from app.modules.splits.models import (
    PaymentPlan,
    PaymentPlanInstallment,
    PlanType,
    PaymentPlanStatus,
    InstallmentStatus,
)
from app.modules.payments.models import (
    PaymentTransaction,
    PaymentMethod,
    TransactionStatus,
    TransactionStatusHistory,
)
from app.modules.refunds.models import Refund, RefundStatus
from app.modules.duplicate_detection.models import (
    DuplicateTransactionFlag,
    DuplicateFlagReason,
    DuplicateFlagStatus,
)
from app.modules.risk.models import (
    RiskSignal,
    RiskLevel,
    RiskAction,
)
from app.modules.reconciliation.models import (

    ReconciliationBatch,
    ReconciliationEntry,
    ReconciliationStatus,
    MatchStatus,
    ReconciliationEntryStatus,
)
from app.modules.settlements.models import (
    Settlement,
    SettlementCycle,
    SettlementStatus,
    SettlementLineItem,
)
from app.modules.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from app.modules.audit.models import AuditLog, AuditAction


def seed_database():
    env = os.environ.get("ENVIRONMENT", settings.ENVIRONMENT)
    force = os.environ.get("FORCE_SEED", "false").lower() == "true"

    if env not in ("development", "test", "local") and not force:
        print(f"[SEED] Skipping seed in environment: {env}. Set FORCE_SEED=true to override.")
        return

    print(f"[SEED] Starting database seeding for environment: {env}...")
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_owner = db.query(User).filter(User.email == "owner@payflow.demo").first()
        if existing_owner and not force:
            print("[SEED] Demo user 'owner@payflow.demo' already exists. Re-verifying core records...")
            # We ensure roles and sample data exist without wiping
            return

        # -------------------------------------------------------------
        # 1. RBAC Roles & Permissions
        # -------------------------------------------------------------
        print("[SEED] Creating RBAC Roles & Permissions...")
        roles_defs = [
            ("Owner", "Full account control, settlement authorizations, and store management", True),
            ("Manager", "Store-level operations, invoice creation, and payment collection", True),
            ("Cashier", "Point-of-sale payment collection and receipt generation", True),
            ("Auditor", "Read-only access to audit logs, transactions, and compliance reports", True),
        ]
        roles_map = {}
        for r_name, r_desc, is_sys in roles_defs:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=r_desc, is_system_role=is_sys)
                db.add(role)
                db.flush()
            roles_map[r_name] = role

        perm_codes = [
            ("staff:read", "Read Staff", "View staff members"),
            ("staff:write", "Manage Staff", "Add or edit staff members"),
            ("merchants:read", "Read Merchant", "View merchant profile and settings"),
            ("merchants:write", "Edit Merchant", "Update merchant profile and settings"),
            ("merchants:kyc", "Manage KYC", "Submit and view KYC documentation"),
            ("stores:read", "Read Stores", "View store details"),
            ("stores:write", "Manage Stores", "Create and edit stores"),
            ("customers:read", "Read Customers", "View customer directory"),
            ("customers:write", "Manage Customers", "Create and edit customers"),
            ("invoices:read", "Read Invoices", "View invoices and payment links"),
            ("invoices:write", "Manage Invoices", "Create and edit invoices"),
            ("payments:read", "Read Payments", "View payment transactions and reports"),
            ("payments:write", "Initiate Payments", "Collect payments and generate QR codes"),
            ("refunds:approve", "Approve Refunds", "Authorize and approve customer refunds"),
            ("settlements:read", "Read Settlements", "View settlement batches"),
            ("settlements:write", "Manage Settlements", "Trigger reconciliation and settlement runs"),
            ("audit:read", "Read Audit Logs", "View compliance and immutable audit logs"),
            ("risk:read", "Read Risk Alerts", "View fraud and risk alerts"),
            ("risk:write", "Resolve Risk", "Review and resolve risk flags"),
        ]
        perms_map = {}
        for code, name, desc in perm_codes:
            perm = db.query(Permission).filter(Permission.code == code).first()
            if not perm:
                perm = Permission(code=code, name=name, description=desc)
                db.add(perm)
                db.flush()
            perms_map[code] = perm

        # Assign permissions to roles
        role_perm_matrix = {
            "Owner": list(perms_map.keys()),
            "Manager": [
                "staff:read", "merchants:read", "stores:read", "stores:write",
                "customers:read", "customers:write", "invoices:read", "invoices:write",
                "payments:read", "payments:write", "refunds:approve", "settlements:read",
                "risk:read", "risk:write", "audit:read",
            ],
            "Cashier": [
                "stores:read", "customers:read", "customers:write", "invoices:read",
                "invoices:write", "payments:read", "payments:write",
            ],
            "Auditor": [
                "merchants:read", "stores:read", "customers:read", "invoices:read",
                "payments:read", "settlements:read", "audit:read", "risk:read",
            ],
        }
        for r_name, p_codes in role_perm_matrix.items():
            r = roles_map[r_name]
            for p_code in p_codes:
                p = perms_map[p_code]
                existing_rp = db.query(RolePermission).filter(
                    RolePermission.role_id == r.id,
                    RolePermission.permission_id == p.id,
                ).first()
                if not existing_rp:
                    db.add(RolePermission(role_id=r.id, permission_id=p.id))
        db.commit()

        # -------------------------------------------------------------
        # 2. Demo Users
        # -------------------------------------------------------------
        print("[SEED] Creating Demo Users...")
        users_def = [
            ("owner@payflow.demo", "Rohan Sharma", "+919876543210", "Owner"),
            ("manager@payflow.demo", "Ananya Verma", "+919876543211", "Manager"),
            ("cashier@payflow.demo", "Vikram Patel", "+919876543212", "Cashier"),
            ("auditor@payflow.demo", "Pooja Deshmukh", "+919876543213", "Auditor"),
        ]
        demo_users = {}
        for email, full_name, phone, role_name in users_def:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    hashed_password=get_password_hash("Password123!"),
                    full_name=full_name,
                    phone=phone,
                    is_active=True,
                )
                db.add(user)
                db.flush()
            demo_users[role_name] = user
        db.commit()

        # -------------------------------------------------------------
        # 3. Demo Merchants (3-5 at different onboarding & KYC stages)
        # -------------------------------------------------------------
        print("[SEED] Creating Merchants & Stores...")
        merchants_data = [
            {
                "business_name": "Apex Electronics & Appliances",
                "legal_name": "Apex Retail Solutions India Pvt Ltd",
                "email": "contact@apexelectronics.in",
                "phone": "+919811223344",
                "pan": "ABCDE1234F",
                "gstin": "27ABCDE1234F1Z5",
                "mcc_code": "5732",
                "upi_vpa": "apexretail@icici",
                "kyc_status": KycStatus.APPROVED,
                "risk_tier": RiskTier.LOW,
                "stores": [
                    {"name": "Apex Flagship - Bandra", "code": "APEX-MUM-01", "vpa": "apex.bandra@icici"},
                    {"name": "Apex Tech Park - Whitefield", "code": "APEX-BLR-01", "vpa": "apex.blr@icici"},
                ],
            },
            {
                "business_name": "Kavita Organic Grocers",
                "legal_name": "Kavita Agro & Fresh Farms LLP",
                "email": "support@kavitaorganics.com",
                "phone": "+919822334455",
                "pan": "BCDEF2345G",
                "gstin": "29BCDEF2345G1Z8",
                "mcc_code": "5411",
                "upi_vpa": "kavitaorganics@okhdfcbank",
                "kyc_status": KycStatus.APPROVED,
                "risk_tier": RiskTier.LOW,
                "stores": [
                    {"name": "Kavita Fresh - Indiranagar", "code": "KVT-BLR-01", "vpa": "kavita.indira@okhdfcbank"},
                    {"name": "Kavita Fresh - Koramangala", "code": "KVT-BLR-02", "vpa": "kavita.kora@okhdfcbank"},
                ],
            },
            {
                "business_name": "Zeta Cloud & Enterprise Consulting",
                "legal_name": "Zeta Solutions Technologies Pvt Ltd",
                "email": "billing@zetacloud.io",
                "phone": "+919833445566",
                "pan": "CDEFG3456H",
                "gstin": "36CDEFG3456H1Z2",
                "mcc_code": "7372",
                "upi_vpa": "zetacloud@axisbank",
                "kyc_status": KycStatus.UNDER_REVIEW,
                "risk_tier": RiskTier.MEDIUM,
                "stores": [
                    {"name": "Zeta HQ - Hyderabad", "code": "ZTA-HYD-01", "vpa": "zeta.hq@axisbank"},
                ],
            },
            {
                "business_name": "Mumbai Artisan Roasters",
                "legal_name": "Mumbai Artisan Coffee Works LLP",
                "email": "hello@mumbaiartisan.cafe",
                "phone": "+919844556677",
                "pan": "DEFGH4567J",
                "gstin": "27DEFGH4567J1Z9",
                "mcc_code": "5814",
                "upi_vpa": "mumbaiartisan@yesbank",
                "kyc_status": KycStatus.PENDING,
                "risk_tier": RiskTier.MEDIUM,
                "stores": [
                    {"name": "Colaba Roastery", "code": "MAR-MUM-01", "vpa": "mar.colaba@yesbank"},
                ],
            },
        ]

        created_merchants = []
        created_stores = []

        for m_info in merchants_data:
            merchant = db.query(Merchant).filter(Merchant.email == m_info["email"]).first()
            if not merchant:
                merchant = Merchant(
                    business_name=m_info["business_name"],
                    legal_name=m_info["legal_name"],
                    email=m_info["email"],
                    phone=m_info["phone"],
                    mcc_code=m_info["mcc_code"],
                    upi_vpa=m_info["upi_vpa"],
                    kyc_status=m_info["kyc_status"],
                    risk_tier=m_info["risk_tier"],
                    is_active=True,
                )
                db.add(merchant)
                db.flush()

                # Add sample KYC Documents
                for doc_type, doc_num in [
                    (KycDocumentType.PAN, m_info["pan"]),
                    (KycDocumentType.GSTIN, m_info["gstin"]),
                    (KycDocumentType.BANK_STATEMENT, f"BS-{uuid.uuid4().hex[:8].upper()}"),
                ]:
                    db.add(
                        MerchantKycDocument(
                            merchant_id=merchant.id,
                            document_type=doc_type,
                            document_number=doc_num,
                            file_url=f"https://storage.payflow.internal/kyc/{merchant.id}/{doc_type.value}.pdf",
                            status=KycDocumentStatus.VERIFIED if m_info["kyc_status"] == KycStatus.APPROVED else KycDocumentStatus.SUBMITTED,
                            verified_at=datetime.now(timezone.utc) if m_info["kyc_status"] == KycStatus.APPROVED else None,
                        )
                    )

                # Add stores
                for s_info in m_info["stores"]:
                    store = Store(
                        merchant_id=merchant.id,
                        name=s_info["name"],
                        code=s_info["code"],
                        upi_vpa=s_info["vpa"],
                        address_line1="Commercial Complex, Suite 400",
                        city="Mumbai" if "MUM" in s_info["code"] else "Bengaluru" if "BLR" in s_info["code"] else "Hyderabad",
                        state="Maharashtra" if "MUM" in s_info["code"] else "Karnataka" if "BLR" in s_info["code"] else "Telangana",
                        postal_code="400050" if "MUM" in s_info["code"] else "560038" if "BLR" in s_info["code"] else "500081",
                        is_active=True,
                    )
                    db.add(store)
                    db.flush()
            else:
                existing_stores = db.query(Store).filter(Store.merchant_id == merchant.id).all()
                created_stores.extend(existing_stores)

            created_merchants.append(merchant)
        db.commit()

        # Link demo staff to Primary Merchant (Apex)
        primary_merchant = created_merchants[0]
        primary_store = created_stores[0] if created_stores else db.query(Store).filter(Store.merchant_id == primary_merchant.id).first()

        for role_name, staff_user in demo_users.items():
            staff_role_enum = getattr(StaffRole, role_name.upper(), StaffRole.CASHIER)
            existing_staff = db.query(MerchantStaff).filter(
                MerchantStaff.merchant_id == primary_merchant.id,
                MerchantStaff.user_id == staff_user.id,
            ).first()
            if not existing_staff:
                db.add(
                    MerchantStaff(
                        merchant_id=primary_merchant.id,
                        user_id=staff_user.id,
                        store_id=primary_store.id if role_name in ("Cashier", "Manager") else None,
                        role=staff_role_enum,
                        is_active=True,
                    )
                )

            # Assign user_roles for primary merchant
            role_obj = roles_map[role_name]
            existing_ur = db.query(UserRole).filter(
                UserRole.merchant_id == primary_merchant.id,
                UserRole.user_id == staff_user.id,
                UserRole.role_id == role_obj.id,
            ).first()
            if not existing_ur:
                db.add(
                    UserRole(
                        merchant_id=primary_merchant.id,
                        user_id=staff_user.id,
                        role_id=role_obj.id,
                    )
                )
        db.commit()

        # -------------------------------------------------------------
        # 4. Customers (20-30 realistic customers)
        # -------------------------------------------------------------
        print("[SEED] Creating Customers...")
        indian_names = [
            ("Aarav Mehta", "aarav.mehta@gmail.com", "+919811100001"),
            ("Diya Sen", "diya.sen@outlook.com", "+919811100002"),
            ("Siddharth Rao", "sid.rao@gmail.com", "+919811100003"),
            ("Priyanka Joshi", "priyanka.j@yahoo.com", "+919811100004"),
            ("Rahul Nair", "rahul.nair@corporate.in", "+919811100005"),
            ("Sneha Kulkarni", "sneha.k@gmail.com", "+919811100006"),
            ("Karan Kapoor", "karan.kapoor@techflow.io", "+919811100007"),
            ("Neha Singhania", "neha.s@gmail.com", "+919811100008"),
            ("Arjun Chawla", "arjun.c@gmail.com", "+919811100009"),
            ("Kavita Iyer", "kavita.iyer@gmail.com", "+919811100010"),
            ("Aditya Bhatt", "aditya.b@gmail.com", "+919811100011"),
            ("Rhea Dsouza", "rhea.dsouza@gmail.com", "+919811100012"),
            ("Varun Saxena", "varun.saxena@gmail.com", "+919811100013"),
            ("Meera Bansal", "meera.bansal@gmail.com", "+919811100014"),
            ("Tanmay Aggarwal", "tanmay.a@gmail.com", "+919811100015"),
            ("Ishita Ghosh", "ishita.ghosh@gmail.com", "+919811100016"),
            ("Gaurav Pandey", "gaurav.p@gmail.com", "+919811100017"),
            ("Ankita Reddy", "ankita.reddy@gmail.com", "+919811100018"),
            ("Manish Tiwari", "manish.tiwari@gmail.com", "+919811100019"),
            ("Swati Pillai", "swati.pillai@gmail.com", "+919811100020"),
            ("Karthik Subramanian", "karthik.s@gmail.com", "+919811100021"),
            ("Divya Menon", "divya.menon@gmail.com", "+919811100022"),
            ("Rakesh Nambiar", "rakesh.n@gmail.com", "+919811100023"),
            ("Shweta Deshmukh", "shweta.d@gmail.com", "+919811100024"),
            ("Amitabh Das", "amitabh.das@gmail.com", "+919811100025"),
        ]

        created_customers = []
        for m in created_merchants[:2]:  # Seed customers for top 2 active merchants
            for name, email_prefix, phone in indian_names:
                m_email = f"{email_prefix.split('@')[0]}_{m.id.hex[:4]}@{email_prefix.split('@')[1]}"
                cust = db.query(Customer).filter(
                    Customer.merchant_id == m.id,
                    Customer.email == m_email,
                ).first()
                if not cust:
                    cust = Customer(
                        merchant_id=m.id,
                        name=name,
                        email=m_email,
                        phone=phone,
                        upi_vpa=f"{name.lower().replace(' ', '')}@okhdfcbank",
                    )
                    db.add(cust)
                    db.flush()
                created_customers.append(cust)
        db.commit()

        # -------------------------------------------------------------
        # 5. Invoices & Payment Plans (60-100 invoices over 90 days)
        # -------------------------------------------------------------
        print("[SEED] Creating Invoices, Items, Payment Plans & Transactions...")
        now = datetime.now(timezone.utc)

        all_transactions = []
        apex_merchant = created_merchants[0]
        apex_customers = db.query(Customer).filter(Customer.merchant_id == apex_merchant.id).all()

        invoice_products = [
            ("4K Smart OLED Television 55-inch", Decimal("54999.00"), "HNS8528"),
            ("Noise-Cancelling Wireless Headphones", Decimal("14999.00"), "HNS8518"),
            ("Ultra-Slim Laptop 16GB RAM 512GB SSD", Decimal("72000.00"), "HNS8471"),
            ("Ergonomic Mesh Office Chair", Decimal("11500.00"), "HNS9401"),
            ("Mechanical RGB Gaming Keyboard", Decimal("4299.00"), "HNS8471"),
            ("Smart Health Fitness Watch", Decimal("6999.00"), "HNS9102"),
            ("USB-C Fast Charging Hub 100W", Decimal("2499.00"), "HNS8504"),
            ("Wireless Home Audio Soundbar", Decimal("8999.00"), "HNS8518"),
        ]

        # Generate 70 invoices for Apex if not already generated
        existing_inv_count = db.query(Invoice).filter(Invoice.merchant_id == apex_merchant.id).count()
        if existing_inv_count < 70:
            for i in range(1, 71):
                customer = random.choice(apex_customers)
                created_date = now - timedelta(days=random.randint(1, 85), hours=random.randint(1, 23))

                # Pick 1-3 line items
                items_sample = random.sample(invoice_products, k=random.randint(1, 3))
                subtotal = sum(price for _, price, _ in items_sample)
                tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
                total = subtotal + tax

                # Determine invoice status distribution:
                # 60% PAID, 15% PARTIALLY_PAID, 15% SENT, 10% OVERDUE
                roll = random.random()
                if roll < 0.60:
                    inv_status = InvoiceStatus.PAID
                    paid_amt = total
                elif roll < 0.75:
                    inv_status = InvoiceStatus.PARTIALLY_PAID
                    paid_amt = (total * Decimal("0.4")).quantize(Decimal("0.01"))
                elif roll < 0.90:
                    inv_status = InvoiceStatus.SENT
                    paid_amt = Decimal("0.00")
                else:
                    inv_status = InvoiceStatus.OVERDUE
                    paid_amt = Decimal("0.00")

                invoice = Invoice(
                    merchant_id=apex_merchant.id,
                    customer_id=customer.id,
                    invoice_number=f"INV-APX-{1000 + i}",
                    subtotal=subtotal,
                    tax_total=tax,
                    discount_total=Decimal("0.00"),
                    total_amount=total,
                    paid_amount=paid_amt,
                    currency="INR",
                    status=inv_status,
                    due_date=created_date + timedelta(days=15),
                    created_at=created_date,
                    updated_at=created_date,
                    allow_partial_payment=True,
                )
                db.add(invoice)
                db.flush()

                # Add invoice items
                for prod_name, price, hsn in items_sample:
                    db.add(
                        InvoiceItem(
                            invoice_id=invoice.id,
                            name=prod_name,
                            description=f"{prod_name} (HSN: {hsn})",
                            quantity=Decimal("1.00"),
                            unit_price=price,
                            tax_rate=Decimal("18.00"),
                            discount_amount=Decimal("0.00"),
                            line_total=(price * Decimal("1.18")).quantize(Decimal("0.01")),
                        )
                    )

                # Showcase legitimate Split/Payment Plans on ~25% of invoices
                if i % 4 == 0:
                    plan_type = PlanType.INSTALLMENT if i % 2 == 0 else PlanType.DEPOSIT
                    p_plan = PaymentPlan(
                        merchant_id=apex_merchant.id,
                        invoice_id=invoice.id,
                        customer_id=customer.id,
                        plan_type=plan_type,
                        total_amount=total,
                        status=PaymentPlanStatus.COMPLETED if inv_status == InvoiceStatus.PAID else PaymentPlanStatus.ACTIVE,
                        created_at=created_date,
                    )
                    db.add(p_plan)
                    db.flush()

                    # 3 installments
                    part_amount = (total / Decimal("3")).quantize(Decimal("0.01"))
                    for inst_idx in range(1, 4):
                        inst_status = (
                            InstallmentStatus.PAID if (inv_status == InvoiceStatus.PAID or (inv_status == InvoiceStatus.PARTIALLY_PAID and inst_idx == 1))
                            else InstallmentStatus.PENDING
                        )
                        inst = PaymentPlanInstallment(
                            payment_plan_id=p_plan.id,
                            installment_number=inst_idx,
                            label=f"Phase {inst_idx} Installment",
                            amount=part_amount,
                            paid_amount=part_amount if inst_status == InstallmentStatus.PAID else Decimal("0.00"),
                            due_date=created_date + timedelta(days=15 * inst_idx),
                            status=inst_status,
                            created_at=created_date,
                        )
                        db.add(inst)

                # Create Transactions for this invoice
                if paid_amt > 0:
                    tx_count = 2 if inv_status == InvoiceStatus.PARTIALLY_PAID or i % 4 == 0 else 1
                    slice_amt = (paid_amt / Decimal(tx_count)).quantize(Decimal("0.01"))

                    for t_idx in range(tx_count):
                        tx_idemp = f"idemp-seed-{invoice.id.hex[:6]}-{t_idx}-{uuid.uuid4().hex[:6]}"
                        tx = PaymentTransaction(
                            merchant_id=apex_merchant.id,
                            invoice_id=invoice.id,
                            customer_id=customer.id,
                            amount=slice_amt,
                            currency="INR",
                            status=TransactionStatus.SUCCESS,
                            payment_method=PaymentMethod.UPI_INTENT if t_idx % 2 == 0 else PaymentMethod.UPI_COLLECT,
                            payer_vpa=f"cust_{customer.id.hex[:6]}@okhdfcbank",
                            payee_vpa=apex_merchant.upi_vpa,
                            idempotency_key=tx_idemp,
                            provider_ref_id=f"MOCK-UPI-{uuid.uuid4().hex[:10].upper()}",
                            created_at=created_date + timedelta(minutes=10 * (t_idx + 1)),
                            updated_at=created_date + timedelta(minutes=10 * (t_idx + 1)),
                        )
                        db.add(tx)
                        db.flush()
                        all_transactions.append(tx)

                        # Add status history
                        db.add(TransactionStatusHistory(
                            transaction_id=tx.id,
                            from_status=None,
                            to_status=TransactionStatus.CREATED.value,
                            reason="Transaction initialized via customer checkout",
                            created_at=tx.created_at,
                        ))
                        db.add(TransactionStatusHistory(
                            transaction_id=tx.id,
                            from_status=TransactionStatus.CREATED.value,
                            to_status=TransactionStatus.INITIATED.value,
                            reason="UPI Intent dispatched to bank PSP",
                            created_at=tx.created_at + timedelta(seconds=2),
                        ))
                        db.add(TransactionStatusHistory(
                            transaction_id=tx.id,
                            from_status=TransactionStatus.INITIATED.value,
                            to_status=TransactionStatus.SUCCESS.value,
                            reason="Payment confirmed by NPCI Simulator switch",
                            created_at=tx.created_at + timedelta(seconds=5),
                        ))

                # Also create non-SUCCESS transactions for realism (FAILED, PENDING, TIMEOUT, etc.)
                if i % 7 == 0:
                    scenario_choice = random.choice([
                        ("FAILED", TransactionStatus.FAILED, "BANK_DECLINED: Insufficient balance"),
                        ("TIMEOUT", TransactionStatus.FAILED, "provider_timeout"),
                        ("PENDING", TransactionStatus.PENDING, "Awaiting customer UPI PIN authorization"),
                    ])
                    fail_tx = PaymentTransaction(
                        merchant_id=apex_merchant.id,
                        invoice_id=invoice.id,
                        customer_id=customer.id,
                        amount=Decimal("1500.00"),
                        currency="INR",
                        status=scenario_choice[1],
                        payment_method=PaymentMethod.UPI_INTENT,
                        failure_reason=scenario_choice[2] if scenario_choice[1] == TransactionStatus.FAILED else None,
                        idempotency_key=f"idemp-fail-{uuid.uuid4().hex[:8]}",
                        provider_ref_id=f"MOCK-ERR-{uuid.uuid4().hex[:8].upper()}",
                        created_at=created_date + timedelta(minutes=2),
                    )
                    db.add(fail_tx)
                    db.flush()
                    all_transactions.append(fail_tx)

            db.commit()

        # Ensure all_transactions is loaded from DB
        all_transactions = db.query(PaymentTransaction).filter(PaymentTransaction.merchant_id == apex_merchant.id).all()


        # -------------------------------------------------------------
        # 6. Refunds against SUCCESS transactions
        # -------------------------------------------------------------
        print("[SEED] Creating Refunds...")
        success_txs = [t for t in all_transactions if t.status == TransactionStatus.SUCCESS]
        if success_txs:
            for r_idx, tx in enumerate(success_txs[:4]):
                refund_amt = (tx.amount * Decimal("0.5")).quantize(Decimal("0.01"))
                r_status = RefundStatus.SUCCESS if r_idx < 3 else RefundStatus.INITIATED
                refund = Refund(
                    merchant_id=tx.merchant_id,
                    transaction_id=tx.id,
                    amount=refund_amt,
                    status=r_status,
                    reason="Customer returned merchandise / sizing exchange",
                    provider_refund_id=f"MOCK-REFUND-{uuid.uuid4().hex[:8].upper()}" if r_status == RefundStatus.SUCCESS else None,
                    completed_at=now - timedelta(days=2) if r_status == RefundStatus.SUCCESS else None,
                    created_at=now - timedelta(days=3),
                )
                db.add(refund)
                db.flush()

                if r_status == RefundStatus.SUCCESS:
                    tx.status = TransactionStatus.PARTIALLY_REFUNDED
                    db.add(TransactionStatusHistory(
                        transaction_id=tx.id,
                        from_status=TransactionStatus.SUCCESS.value,
                        to_status=TransactionStatus.PARTIALLY_REFUNDED.value,
                        reason=f"Partial refund of INR {refund_amt} processed",
                        created_at=now - timedelta(days=2),
                    ))
        db.commit()

        # -------------------------------------------------------------
        # 7. Duplicate Flags & Risk Signals
        # -------------------------------------------------------------
        print("[SEED] Creating Duplicate Flags & Risk Signals...")
        if len(success_txs) >= 2:
            db.add(
                DuplicateTransactionFlag(
                    merchant_id=apex_merchant.id,
                    original_transaction_id=success_txs[0].id,
                    duplicate_transaction_id=success_txs[1].id,
                    flag_reason=DuplicateFlagReason.IDENTICAL_IDEMPOTENCY_KEY,
                    status=DuplicateFlagStatus.RESOLVED,
                    match_reason="Rapid replay of identical idempotency token at checkout. Refund processed for duplicate.",
                    resolved_at=now - timedelta(days=1),
                )
            )

        db.add(
            RiskSignal(
                merchant_id=apex_merchant.id,
                transaction_id=success_txs[0].id if success_txs else None,
                risk_score=Decimal("45.00"),
                risk_level=RiskLevel.MEDIUM,
                rule_triggered="RAPID_SUCCESSION_PAYMENTS",
                action_taken=RiskAction.ALLOW,
                metadata_json={
                    "velocity_count": 4,
                    "window_seconds": 60,
                    "reason": "4 consecutive payments from same VPA within 60 seconds",
                },
                created_at=now - timedelta(hours=6),
            )
        )
        db.add(
            RiskSignal(
                merchant_id=apex_merchant.id,
                transaction_id=success_txs[1].id if len(success_txs) > 1 else None,
                risk_score=Decimal("85.00"),
                risk_level=RiskLevel.HIGH,
                rule_triggered="SPLIT_STRUCTURING_ATTEMPT",
                action_taken=RiskAction.FLAG_FOR_REVIEW,
                is_reviewed=True,
                resolution_note="Flagged for AML compliance inspection",
                metadata_json={
                    "pattern": "Repeated INR 99,000 splits just beneath 100,000 reporting threshold",
                    "action_taken": "Flagged for AML compliance inspection",
                },
                created_at=now - timedelta(days=1),
            )
        )
        db.commit()


        # -------------------------------------------------------------
        # 8. Reconciliation Batch & Entries
        # -------------------------------------------------------------
        print("[SEED] Creating Reconciliation Batches & Entries...")
        recon_batch = ReconciliationBatch(
            merchant_id=apex_merchant.id,
            batch_date=(now - timedelta(days=1)).date(),
            period_start=now - timedelta(days=2),
            period_end=now - timedelta(days=1),
            status=ReconciliationStatus.MATCHED,
            total_records=len(success_txs[:5]),
            matched_records=len(success_txs[:5]),
            mismatched_records=0,
            discrepancy_count=0,
            mdr_rate=Decimal("0.015"),
        )
        db.add(recon_batch)
        db.flush()

        for s_tx in success_txs[:5]:
            exp_net = (s_tx.amount * Decimal("0.985")).quantize(Decimal("0.01"))
            db.add(
                ReconciliationEntry(
                    batch_id=recon_batch.id,
                    transaction_id=s_tx.id,
                    expected_amount=exp_net,
                    actual_amount=exp_net,
                    match_status=MatchStatus.MATCHED,
                    status=ReconciliationEntryStatus.MATCHED,
                    notes="Direct match against mock UPI settlement",
                )
            )
        db.commit()

        # -------------------------------------------------------------
        # 9. Settlements & SettlementLineItems
        # -------------------------------------------------------------
        print("[SEED] Creating Settlement Batches...")
        settled_txs = success_txs[:5]
        gross_total = sum(t.amount for t in settled_txs)
        deduction = (gross_total * Decimal("0.015")).quantize(Decimal("0.01"))
        net_settled = gross_total - deduction

        settlement = Settlement(
            merchant_id=apex_merchant.id,
            reconciliation_batch_id=recon_batch.id,
            settlement_date=(now - timedelta(days=1)).date(),
            settlement_cycle=SettlementCycle.T_PLUS_1,
            transaction_count=len(settled_txs),
            gross_amount=gross_total,
            mdr_amount=deduction,
            tax_on_mdr=Decimal("0.00"),
            deduction_amount=deduction,
            net_amount=net_settled,
            status=SettlementStatus.SETTLED,
            bank_account_ref="HDFC_00492817293",
            utr_reference=f"UTR{uuid.uuid4().int % 1000000000000:012d}",
            settled_at=now - timedelta(days=1),
        )
        db.add(settlement)
        db.flush()

        for st_tx in settled_txs:
            fee = (st_tx.amount * Decimal("0.015")).quantize(Decimal("0.01"))
            db.add(
                SettlementLineItem(
                    settlement_id=settlement.id,
                    transaction_id=st_tx.id,
                    amount=st_tx.amount,
                    fee_amount=fee,
                    tax_amount=Decimal("0.00"),
                    net_amount=st_tx.amount - fee,
                )
            )
        db.commit()


        # -------------------------------------------------------------
        # 10. Operational Notifications & Audit Logs
        # -------------------------------------------------------------
        print("[SEED] Creating In-App Notifications & Audit Logs...")
        sample_notifs = [
            ("Daily Settlement Credited", f"INR {net_settled} settled to HDFC Bank (UTR: {settlement.utr_reference}).", True),
            ("High Velocity Alert", "Multiple rapid payment attempts detected on Bandra store POS.", False),
            ("Partial Refund Completed", "Refund of INR 1,200.00 credited back to customer source VPA.", True),
            ("Nightly Reconciliation Complete", "All 5 records matched bank statement with zero discrepancy.", True),
        ]
        for title, content, is_read in sample_notifs:
            db.add(
                Notification(
                    merchant_id=apex_merchant.id,
                    recipient=apex_merchant.email,
                    channel=NotificationChannel.IN_APP,
                    title=title,
                    content=content,
                    status=NotificationStatus.SENT,
                    is_read=is_read,
                    sent_at=now - timedelta(hours=random.randint(1, 48)),
                )
            )

        # Audit Logs
        db.add(
            AuditLog(
                merchant_id=apex_merchant.id,
                user_id=demo_users["Owner"].id,
                action=AuditAction.CREATE,
                entity_name="settlements",
                entity_id=settlement.id,
                ip_address="127.0.0.1",
                changes={"amount": str(net_settled), "status": "SETTLED"},
            )
        )
        db.add(
            AuditLog(
                merchant_id=apex_merchant.id,
                user_id=demo_users["Manager"].id,
                action=AuditAction.UPDATE,
                entity_name="stores",
                entity_id=primary_store.id,
                ip_address="127.0.0.1",
                changes={"name": primary_store.name, "is_active": True},
            )
        )
        db.commit()


        print("[SEED] Seeding completed successfully!")
        print(f"[SEED] Demo Owner Credentials:   owner@payflow.demo   / Password123!")
        print(f"[SEED] Demo Manager Credentials: manager@payflow.demo / Password123!")
        print(f"[SEED] Demo Cashier Credentials: cashier@payflow.demo / Password123!")
        print(f"[SEED] Demo Auditor Credentials: auditor@payflow.demo / Password123!")

    except Exception as exc:
        db.rollback()
        print(f"[SEED] ERROR during database seeding: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
