"""
BlackRoad SDK Exceptions
"""


class BlackRoadError(Exception):
    """Base exception for BlackRoad SDK errors."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class AuthenticationError(BlackRoadError):
    """Raised when API authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTH_ERROR")


class RateLimitError(BlackRoadError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message, code="RATE_LIMIT")
        self.retry_after = retry_after


class NotFoundError(BlackRoadError):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND")


class ValidationError(BlackRoadError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Validation failed", errors: list = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.errors = errors or []


class ConnectionError(BlackRoadError):
    """Raised when connection to API fails."""

    def __init__(self, message: str = "Connection failed"):
        super().__init__(message, code="CONNECTION_ERROR")


class TimeoutError(BlackRoadError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, code="TIMEOUT")
