"""Role-Based Access Control (RBAC) Module."""
from app.modules.rbac.dependencies import require_permission
from app.modules.rbac.routes import router as rbac_router
from app.modules.rbac.seed import seed_rbac_data

__all__ = ["require_permission", "rbac_router", "seed_rbac_data"]
