"""
Exceptions raised by the Upstox client.

This module contains custom exception classes for different error scenarios
that may occur when using the Upstox API.
"""


class UpstoxException(Exception):
    """Base exception class for all Upstox API errors."""

    def __init__(self, message, code=None, status_code=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        if self.code:
            return f"{self.message} (Code: {self.code})"
        return self.message


class TokenException(UpstoxException):
    """Raised when there are authentication or token-related errors."""

    pass


class OrderException(UpstoxException):
    """Raised when there are order-related errors."""

    pass


class PermissionException(UpstoxException):
    """Raised when the user doesn't have permission to perform an action."""

    pass


class InputException(UpstoxException):
    """Raised when there are input validation errors."""

    pass


class NetworkException(UpstoxException):
    """Raised when there are network-related errors."""

    pass


class DataException(UpstoxException):
    """Raised when there are data-related errors."""

    pass


class RateLimitException(UpstoxException):
    """Raised when API rate limits are exceeded."""

    pass


class ValidationException(InputException):
    """Raised when input validation fails."""

    pass


class ConfigurationException(UpstoxException):
    """Raised when there are configuration-related errors."""

    pass
