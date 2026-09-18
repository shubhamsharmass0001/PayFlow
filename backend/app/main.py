from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware
import os
from starlette.staticfiles import StaticFiles

import app.db.base  # noqa: F401 Ensure all models are registered cleanly before router imports
from app.modules.auth.routes import router as auth_router
from app.modules.customers.routes import router as customers_router
from app.modules.invoices.routes import router as invoices_router
from app.modules.merchants.routes import router as merchants_router
from app.modules.mock_upi_provider.routes import router as mock_upi_router
from app.modules.payments.routes import router as payments_router
from app.modules.payment_links.routes import router as payment_links_router
from app.modules.payment_requests.routes import router as payment_requests_router
from app.modules.rbac.routes import router as rbac_router
from app.modules.reconciliation.routes import router as reconciliation_router
from app.modules.refunds.routes import router as refunds_router
from app.modules.settlements.routes import router as settlements_router
from app.modules.splits.routes import router as splits_router
from app.modules.stores.routes import router as stores_router
from app.modules.webhooks.routes import router as webhooks_router
from app.modules.duplicate_detection.routes import router as duplicate_detection_router
from app.modules.analytics.routes import router as analytics_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.audit.routes import router as audit_router
from app.modules.risk.routes import router as risk_router
from app.modules.ai_assistant.routes import router as ai_assistant_router
from app.shared.exceptions import PayFlowException

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    setup_logging()
    logger.info(
        "app_startup",
        app_name=settings.PROJECT_NAME,
        env=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    yield
    # Shutdown actions
    logger.info("app_shutdown", app_name=settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom Middlewares
app.add_middleware(RequestLoggingMiddleware)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ==============================================================================
# Global Exception Handlers (Consistent JSON Error Envelope)
# ==============================================================================

@app.exception_handler(PayFlowException)
async def payflow_exception_handler(request: Request, exc: PayFlowException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error.get("loc", []))
        formatted_errors.append({
            "location": loc,
            "message": error.get("msg"),
            "type": error.get("type"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "The submitted payload failed validation checks.",
            "details": {"errors": formatted_errors},
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": {},
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_server_exception", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred. Please contact support.",
            "details": {},
        },
    )


# ==============================================================================
# Routers & Static File Registration
# ==============================================================================

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(rbac_router, prefix=settings.API_V1_STR)
app.include_router(merchants_router, prefix=settings.API_V1_STR)
app.include_router(stores_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(invoices_router, prefix=settings.API_V1_STR)
app.include_router(payment_requests_router, prefix=settings.API_V1_STR)
app.include_router(payment_links_router, prefix=settings.API_V1_STR)
app.include_router(payment_links_router)  # Also expose /pay/{slug} directly at root for clean customer checkout URLs
app.include_router(mock_upi_router, prefix=settings.API_V1_STR)
app.include_router(payments_router, prefix=settings.API_V1_STR)
app.include_router(payments_router)
app.include_router(splits_router, prefix=settings.API_V1_STR)
app.include_router(splits_router)
app.include_router(webhooks_router, prefix=settings.API_V1_STR)
app.include_router(webhooks_router)
app.include_router(reconciliation_router, prefix=settings.API_V1_STR)
app.include_router(reconciliation_router)
app.include_router(duplicate_detection_router, prefix=settings.API_V1_STR)
app.include_router(duplicate_detection_router)
app.include_router(refunds_router, prefix=settings.API_V1_STR)
app.include_router(refunds_router)
app.include_router(settlements_router, prefix=settings.API_V1_STR)
app.include_router(settlements_router)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(audit_router)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(risk_router)
app.include_router(ai_assistant_router, prefix=settings.API_V1_STR)
app.include_router(ai_assistant_router)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }
