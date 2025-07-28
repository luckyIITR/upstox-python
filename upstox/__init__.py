"""
Upstox Python Client Library

A Python client library for the Upstox API that provides easy access to trading,
portfolio management, and market data functionality.

For more information, visit: https://upstox.com/developer/api-documentation/open-api
"""

from .upstox import Upstox
from .exceptions import (
    UpstoxException,
    TokenException,
    OrderException,
    PermissionException,
    InputException,
    NetworkException,
    DataException,
)

__version__ = "1.0.0"
__author__ = "Upstox Python Client"
__email__ = "support@upstox.com"

__all__ = [
    "Upstox",
    "UpstoxException",
    "TokenException",
    "OrderException",
    "PermissionException",
    "InputException",
    "NetworkException",
    "DataException",
]
