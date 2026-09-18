"""Merchants module providing onboarding, KYC uploads, profile management, and staff assignments."""
from app.modules.merchants.routes import router as merchants_router

__all__ = ["merchants_router"]
