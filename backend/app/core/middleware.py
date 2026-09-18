import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog
from jose import jwt

logger = structlog.get_logger("payflow.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Best-effort extraction of merchant_id from headers or query parameters
        merchant_id = (
            request.headers.get("X-Merchant-ID")
            or request.query_params.get("merchant_id")
            or getattr(request.state, "merchant_id", None)
        )

        # Best-effort extraction of user_id from Authorization header if present
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                try:
                    unverified_claims = jwt.get_unverified_claims(auth_header.split(" ")[1])
                    user_id = unverified_claims.get("sub")
                except Exception:
                    pass

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            user_id=str(user_id) if user_id else None,
            merchant_id=str(merchant_id) if merchant_id else None,
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            latency_ms = round(process_time * 1000, 2)

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"

            # Check if user_id or merchant_id was populated on request.state during execution
            final_user_id = getattr(request.state, "user_id", user_id)
            final_merchant_id = getattr(request.state, "merchant_id", merchant_id)

            logger.info(
                "request_completed",
                request_id=request_id,
                user_id=str(final_user_id) if final_user_id else None,
                merchant_id=str(final_merchant_id) if final_merchant_id else None,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )
            return response
        except Exception as exc:
            process_time = time.perf_counter() - start_time
            latency_ms = round(process_time * 1000, 2)
            logger.error(
                "request_failed",
                request_id=request_id,
                user_id=str(user_id) if user_id else None,
                merchant_id=str(merchant_id) if merchant_id else None,
                method=request.method,
                path=request.url.path,
                error=str(exc),
                latency_ms=latency_ms,
            )
            raise exc
