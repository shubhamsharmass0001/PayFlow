from typing import Optional
from fastapi import Header, HTTPException, status


async def get_idempotency_key(
    idempotency_key: Optional[str] = Header(
        None,
        alias="Idempotency-Key",
        description="Unique key to prevent duplicate processing of requests",
    ),
) -> Optional[str]:
    """Dependency to retrieve and validate the optional or required Idempotency-Key header."""
    return idempotency_key


def require_idempotency_key(
    idempotency_key: Optional[str] = Header(
        None,
        alias="Idempotency-Key",
        description="Unique key required to prevent duplicate processing of requests",
    ),
) -> str:
    """Dependency ensuring Idempotency-Key header is present on mutating endpoints."""
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required for this operation.",
        )
    return idempotency_key
