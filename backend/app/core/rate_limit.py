import logging
from typing import Optional
import redis
from app.core.config import settings
from app.shared.exceptions import RateLimitExceededException

logger = logging.getLogger("payflow.rate_limit")

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    global _redis_client
    if _redis_client is None and settings.REDIS_URL:
        try:
            _redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )
        except Exception as exc:
            logger.warning(f"Could not connect to Redis for rate limiting: {exc}")
            return None
    return _redis_client


def check_login_rate_limit(
    client_ip: str,
    identifier: str,
    max_attempts: int = 5,
    window_seconds: int = 900,  # 15 minutes
    redis_conn: Optional[redis.Redis] = None,
) -> None:
    """Enforces rate limiting on login attempts per IP + phone/email.

    Raises RateLimitExceededException (HTTP 429) if exceeded.
    """
    client = redis_conn or get_redis_client()
    if client is None:
        return

    key = f"payflow:ratelimit:login:{client_ip}:{identifier}"
    try:
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        attempts, ttl = pipe.execute()

        if attempts == 1 or ttl == -1:
            client.expire(key, window_seconds)
            ttl = window_seconds

        if attempts > max_attempts:
            raise RateLimitExceededException(
                message=f"Too many failed login attempts. Please wait {ttl} seconds before trying again.",
                code="AUTH_RATE_LIMIT_EXCEEDED",
                details={
                    "max_attempts": max_attempts,
                    "attempts": attempts,
                    "retry_after_seconds": max(ttl, 1),
                },
            )
    except RateLimitExceededException:
        raise
    except Exception as exc:
        # Graceful degradation if Redis fails
        logger.warning(f"Redis rate limiting error, allowing request: {exc}")


def check_rate_limit(
    key: str,
    max_requests: int = 60,
    window_seconds: int = 60,
    error_message: str = "Rate limit exceeded. Please try again later.",
    error_code: str = "RATE_LIMIT_EXCEEDED",
    redis_conn: Optional[redis.Redis] = None,
) -> None:
    """Generic rate limiter using Redis INCR + EXPIRE.

    Raises RateLimitExceededException (HTTP 429) if exceeded.
    """
    client = redis_conn or get_redis_client()
    if client is None:
        return

    full_key = f"payflow:ratelimit:{key}"
    try:
        pipe = client.pipeline()
        pipe.incr(full_key)
        pipe.ttl(full_key)
        attempts, ttl = pipe.execute()

        if attempts == 1 or ttl == -1:
            client.expire(full_key, window_seconds)
            ttl = window_seconds

        if attempts > max_requests:
            raise RateLimitExceededException(
                message=f"{error_message} Retry in {ttl} seconds.",
                code=error_code,
                details={
                    "max_requests": max_requests,
                    "attempts": attempts,
                    "retry_after_seconds": max(ttl, 1),
                },
            )
    except RateLimitExceededException:
        raise
    except Exception as exc:
        logger.warning(f"Redis rate limiting error, allowing request: {exc}")


def rate_limit_dependency(
    max_requests: int = 60,
    window_seconds: int = 60,
    key_prefix: str = "public",
):
    """FastAPI dependency to rate limit public endpoints by client IP."""
    from fastapi import Request

    def dependency(request: Request):
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client and request.client.host:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        endpoint = request.url.path
        key = f"{key_prefix}:{endpoint}:{client_ip}"
        check_rate_limit(
            key=key,
            max_requests=max_requests,
            window_seconds=window_seconds,
            error_message="Too many requests for this endpoint.",
            error_code="RATE_LIMIT_EXCEEDED",
        )

    return dependency

