"""RBAC Default Permissions and Role Seeding.

===========================================================================================
DEFAULT RBAC PERMISSION MATRIX:
===========================================================================================
Resource      Permission Code     Owner          Manager        Cashier        Auditor
===========================================================================================
Invoices      invoices:read       YES            YES            YES            YES
              invoices:write      YES            YES            YES            NO
Payments      payments:read       YES            YES            YES            YES
              payments:write      YES            YES            YES            NO
Refunds       refunds:read        YES            YES            NO             YES
              refunds:write       YES            YES            NO             NO
Settlements   settlements:read    YES            YES            NO             YES
              settlements:write   YES            NO             NO             NO
Staff         staff:read          YES            YES            NO             YES
              staff:write         YES            YES            NO             NO
Audit Logs    audit:read          YES            NO             NO             YES
              audit:write         NO (immutable) NO (immutable) NO (immutable) NO (immutable)
===========================================================================================

Role Capabilities:
- Owner: Full administrative and financial authority over the merchant organization.
- Manager: Store-level operational authority for invoicing, payment acceptance, refunds,
  and staff management; read-only access to settlement data and audit logs.
- Cashier: Frontline checkout authority. Can generate invoices and collect payments.
  Cannot trigger refunds, manage staff, or inspect settlements/audits.
- Auditor: Comprehensive read-only inspection access across all operational, financial,
  and audit records for compliance reviews.
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from app.modules.rbac.models import Permission, Role, RolePermission

DEFAULT_PERMISSIONS = [
    # Invoices
    ("invoices:read", "Read Invoices", "View merchant bills and invoice details"),
    ("invoices:write", "Write Invoices", "Create, edit, and cancel merchant invoices"),
    # Payments
    ("payments:read", "Read Payments", "View transaction history and payment statuses"),
    ("payments:write", "Write Payments", "Initiate payments, collect requests, and QR codes"),
    # Refunds
    ("refunds:read", "Read Refunds", "View refund requests and reversal statuses"),
    ("refunds:write", "Write Refunds", "Initiate customer transaction refunds"),
    ("refunds:approve", "Approve Refunds", "Approve initiated refunds and trigger settlement reversal (Manager/Owner only)"),
    # Settlements
    ("settlements:read", "Read Settlements", "Inspect merchant payout records and line items"),
    ("settlements:write", "Write Settlements", "Configure bank accounts and trigger on-demand payouts"),
    # Staff
    ("staff:read", "Read Staff", "View merchant store staff members and role assignments"),
    ("staff:write", "Write Staff", "Invite, assign, and deactivate merchant staff accounts"),
    # Customers
    ("customers:read", "Read Customers", "View merchant customer profiles and directories"),
    ("customers:write", "Write Customers", "Create, edit, and manage merchant customer profiles"),
    # Audit Logs
    ("audit:read", "Read Audit Logs", "Inspect immutable platform security and state audit trails"),
]

ROLE_PERMISSION_MAP: Dict[str, List[str]] = {
    "Owner": [
        "invoices:read",
        "invoices:write",
        "payments:read",
        "payments:write",
        "refunds:read",
        "refunds:write",
        "refunds:approve",
        "settlements:read",
        "settlements:write",
        "staff:read",
        "staff:write",
        "customers:read",
        "customers:write",
        "audit:read",
    ],
    "Manager": [
        "invoices:read",
        "invoices:write",
        "payments:read",
        "payments:write",
        "refunds:read",
        "refunds:write",
        "refunds:approve",
        "settlements:read",
        "staff:read",
        "staff:write",
        "customers:read",
        "customers:write",
    ],
    "Cashier": [
        "invoices:read",
        "invoices:write",
        "payments:read",
        "payments:write",
        "customers:read",
        "settlements:read",
    ],
    "Auditor": [
        "invoices:read",
        "payments:read",
        "refunds:read",
        "settlements:read",
        "staff:read",
        "customers:read",
        "audit:read",
    ],
}


def seed_rbac_data(db: Session) -> Dict[str, Role]:
    """Idempotently seeds standard roles, permissions, and role-permission bindings."""
    # 1. Upsert Permissions
    perm_objects: Dict[str, Permission] = {}
    for code, name, desc in DEFAULT_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.code == code).first()
        if not perm:
            perm = Permission(code=code, name=name, description=desc)
            db.add(perm)
            db.flush()
        perm_objects[code] = perm

    # 2. Upsert Roles and Bindings
    roles: Dict[str, Role] = {}
    for role_name, allowed_perms in ROLE_PERMISSION_MAP.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(
                name=role_name,
                description=f"Standard PayFlow {role_name} role",
                is_system_role=True,
            )
            db.add(role)
            db.flush()
        roles[role_name] = role

        for perm_code in allowed_perms:
            perm = perm_objects[perm_code]
            binding = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
                .first()
            )
            if not binding:
                binding = RolePermission(role_id=role.id, permission_id=perm.id)
        # Remove obsolete bindings for this role if any
        allowed_perm_ids = [perm_objects[c].id for c in allowed_perms]
        if allowed_perm_ids:
            db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                ~RolePermission.permission_id.in_(allowed_perm_ids),
            ).delete(synchronize_session=False)

    db.commit()
    return roles
