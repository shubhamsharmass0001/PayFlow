from typing import Any, Dict, Optional
from fastapi import status


class PayFlowException(Exception):
    """Base exception for all PayFlow application errors returning a consistent JSON envelope:

    {
        "code": "ERROR_CODE",
        "message": "Human-readable description",
        "details": {}
    }
    """

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_SERVER_ERROR",
        message: str = "An unexpected error occurred",
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        self.headers = headers or {}


class UnauthorizedException(PayFlowException):
    def __init__(
        self,
        message: str = "Could not validate credentials",
        code: str = "UNAUTHORIZED",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=code,
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(PayFlowException):
    def __init__(
        self,
        message: str = "Not enough permissions to perform this action",
        code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code=code,
            message=message,
            details=details,
        )


class RateLimitExceededException(PayFlowException):
    def __init__(
        self,
        message: str = "Too many requests. Please try again later.",
        code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code=code,
            message=message,
            details=details,
        )


class EntityNotFoundException(PayFlowException):
    def __init__(
        self,
        entity_name: str,
        entity_id: Any,
        code: str = "NOT_FOUND",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
            message=f"{entity_name} with id '{entity_id}' was not found.",
            details={"entity": entity_name, "id": str(entity_id)},
        )


class ConflictException(PayFlowException):
    def __init__(
        self,
        message: str = "Resource conflict occurred",
        code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=code,
            message=message,
            details=details,
        )


class BadRequestException(PayFlowException):
    def __init__(
        self,
        message: str = "Invalid request payload or parameters",
        code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=code,
            message=message,
            details=details,
        )


class IdempotencyViolationException(PayFlowException):
    def __init__(
        self,
        message: str = "Duplicate request detected for idempotency key",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="IDEMPOTENCY_CONFLICT",
            message=message,
            details=details,
        )
