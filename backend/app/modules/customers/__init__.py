"""Customers module."""

from app.modules.customers.models import Customer
from app.modules.customers.routes import router as customers_router

__all__ = ["Customer", "customers_router"]
