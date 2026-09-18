"""Authentication module providing user registration, JWT generation, and token rotation."""
from app.modules.auth.routes import router as auth_router

__all__ = ["auth_router"]
