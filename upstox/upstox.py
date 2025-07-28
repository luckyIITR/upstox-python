"""
Main Upstox client class.

This module contains the main Upstox client class that provides access to all
Upstox API functionality including authentication, trading, portfolio management,
and market data.
"""

import json
import logging
import requests
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode

from .exceptions import (
    UpstoxException,
    TokenException,
    OrderException,
    PermissionException,
    InputException,
    NetworkException,
    DataException,
    RateLimitException,
)


class Upstox:
    """
    Main Upstox client class.

    This class provides access to all Upstox API functionality including
    authentication, trading, portfolio management, and market data.
    """

    # API endpoints
    BASE_URL = "https://api.upstox.com/v2"
    BASE_URL_V3 = "https://api.upstox.com/v3"
    BASE_URL_HFT = "https://api-hft.upstox.com/v3"
    LOGIN_URL = "https://api.upstox.com/v2/login/authorization/dialog"
    TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"

    # Order types
    ORDER_TYPE_MARKET = "market"
    ORDER_TYPE_LIMIT = "limit"
    ORDER_TYPE_STOP_LOSS = "stop_loss"
    ORDER_TYPE_STOP_LOSS_MARKET = "stop_loss_market"

    # Transaction types
    TRANSACTION_TYPE_BUY = "buy"
    TRANSACTION_TYPE_SELL = "sell"

    # Product types
    PRODUCT_CNC = "cnc"  # Cash and Carry
    PRODUCT_MIS = "mis"  # Margin Intraday Square Off
    PRODUCT_NRML = "nrml"  # Normal
    PRODUCT_CO = "co"  # Cover Order
    PRODUCT_BO = "bo"  # Bracket Order

    # Validity types
    VALIDITY_DAY = "day"
    VALIDITY_IOC = "ioc"  # Immediate or Cancel
    VALIDITY_FOK = "fok"  # Fill or Kill

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_MCX = "MCX"

    # Historical Data V3 Units
    UNIT_MINUTES = "minutes"
    UNIT_HOURS = "hours"
    UNIT_DAYS = "days"
    UNIT_WEEKS = "weeks"
    UNIT_MONTHS = "months"

    # Historical Data V3 Intervals
    # Minutes: 1-300
    # Hours: 1-5
    # Days, Weeks, Months: 1

    def __init__(
        self,
        api_key: str,
        access_token: Optional[str] = None,
        timeout: int = 30,
        debug: bool = False,
    ):
        """
        Initialize the Upstox client.

        Args:
            api_key: Your Upstox API key
            access_token: Access token for authenticated requests
            timeout: Request timeout in seconds
            debug: Enable debug logging
        """
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout
        self.debug = debug

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        self.logger = logging.getLogger(__name__)

        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Upstox-Python/1.0.0",
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

        if access_token:
            self.set_access_token(access_token)

    def set_access_token(self, access_token: str) -> None:
        """
        Set the access token for authenticated requests.

        Args:
            access_token: The access token to use
        """
        self.access_token = access_token
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def get_login_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Get the login URL for OAuth2 authentication.

        Args:
            redirect_uri: The redirect URI registered with Upstox
            state: Optional state parameter for security

        Returns:
            The login URL to redirect users to
        """
        params = {
            "client_id": self.api_key,
            "redirect_uri": redirect_uri,
            "response_type": "code",
        }

        if state:
            params["state"] = state

        return f"{self.LOGIN_URL}?{urlencode(params)}"

    def generate_session(
        self, authorization_code: str, api_secret: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Generate session using authorization code.

        Args:
            authorization_code: The authorization code received from login
            api_secret: Your Upstox API secret
            redirect_uri: The redirect URI used during login (must match the one used in get_login_url)

        Returns:
            Dictionary containing access_token and other session data

        Raises:
            TokenException: If authentication fails
        """
        data = {
            "code": authorization_code,
            "client_id": self.api_key,
            "client_secret": api_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            # print(data)
            response = self.session.post(
                self.TOKEN_URL, data=data, timeout=self.timeout
            )
            response.raise_for_status()

            session_data = response.json()

            if "access_token" in session_data:
                self.set_access_token(session_data["access_token"])
                return session_data
            else:
                raise TokenException("No access token in response")

        except requests.exceptions.RequestException as e:
            raise TokenException(f"Failed to generate session: {str(e)}")

    def generate_extended_token(
        self, authorization_code: str, api_secret: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Generate extended token for long-term read-only access.

        Extended tokens are valid for one year and can be used for read-only API calls:
        - Get Positions
        - Get Holdings
        - Get Order Details
        - Get Order History
        - Get Order Book

        Note: Extended tokens are available for multi-client applications upon request.
        Contact Upstox support for enrollment.

        Args:
            authorization_code: The authorization code received from login
            api_secret: Your Upstox API secret
            redirect_uri: The redirect URI used during login

        Returns:
            Dictionary containing extended_token and other session data

        Raises:
            TokenException: If authentication fails
        """
        data = {
            "code": authorization_code,
            "client_id": self.api_key,
            "client_secret": api_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "token_type": "extended",
        }

        try:
            response = self.session.post(
                self.TOKEN_URL, data=data, timeout=self.timeout
            )
            response.raise_for_status()

            session_data = response.json()

            if "extended_token" in session_data:
                return session_data
            else:
                raise TokenException("No extended token in response")

        except requests.exceptions.RequestException as e:
            raise TokenException(f"Failed to generate extended token: {str(e)}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the Upstox API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests

        Returns:
            API response data (extracted from response structure)

        Raises:
            Various UpstoxException subclasses based on error type
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)

            if self.debug:
                self.logger.debug(f"{method} {url} - Status: {response.status_code}")

            # Handle rate limiting
            if response.status_code == 429:
                raise NetworkException("Rate limit exceeded")

            # Handle authentication errors
            if response.status_code == 401:
                raise TokenException("Invalid or expired access token")

            # Handle permission errors
            if response.status_code == 403:
                raise PermissionException("Insufficient permissions")

            # Handle validation errors
            if response.status_code == 400:
                raise InputException("Invalid request parameters")

            # Handle server errors
            if response.status_code >= 500:
                raise NetworkException(f"Server error: {response.status_code}")

            response.raise_for_status()

            # Parse response according to Upstox response structure
            response_data = response.json()

            # Handle standardized response structure
            if isinstance(response_data, dict):
                status = response_data.get("status")

                if status == "success":
                    # Return the data portion of success response
                    return response_data.get("data", response_data)
                elif status == "error":
                    # Handle error response structure
                    errors = response_data.get("errors", [])
                    if errors:
                        error = errors[0]  # Get first error
                        error_code = error.get("error_code")
                        message = error.get("message", "Unknown error")
                        property_path = error.get("property_path")
                        invalid_value = error.get("invalid_value")

                        # Map error codes to specific exceptions
                        if error_code in ["UDAPI1021", "UDAPI100011"]:
                            raise InputException(f"{message} (Code: {error_code})")
                        elif error_code in [
                            "UDAPI1015",
                            "UDAPI1146",
                            "UDAPI1147",
                            "UDAPI1148",
                        ]:
                            raise InputException(f"{message} (Code: {error_code})")
                        elif error_code in ["UDAPI1022"]:
                            raise InputException(f"{message} (Code: {error_code})")
                        else:
                            raise UpstoxException(f"{message} (Code: {error_code})")
                    else:
                        raise UpstoxException("Unknown error occurred")
                else:
                    # If no status field, return as-is (backward compatibility)
                    return response_data

            # If response is not a dict, return as-is
            return response_data

        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Request failed: {str(e)}")

    def _make_request_v3(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the Upstox V3 API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            API response data (extracted from response structure)

        Raises:
            Various UpstoxException subclasses based on error type

        Note:
            This method uses the V3 base URL (https://api.upstox.com/v3)
            and follows the same error handling and response parsing as _make_request.
        """
        url = f"{self.BASE_URL_V3}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)

            if self.debug:
                self.logger.debug(f"{method} {url} - Status: {response.status_code}")

            # Handle rate limiting
            if response.status_code == 429:
                raise NetworkException("Rate limit exceeded")

            # Handle authentication errors
            if response.status_code == 401:
                raise TokenException("Invalid or expired access token")

            # Handle permission errors
            if response.status_code == 403:
                raise PermissionException("Insufficient permissions")

            # Handle validation errors
            if response.status_code == 400:
                raise InputException("Invalid request parameters")

            # Handle server errors
            if response.status_code >= 500:
                raise NetworkException(f"Server error: {response.status_code}")

            response.raise_for_status()

            # Parse response according to Upstox response structure
            response_data = response.json()

            # Handle standardized response structure
            if isinstance(response_data, dict):
                status = response_data.get("status")

                if status == "success":
                    # Return the data portion of success response
                    return response_data.get("data", response_data)
                elif status == "error":
                    # Handle error response structure
                    errors = response_data.get("errors", [])
                    if errors:
                        error = errors[0]  # Get first error
                        error_code = error.get("error_code")
                        message = error.get("message", "Unknown error")
                        property_path = error.get("property_path")
                        invalid_value = error.get("invalid_value")

                        # Map V3 specific error codes
                        if error_code in [
                            "UDAPI1021",
                            "UDAPI100011",
                            "UDAPI1015",
                            "UDAPI1146",
                            "UDAPI1147",
                            "UDAPI1148",
                        ]:
                            raise InputException(f"{message} (Code: {error_code})")
                        else:
                            raise UpstoxException(f"{message} (Code: {error_code})")
                    else:
                        raise UpstoxException("Unknown error occurred")
                else:
                    # If no status field, return as-is (backward compatibility)
                    return response_data

            # If response is not a dict, return as-is
            return response_data

        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Request failed: {str(e)}")

    def _make_request_hft(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the Upstox HFT API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            API response data (extracted from response structure)

        Raises:
            Various UpstoxException subclasses based on error type

        Note:
            This method uses the HFT base URL (https://api-hft.upstox.com/v3)
            and follows the same error handling and response parsing as _make_request.
        """
        url = f"{self.BASE_URL_HFT}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)

            if self.debug:
                self.logger.debug(f"{method} {url} - Status: {response.status_code}")

            # Handle rate limiting
            if response.status_code == 429:
                raise NetworkException("Rate limit exceeded")

            # Handle authentication errors
            if response.status_code == 401:
                raise TokenException("Invalid or expired access token")

            # Handle permission errors
            if response.status_code == 403:
                raise PermissionException("Insufficient permissions")

            # Handle validation errors
            if response.status_code == 400:
                raise InputException("Invalid request parameters")

            # Handle server errors
            if response.status_code >= 500:
                raise NetworkException(f"Server error: {response.status_code}")

            response.raise_for_status()

            # Parse response according to Upstox response structure
            response_data = response.json()

            # Handle standardized response structure
            if isinstance(response_data, dict):
                status = response_data.get("status")

                if status == "success":
                    # Return the data portion of success response
                    return response_data.get("data", response_data)
                elif status == "error":
                    # Handle error response structure
                    errors = response_data.get("errors", [])
                    if errors:
                        error = errors[0]  # Get first error
                        error_code = error.get("error_code")
                        message = error.get("message", "Unknown error")
                        property_path = error.get("property_path")
                        invalid_value = error.get("invalid_value")

                        # Map HFT specific error codes
                        if error_code in [
                            "UDAPI1021",
                            "UDAPI100011",
                            "UDAPI1015",
                            "UDAPI1146",
                            "UDAPI1147",
                            "UDAPI1148",
                        ]:
                            raise InputException(f"{message} (Code: {error_code})")
                        else:
                            raise UpstoxException(f"{message} (Code: {error_code})")
                    else:
                        raise UpstoxException("Unknown error occurred")
                else:
                    # If no status field, return as-is (backward compatibility)
                    return response_data

            # If response is not a dict, return as-is
            return response_data

        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Request failed: {str(e)}")

    # User Profile Methods

    def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information.

        Returns:
            User profile data
        """
        return self._make_request("GET", "/user/profile")

    def get_fund_margin(self, segment: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user funds and margin data for equity and commodity markets.

        This API retrieves user funds data including margin utilized, available margin,
        and total payin amount during the day for both equity and commodity segments.

        Args:
            segment: Optional market segment filter
                    - 'SEC' for Equity segment
                    - 'COM' for Commodity segment
                    - None for both segments (default)

        Returns:
            Dictionary containing funds and margin data for equity and commodity segments

        Example:
            ```python
            # Get funds and margin for both segments
            funds = upstox.get_fund_margin()

            # Get funds and margin for equity segment only
            equity_funds = upstox.get_fund_margin(segment='SEC')

            # Get funds and margin for commodity segment only
            commodity_funds = upstox.get_fund_margin(segment='COM')
            ```

        Response Format:
            Returns data with equity and commodity objects, each containing:
            - used_margin: Amount blocked in open orders/positions
            - payin_amount: Instant payin amount
            - span_margin: Amount blocked for SPAN margin
            - adhoc_margin: Manual payin amount
            - notional_cash: Amount maintained for withdrawal
            - available_margin: Total margin available for trading
            - exposure_margin: Amount blocked for exposure margin

        Note:
            - The Funds service is accessible from 5:30 AM to 12:00 AM IST daily
            - Service is down for maintenance from 12:00 AM to 5:30 AM IST daily
            - From 19th July 2025, combined funds for both Equity and Commodity segments
              will be returned in the 'equity' object
        """
        params = {}
        if segment:
            params["segment"] = segment

        return self._make_request("GET", "/user/get-funds-and-margin", params=params)

    # Charges Methods

    def get_charges(
        self,
        instrument_token: str,
        quantity: int,
        price: float,
        product: str,
        transaction_type: str,
    ) -> Dict[str, Any]:
        """
        Get brokerage details for an order.

        This API calculates brokerage fees associated with stock trading. It provides
        a comprehensive breakdown of total charges including taxes, other charges, and DP plan details.

        Args:
            instrument_token: Key of the instrument
            quantity: Quantity with which the order is to be placed
            price: Price with which the order is to be placed
            product: Product with which the order is to be placed
            transaction_type: Indicates whether it's a BUY or SELL order

        Returns:
            Dictionary containing detailed brokerage breakdown

        Example:
            ```python
            charges = upstox.get_charges(
                instrument_token="NSE_EQ|INE669E01016",
                quantity=100,
                price=16.8,
                product="D",
                transaction_type="BUY"
            )
            ```

        Response Format:
            Returns charges object containing:
            - total: Total charges for the order
            - brokerage: Brokerage charges
            - taxes: GST, STT, and stamp duty charges
            - other_charges: Transaction, clearing, IPF, and SEBI turnover charges
            - dp_plan: Depository Participant plan details

        Note:
            The camelCase fields (otherTaxes, dpPlan) are deprecated and will be removed
            in future versions. Use the snake_case versions for consistency.
        """
        params = {
            "instrument_token": instrument_token,
            "quantity": quantity,
            "price": price,
            "product": product,
            "transaction_type": transaction_type,
        }
        return self._make_request("GET", "/charges/brokerage", params=params)

    # Margin Methods

    def get_margins(self, instruments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get margin details for instruments.

        This API provides the functionality to retrieve the margin for instruments.
        It accepts input parameters like the instrument, quantity, transaction_type and product.

        Args:
            instruments: List of instrument objects, each containing:
                        - instrument_key: Key of the instrument
                        - quantity: Quantity with which the order is to be placed
                        - product: Product with which the order is to be placed (I, D, CO, MTF)
                        - transaction_type: Indicates whether it's a BUY or SELL order
                        - price: Optional price with which the order is to be placed

        Returns:
            Dictionary containing margin details for all instruments

        Example:
            ```python
            instruments = [
                {
                    "instrument_key": "NSE_EQ|INE669E01016",
                    "quantity": 1,
                    "transaction_type": "BUY",
                    "product": "D",
                    "price": 16.8
                }
            ]
            margins = upstox.get_margins(instruments)
            ```

        Response Format:
            Returns data containing:
            - margins: List of margin details for each instrument
            - required_margin: Total margin required to execute the orders
            - final_margin: Total margin after margin benefit

        Each margin object contains:
            - equity_margin: Margin applicable for equity trades
            - total_margin: Total margin required for the basket
            - exposure_margin: Exposure margin for FNO trades
            - tender_margin: Tender margin for futures contracts
            - span_margin: Span margin for derivatives trade
            - net_buy_premium: Option premium required
            - additional_margin: Additional margin for MCX FNO trade

        Note:
            - A maximum of 20 instruments is allowed per request
            - Margin fields that are not applicable will be set to zero for a given instrument
        """
        if len(instruments) > 20:
            raise InputException("Maximum 20 instruments allowed per request")

        data = {"instruments": instruments}
        return self._make_request("POST", "/charges/margins", json=data)

    # Order Methods

    def place_order_v3(
        self,
        quantity: int,
        product: str,
        validity: str,
        price: float,
        instrument_token: str,
        order_type: str,
        transaction_type: str,
        disclosed_quantity: int = 0,
        trigger_price: float = 0,
        is_amo: bool = False,
        slice: bool = False,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Place an order using V3 HFT API.

        This API places an order to the exchange with enhanced features including auto-slicing
        capability and latency information in the response metadata. Uses the HFT base URL
        for high-frequency trading operations.

        Args:
            quantity: Quantity with which the order is to be placed
            product: Product type (I, D, MTF)
            validity: Order validity (DAY, IOC)
            price: Price at which the order will be placed
            instrument_token: Key of the instrument
            order_type: Type of order (MARKET, LIMIT, SL, SL-M)
            transaction_type: BUY or SELL order
            disclosed_quantity: Quantity to be disclosed in market depth (default: 0)
            trigger_price: Trigger price for stop loss orders (default: 0)
            is_amo: Whether it's an After Market Order (default: False)
            slice: Enable auto-slicing for large orders (default: False)
            tag: Optional tag for order identification (default: None)

        Returns:
            Dictionary containing order IDs and metadata

        Example:
            ```python
            response = upstox.place_order_v3(
                quantity=1,
                product="D",
                validity="DAY",
                price=0,
                instrument_token="NSE_EQ|INE848E01016",
                order_type="MARKET",
                transaction_type="BUY",
                slice=True
            )
            ```

        Response Format:
            Returns data containing:
            - order_ids: List of reference order IDs
            - metadata: Order metadata including latency information

        Note:
            - The API is accessible from 5:30 AM to 12:00 AM IST daily
            - When slicing is enabled, maximum 25 orders can be placed in a single request
            - Currently product type 'OCO' is not allowed
            - Margin Trading Facility (MTF) is available for trading-eligible securities
            - Uses HFT base URL (https://api-hft.upstox.com/v3) for optimized performance
        """
        data = {
            "quantity": quantity,
            "product": product,
            "validity": validity,
            "price": price,
            "instrument_token": instrument_token,
            "order_type": order_type,
            "transaction_type": transaction_type,
            "disclosed_quantity": disclosed_quantity,
            "trigger_price": trigger_price,
            "is_amo": is_amo,
            "slice": slice,
        }

        if tag:
            if len(tag) > 40:
                raise InputException("Tag length exceeds limit of 40 characters")
            data["tag"] = tag

        return self._make_request_hft("POST", "/order/place", json=data)

    def place_multi_order(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Place multiple orders simultaneously.

        This API extends the functionality of Place Order API, allowing multiple orders
        to be placed simultaneously on the exchange.

        Args:
            orders: List of order objects, each containing:
                   - correlation_id: Unique identifier for tracking (required)
                   - quantity: Order quantity
                   - product: Product type (I, D, MTF)
                   - validity: Order validity (DAY, IOC)
                   - price: Order price
                   - instrument_token: Instrument key
                   - order_type: Order type (MARKET, LIMIT, SL, SL-M)
                   - transaction_type: BUY or SELL
                   - disclosed_quantity: Disclosed quantity (default: 0)
                   - trigger_price: Trigger price (default: 0)
                   - is_amo: After Market Order flag (default: False)
                   - slice: Auto-slicing flag (default: False)
                   - tag: Optional tag

        Returns:
            Dictionary containing order details for all placed orders

        Example:
            ```python
            orders = [
                {
                    "correlation_id": "order1",
                    "quantity": 1,
                    "product": "D",
                    "validity": "DAY",
                    "price": 0,
                    "instrument_token": "NSE_EQ|INE848E01016",
                    "order_type": "MARKET",
                    "transaction_type": "BUY"
                }
            ]
            response = upstox.place_multi_order(orders)
            ```

        Note:
            - Maximum 25 orders can be placed in a single request
            - Each order must have a unique correlation_id
            - Subject to different rate limits compared to standard limits
            - API is accessible from 5:30 AM to 12:00 AM IST daily
            - Uses HFT base URL (https://api-hft.upstox.com/v3) for optimized performance
        """
        if len(orders) > 25:
            raise InputException("Maximum 25 orders allowed per request")

        # Validate correlation_ids are unique
        correlation_ids = [order.get("correlation_id") for order in orders]
        if len(correlation_ids) != len(set(correlation_ids)):
            raise InputException("Each order must have a unique correlation_id")

        return self._make_request("POST", "/order/multi/place", json={"orders": orders})

    def modify_order_v3(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        trigger_price: Optional[float] = None,
        validity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Modify an existing order using V3 HFT API.

        Args:
            order_id: Order ID to modify
            quantity: New quantity (optional)
            price: New price (optional)
            order_type: New order type (optional)
            trigger_price: New trigger price (optional)
            validity: New validity (optional)

        Returns:
            Modification response with updated order details

        Example:
            ```python
            response = upstox.modify_order_v3(
                order_id="12345",
                quantity=200,
                price=150.50
            )
            ```
        """
        data = {}
        data["order_id"] = order_id
        if quantity is not None:
            data["quantity"] = quantity
        if price is not None:
            data["price"] = price
        if order_type is not None:
            data["order_type"] = order_type
        if trigger_price is not None:
            data["trigger_price"] = trigger_price
        if validity is not None:
            data["validity"] = validity

        return self._make_request_hft("PUT", f"/order/modify", json=data)

    def cancel_order_v3(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order using V3 HFT API.

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancellation response

        Example:
            ```python
            response = upstox.cancel_order_v3("12345")
            ```
        """
        data = {"order_id": order_id}
        return self._make_request_hft("DELETE", f"/order/cancel", json=data)

    def cancel_multi_order(self, order_ids: List[str]) -> Dict[str, Any]:
        """
        Cancel multiple orders simultaneously.

        Args:
            order_ids: List of order IDs to cancel

        Returns:
            Cancellation response for all orders

        Example:
            ```python
            response = upstox.cancel_multi_order(["12345", "12346", "12347"])
            ```
        """
        data = {"order_ids": order_ids}
        return self._make_request("DELETE", "/order/multi/cancel", json=data)

    def exit_all_positions(
        self, segment: Optional[str] = None, tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exit all open positions.

        This API allows you to exit all open positions in a single request. You can filter by
        segment or tag to exit specific positions, or exit all open positions with a single request.

        Args:
            segment: Optional segment filter (e.g., 'NSE_EQ', 'BSE_EQ', 'NSE_FO', 'BSE_FO', 'MCX_FO', 'NCD_FO', 'BCD_FO', 'NSE_COM')
            tag: Optional tag filter for exiting positions associated with specific order tags

        Returns:
            Response containing details of exited positions with order IDs and summary

        Example:
            ```python
            # Exit all positions
            response = upstox.exit_all_positions()

            # Exit positions for specific segment
            response = upstox.exit_all_positions(segment='NSE_EQ')

            # Exit positions with specific tag
            response = upstox.exit_all_positions(tag='Strategy_A')

            # Exit positions for specific segment and tag
            response = upstox.exit_all_positions(segment='NSE_EQ', tag='Strategy_A')
            ```

        Response Format:
            Returns data containing:
            - order_ids: List of reference order IDs for successful exits
            - errors: Array of errors for failed exits (if any)
            - summary: Summary with total, success, and error counts

        Note:
            - Maximum 50 positions can be exited in a single request
            - Order tags are only valid for intraday positions
            - Auto slicing is enabled by default
            - API is accessible during market hours only
            - BUY positions are executed first, followed by SELL orders
        """
        params = {}
        if segment:
            params["segment"] = segment
        if tag:
            params["tag"] = tag

        return self._make_request("POST", "/order/positions/exit", params=params)

    def get_order_details(
        self, order_id: Optional[str] = None, tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get order details for a specific order.

        This API retrieves the latest status of a specific order. Orders placed by the user
        remain available for one trading day and are automatically removed at the end of the trading session.

        Args:
            order_id: The order reference ID for which the order status is required
            tag: The tag to uniquely identify an order (alternative to order_id)

        Returns:
            Dictionary containing detailed order information

        Raises:
            InputException: If neither order_id nor tag is provided
            DataException: If order is not found

        Example:
            ```python
            # Get order details by order ID
            order_details = upstox.get_order_details(order_id="231019025562880")

            # Get order details by tag
            order_details = upstox.get_order_details(tag="Strategy_A")
            ```

        Response Format:
            Returns order details including:
            - exchange: Exchange (NSE, BSE, etc.)
            - product: Product type (I, D, CO, MTF)
            - price: Order price
            - quantity: Order quantity
            - status: Current order status
            - tag: Order tag
            - instrument_token: Instrument key
            - trading_symbol: Trading symbol
            - order_type: Order type (MARKET, LIMIT, SL, SL-M)
            - validity: Order validity (DAY, IOC)
            - transaction_type: BUY or SELL
            - average_price: Average execution price
            - filled_quantity: Quantity filled
            - pending_quantity: Quantity pending
            - order_id: Internal order ID
            - exchange_order_id: Exchange order ID
            - order_timestamp: Order placement timestamp
            - exchange_timestamp: Exchange timestamp

        Note:
            - At least one of 'order_id' or 'tag' is required
            - Orders are available for one trading day only
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
        """
        if not order_id and not tag:
            raise InputException(
                "At least one of 'order_id' or 'tag' is required to fetch order details"
            )

        params = {}
        if order_id:
            params["order_id"] = order_id
        if tag:
            params["tag"] = tag

        return self._make_request("GET", "/order/details", params=params)

    def get_order_history(
        self, order_id: Optional[str] = None, tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get order history for a specific order.

        This API retrieves the details of a specific order and provides information regarding
        the progression of an order through its various execution stages. Orders placed by the
        user remain available for one trading day and are automatically removed at the end of
        the trading session.

        Args:
            order_id: The order reference ID for which the order history is required
            tag: The unique tag of the order for which the order history is being requested

        Returns:
            List of dictionaries containing order history with progression through various stages

        Raises:
            InputException: If neither order_id nor tag is provided
            DataException: If order is not found

        Example:
            ```python
            # Get order history by order ID
            order_history = upstox.get_order_history(order_id="231019025564798")

            # Get order history by tag
            order_history = upstox.get_order_history(tag="Strategy_A")

            # Get order history by both order ID and tag (exact match)
            order_history = upstox.get_order_history(
                order_id="231019025564798",
                tag="Strategy_A"
            )
            ```

        Response Format:
            Returns a list of order history entries, each containing:
            - exchange: Exchange (NSE, BSE, etc.)
            - price: Order price
            - product: Product type (I, D, CO, MTF)
            - quantity: Order quantity
            - status: Order status at this stage
            - tag: Order tag
            - validity: Order validity (DAY, IOC)
            - average_price: Average execution price
            - disclosed_quantity: Disclosed quantity
            - exchange_order_id: Exchange order ID
            - exchange_timestamp: Exchange timestamp
            - instrument_token: Instrument key
            - is_amo: After Market Order flag
            - status_message: Status message
            - order_id: Internal order ID
            - order_request_id: Order request ID
            - order_type: Order type (MARKET, LIMIT, SL, SL-M)
            - parent_order_id: Parent order ID for CO orders
            - trading_symbol: Trading symbol
            - order_timestamp: Order placement timestamp
            - filled_quantity: Quantity filled
            - transaction_type: BUY or SELL
            - trigger_price: Trigger price for stop orders
            - placed_by: User identifier
            - variety: Order complexity

        Note:
            - At least one of 'order_id' or 'tag' is required
            - When both order_id and tag are provided, returns history of order matching both
            - When only tag is provided, returns history of all orders matching the tag
            - Orders are available for one trading day only
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Provides progression through various execution stages (put order req received,
              validation pending, open pending, open, complete, etc.)
        """
        if not order_id and not tag:
            raise InputException(
                "At least one of 'order_id' or 'tag' is required to fetch order history"
            )

        params = {}
        if order_id:
            params["order_id"] = order_id
        if tag:
            params["tag"] = tag

        return self._make_request("GET", "/order/history", params=params)

    def get_order_book(self) -> List[Dict[str, Any]]:
        """
        Get order book for the current day.

        This API retrieves the list of all orders placed for the current day. Orders initiated
        by the user remain active for a single day and are automatically cleared at the conclusion
        of the trading session. The response indicates the most current status of each order.

        Returns:
            List of dictionaries containing all orders for the current day

        Example:
            ```python
            # Get all orders for the current day
            order_book = upstox.get_order_book()

            # Process orders by status
            for order in order_book:
                print(f"Order {order['order_id']}: {order['status']} - {order['trading_symbol']}")
            ```

        Response Format:
            Returns a list of order objects, each containing:
            - exchange: Exchange (NSE, BSE, NFO, etc.)
            - product: Product type (I, D, CO, MTF)
            - price: Order price
            - quantity: Order quantity
            - status: Current order status
            - tag: Order tag
            - instrument_token: Instrument key
            - placed_by: User identifier
            - trading_symbol: Trading symbol
            - order_type: Order type (MARKET, LIMIT, SL, SL-M)
            - validity: Order validity (DAY, IOC)
            - trigger_price: Trigger price for stop orders
            - disclosed_quantity: Disclosed quantity
            - transaction_type: BUY or SELL
            - average_price: Average execution price
            - filled_quantity: Quantity filled
            - pending_quantity: Quantity pending
            - status_message: Status message
            - status_message_raw: Raw status message from RMS
            - exchange_order_id: Exchange order ID
            - parent_order_id: Parent order ID for CO orders
            - order_id: Internal order ID
            - variety: Order complexity
            - order_timestamp: Order placement timestamp
            - exchange_timestamp: Exchange timestamp
            - is_amo: After Market Order flag
            - order_request_id: Order request ID
            - order_ref_id: Order reference ID

        Note:
            - Orders are available for one trading day only
            - Orders are automatically cleared at the end of trading session
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Returns all orders regardless of status (complete, rejected, cancelled, open, etc.)
            - For comprehensive list of order statuses, refer to the Order Status Appendix
        """
        return self._make_request("GET", "/order/retrieve-all")

    def get_trades(self) -> List[Dict[str, Any]]:
        """
        Get all trades executed for the current day.

        This API retrieves the list of all trades executed for the day. An order, initially
        submitted as one entity, can be executed in smaller segments based on market situation.
        Each of these partial executions constitutes a trade, and a single order may consist
        of several such trades.

        Returns:
            List of dictionaries containing all trades executed for the current day

        Example:
            ```python
            # Get all trades for the current day
            trades = upstox.get_trades()

            # Process trades by transaction type
            for trade in trades:
                print(f"Trade {trade['trade_id']}: {trade['transaction_type']} {trade['quantity']} {trade['trading_symbol']} @ {trade['average_price']}")
            ```

        Response Format:
            Returns a list of trade objects, each containing:
            - exchange: Exchange (NSE, BSE, etc.)
            - product: Product type (I, D, CO, MTF)
            - trading_symbol: Trading symbol
            - instrument_token: Instrument key
            - order_type: Order type (MARKET, LIMIT, SL, SL-M)
            - transaction_type: BUY or SELL
            - quantity: Quantity traded
            - exchange_order_id: Exchange order ID
            - order_id: Internal order ID
            - exchange_timestamp: Trade execution timestamp
            - average_price: Price at which quantity was traded
            - trade_id: Unique trade ID from exchange
            - order_ref_id: Order reference ID
            - order_timestamp: Order placement timestamp

        Note:
            - Returns all trades executed for the current day
            - A single order may result in multiple trades due to partial executions
            - Each trade represents a specific execution segment
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Trade execution can happen in smaller segments based on market conditions
        """
        return self._make_request("GET", "/order/trades/get-trades-for-day")

    def get_order_trades(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Get all trades executed for a specific order.

        This API retrieves the list of all trades executed for a specific order. To access
        the trade information, you need to pass the order_id. An order can be executed in
        smaller segments based on market situation, and each of these partial executions
        constitutes a trade.

        Args:
            order_id: The order ID for which to get order trades

        Returns:
            List of dictionaries containing all trades executed for the specific order

        Raises:
            InputException: If order_id is not provided or invalid

        Example:
            ```python
            # Get all trades for a specific order
            order_trades = upstox.get_order_trades(order_id="221013001021539")

            # Process trades for the order
            for trade in order_trades:
                print(f"Trade {trade['trade_id']}: {trade['quantity']} @ {trade['average_price']}")
            ```

        Response Format:
            Returns a list of trade objects, each containing:
            - exchange: Exchange (NSE, BSE, etc.)
            - product: Product type (I, D, CO, MTF)
            - trading_symbol: Trading symbol
            - instrument_token: Instrument key
            - order_type: Order type (MARKET, LIMIT, SL, SL-M)
            - transaction_type: BUY or SELL
            - quantity: Quantity traded in this trade
            - exchange_order_id: Exchange order ID
            - order_id: Internal order ID
            - exchange_timestamp: Trade execution timestamp
            - average_price: Price at which quantity was traded
            - trade_id: Unique trade ID from exchange
            - order_ref_id: Order reference ID
            - order_timestamp: Order placement timestamp

        Note:
            - Returns all trades executed for the specific order
            - A single order may result in multiple trades due to partial executions
            - Each trade represents a specific execution segment of the order
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Trade execution can happen in smaller segments based on market conditions
        """
        if not order_id:
            raise InputException("Order id is required")

        params = {"order_id": order_id}
        return self._make_request("GET", "/order/trades", params=params)

    def get_trade_history(
        self,
        start_date: str,
        end_date: str,
        page_number: int,
        page_size: int,
        segment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get historical trade data.

        This API provides users with access to their historical trade and transaction data,
        allowing them to retrieve details of orders executed through Upstox platform. This
        enables various use cases including reviewing past month's trade activity, maintaining
        records for compliance or analysis.

        Args:
            start_date: Date from which data needs to be fetched (YYYY-MM-DD format)
            end_date: Date till data needs to be fetched (YYYY-MM-DD format)
            page_number: Page number for pagination (starting from 1)
            page_size: Number of records per page (1-5000)
            segment: Optional segment filter (EQ, FO, COM, CD, MF)
                     - EQ: Equity
                     - FO: Futures and Options
                     - COM: Commodity
                     - CD: Currency Derivatives
                     - MF: Mutual funds
                     - If not provided, considers all segments

        Returns:
            Dictionary containing historical trade data with pagination metadata

        Raises:
            InputException: If parameters are invalid or out of range
            DataException: If data retrieval fails

        Example:
            ```python
            # Get historical trades for equity segment
            trades = upstox.get_trade_history(
                start_date="2023-01-01",
                end_date="2023-01-31",
                page_number=1,
                page_size=100,
                segment="EQ"
            )

            # Get all historical trades
            trades = upstox.get_trade_history(
                start_date="2023-01-01",
                end_date="2023-01-31",
                page_number=1,
                page_size=50
            )
            ```

        Response Format:
            Returns data containing:
            - data: List of trade objects with detailed information
            - meta_data: Pagination metadata with page information

        Each trade object contains:
            - exchange: Exchange (NSE, BSE, NFO, MCX, CDS, BMF)
            - segment: Segment (EQ, FO, COM, CD, MF)
            - option_type: Option type (CE, PE) - only for FO and CD segments
            - quantity: Quantity traded
            - amount: Total amount of the trade
            - trade_id: Unique trade ID from exchange
            - trade_date: Date of the trade (YYYY-MM-DD)
            - transaction_type: BUY or SELL
            - scrip_name: Name of the scrip traded
            - strike_price: Strike price for options
            - expiry: Expiry date for derivatives (YYYY-MM-DD)
            - price: Price per unit
            - isin: ISIN code (available for EQ and MF segments)
            - symbol: Trading symbol (available for EQ and FO segments)
            - instrument_token: Instrument key (available for EQ and MF segments)

        Note:
            - Currently provides data only for last 3 financial years
            - Date range must be within the last 3 financial years
            - Page size must be between 1 and 5000
            - Page number must be at least 1
            - End date must be greater than or equal to start date
        """
        # Validate required parameters
        if not start_date or not end_date:
            raise InputException("start_date and end_date are required")

        if not page_number or page_number < 1:
            raise InputException("page_number must be at least 1")

        if not page_size or page_size < 1 or page_size > 5000:
            raise InputException("page_size must be between 1 and 5000")

        # Validate date format and range
        try:
            from datetime import datetime

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if end_dt < start_dt:
                raise InputException(
                    "end_date must be greater than or equal to start_date"
                )
        except ValueError:
            raise InputException("Date format should be YYYY-MM-DD")

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "page_number": page_number,
            "page_size": page_size,
        }

        if segment:
            valid_segments = ["EQ", "FO", "COM", "CD", "MF"]
            if segment not in valid_segments:
                raise InputException(
                    f"Invalid segment: {segment}. Valid segments are: {', '.join(valid_segments)}"
                )
            params["segment"] = segment

        return self._make_request("GET", "/charges/historical-trades", params=params)

    # Portfolio Methods

    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions for the user.

        This API retrieves the current positions for the user. These assets remain within
        the positions portfolio until they are either sold or reach their standard three-month
        expiration date in the case of derivatives. If any equity positions are carried overnight,
        they are automatically shifted to the holdings portfolio on the following trading day.

        Returns:
            List of dictionaries containing current position details

        Example:
            ```python
            # Get current positions
            positions = upstox.get_positions()

            # Process positions by exchange
            for position in positions:
                print(f"{position['trading_symbol']}: {position['quantity']} @ {position['last_price']} (P&L: {position['pnl']})")
            ```

        Response Format:
            Returns a list of position objects, each containing:
            - exchange: Exchange (NSE, BSE, NFO, MCX, CDS)
            - multiplier: Quantity/lot size multiplier for P&L calculations
            - value: Net value of the position
            - pnl: Profit and loss - net returns on the position
            - product: Product type (I, D, CO)
            - instrument_token: Instrument key
            - average_price: Average price at which net position quantity was acquired
            - buy_value: Net value of the bought quantities
            - overnight_quantity: Quantity held previously and carried forward overnight
            - day_buy_value: Amount at which quantity is bought during the day
            - day_buy_price: Average price at which day quantity was bought
            - overnight_buy_amount: Amount at which quantity was bought in previous session
            - overnight_buy_quantity: Quantity bought in previous session
            - day_buy_quantity: Quantity bought during the day
            - day_sell_value: Amount at which quantity is sold during the day
            - day_sell_price: Average price at which day quantity was sold
            - overnight_sell_amount: Amount at which quantity was sold in previous session
            - overnight_sell_quantity: Quantity sold short in previous session
            - day_sell_quantity: Quantity sold during the day
            - quantity: Net quantity left after nullifying buy/sell quantities
            - last_price: Last traded market price of the instrument
            - unrealised: Day P&L generated against open positions
            - realised: Day P&L generated against closed positions
            - sell_value: Net value of the sold quantities
            - trading_symbol: Trading symbol of the instrument
            - close_price: Closing price from last trading day
            - buy_price: Average price at which quantities were bought
            - sell_price: Average price at which quantities were sold

        Note:
            - Positions remain until sold or derivatives expire (3-month standard)
            - Equity positions carried overnight are moved to holdings portfolio
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Supports all exchanges: NSE, BSE, NFO, MCX, CDS
            - Provides comprehensive P&L tracking (realised and unrealised)
        """
        return self._make_request("GET", "/portfolio/short-term-positions")

    def get_mtf_positions(self) -> List[Dict[str, Any]]:
        """
        Get current Margin Trade Funding (MTF) positions for the user.

        This API retrieves the current MTF positions for the user. MTF is a facility that
        allows investors to buy securities by paying a fraction of the transaction value,
        with the remaining amount funded by Upstox. These positions remain in the MTF
        portfolio until they are either sold or the loan is repaid.

        Returns:
            List of dictionaries containing current MTF position details

        Example:
            ```python
            # Get current MTF positions
            mtf_positions = upstox.get_mtf_positions()

            # Process MTF positions
            for position in mtf_positions:
                print(f"{position['trading_symbol']}: {position['quantity']} @ {position['last_price']} (P&L: {position['pnl']})")
            ```

        Response Format:
            Returns a list of MTF position objects, each containing:
            - exchange: Exchange (NSE only for MTF positions)
            - multiplier: Quantity/lot size multiplier for P&L calculations
            - value: Net value of the position
            - pnl: Profit and loss - net returns on the position
            - product: Product type (always 'MTF')
            - instrument_token: Instrument key
            - average_price: Average price at which net position quantity was acquired
            - buy_value: Net value of the bought quantities
            - overnight_quantity: Quantity held previously and carried forward overnight
            - day_buy_value: Amount at which quantity is bought during the day
            - day_buy_price: Average price at which day quantity was bought
            - overnight_buy_amount: Amount at which quantity was bought in previous session
            - overnight_buy_quantity: Quantity bought in previous session
            - day_buy_quantity: Quantity bought during the day
            - day_sell_value: Amount at which quantity is sold during the day
            - day_sell_price: Average price at which day quantity was sold
            - overnight_sell_amount: Amount at which quantity was sold in previous session
            - overnight_sell_quantity: Quantity sold short in previous session
            - day_sell_quantity: Quantity sold during the day
            - quantity: Net quantity left after nullifying buy/sell quantities
            - last_price: Last traded market price of the instrument
            - unrealised: Day P&L generated against open positions
            - realised: Day P&L generated against closed positions
            - sell_value: Net value of the sold quantities
            - trading_symbol: Trading symbol of the instrument
            - close_price: Closing price from last trading day
            - buy_price: Average price at which quantities were bought
            - sell_price: Average price at which quantities were sold

        Note:
            - MTF positions remain until sold or loan is repaid
            - Only available for NSE exchange
            - Product type is always 'MTF'
            - Provides leverage facility for buying securities
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Supports comprehensive P&L tracking (realised and unrealised)
        """
        return self._make_request_v3("GET", "/portfolio/mtf-positions")

    def convert_positions(
        self,
        instrument_token: str,
        new_product: str,
        old_product: str,
        transaction_type: str,
        quantity: int,
    ) -> Dict[str, Any]:
        """
        Convert positions between different product types.

        This API allows you to convert your intraday positions into delivery trades or
        your margin trades into cash and carry, and vice versa. Position would be converted
        only if the required margin is available. Delivery holdings can be converted to
        Intraday positions only if it is purchased on the same day before the auto square
        off timing. Only simple orders can be converted from Intraday to delivery,
        Special orders like CO cannot be converted from intraday to delivery.

        Args:
            instrument_token (str): Key of the instrument
            new_product (str): New product type. Possible values: 'I' (Intraday), 'D' (Delivery)
            old_product (str): Old product type. Possible values: 'I' (Intraday), 'D' (Delivery)
            transaction_type (str): Transaction type. Possible values: 'BUY', 'SELL'
            quantity (int): Quantity with which the position to convert

        Returns:
            Dictionary containing the conversion status

        Raises:
            InputException: If any of the parameters are invalid
            OrderException: If conversion fails due to insufficient margin or other order-related issues
            PermissionException: If user doesn't have permission to convert positions

        Example:
            ```python
            # Convert intraday position to delivery
            result = upstox.convert_positions(
                instrument_token="151064324",
                new_product="D",  # Delivery
                old_product="I",  # Intraday
                transaction_type="BUY",
                quantity=1
            )

            # Convert delivery position to intraday
            result = upstox.convert_positions(
                instrument_token="151064324",
                new_product="I",  # Intraday
                old_product="D",  # Delivery
                transaction_type="SELL",
                quantity=1
            )
            ```

        Response Format:
            Returns a dictionary with:
            - status: Overall request status ('success')
            - data: Response data containing:
              - status: Status message for convert position request ('complete')

        Note:
            - Position conversion requires sufficient margin availability
            - Delivery to Intraday conversion only works for same-day purchases before auto square-off
            - Only simple orders can be converted from Intraday to Delivery
            - Special orders like CO (Cover Order) cannot be converted
            - Product types: 'I' = Intraday, 'D' = Delivery
            - Transaction types: 'BUY' = Buy transaction, 'SELL' = Sell transaction
            - Quantity must be positive and within available position limits
        """
        # Input validation
        if not instrument_token:
            raise InputException("instrument_token is required")

        if new_product not in ["I", "D"]:
            raise InputException("new_product must be 'I' (Intraday) or 'D' (Delivery)")

        if old_product not in ["I", "D"]:
            raise InputException("old_product must be 'I' (Intraday) or 'D' (Delivery)")

        if transaction_type not in ["BUY", "SELL"]:
            raise InputException("transaction_type must be 'BUY' or 'SELL'")

        if quantity <= 0:
            raise InputException("quantity must be positive")

        data = {
            "instrument_token": instrument_token,
            "new_product": new_product,
            "old_product": old_product,
            "transaction_type": transaction_type,
            "quantity": quantity,
        }

        return self._make_request("POST", "/portfolio/convert-position", json=data)

    def get_holdings(self) -> List[Dict[str, Any]]:
        """
        Get long-term holdings of the user.

        This API retrieves the long-term holdings of the user. A Holding within a holdings
        portfolio remains in place without a predetermined time limit. It can only be
        withdrawn when it is divested, delisted, or subject to modifications dictated by
        the stock exchanges. In essence, the instruments housed in the portfolio are
        securely located within the user's DEMAT account, in strict compliance with the
        regulations.

        Returns:
            List of dictionaries containing long-term holding details

        Example:
            ```python
            # Get long-term holdings
            holdings = upstox.get_holdings()

            # Process holdings
            for holding in holdings:
                print(f"{holding['trading_symbol']}: {holding['quantity']} @ {holding['average_price']} (P&L: {holding['pnl']})")
            ```

        Response Format:
            Returns a list of holding objects, each containing:
            - isin: The standard ISIN representing stocks listed on multiple exchanges
            - cnc_used_quantity: Quantity either blocked towards open or completed order
            - collateral_type: Category of collateral assigned by RMS
            - company_name: Name of the company
            - haircut: Haircut percentage applied from RMS (applicable in case of collateral)
            - product: Product type (I=Intraday, D=Delivery, CO=Cover Order, MTF=Margin Trade Funding)
            - quantity: The total holding quantity
            - trading_symbol: Trading symbol of the instrument (use this instead of deprecated 'tradingsymbol')
            - last_price: Last traded price of the instrument
            - close_price: Closing price from the last trading day
            - pnl: Profit and Loss
            - day_change: Day's change in absolute value for the stock
            - day_change_percentage: Day's change in percentage for the stock
            - instrument_token: Key of the instrument
            - average_price: Average price at which the net holding quantity was acquired
            - collateral_quantity: Quantity marked as collateral by RMS on user's request
            - collateral_update_quantity: Updated collateral quantity
            - t1_quantity: Quantity on T+1 day after order execution
            - exchange: Exchange to which the order is associated

        Note:
            - Holdings are long-term investments in DEMAT account
            - No predetermined time limit for holdings
            - Can only be withdrawn when divested, delisted, or modified by exchanges
            - Securely located within user's DEMAT account
            - The lowercase field 'tradingsymbol' is deprecated, use 'trading_symbol'
            - Holdings represent actual ownership of securities
            - Different from intraday positions which have time limits
            - Supports collateral marking for margin requirements
            - T+1 quantity indicates settlement status
        """
        return self._make_request("GET", "/portfolio/long-term-holdings")

    # Market Information Methods

    def get_market_holidays(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get market holidays for the current year.

        This API retrieves holidays for the current year and supports an optional
        parameter to fetch holiday details for a specific date.

        Args:
            date: Optional date for retrieving holiday information (YYYY-MM-DD format)

        Returns:
            List of holiday information including date, description, holiday type,
            and exchange details

        Example:
            ```python
            # Get all holidays for current year
            holidays = upstox.get_market_holidays()

            # Get holiday for specific date
            holiday = upstox.get_market_holidays(date="2024-01-26")
            ```

        Response Format:
            Each holiday object contains:
            - date: Date in YYYY-MM-DD format
            - description: Description about the holiday
            - holiday_type: Type of holiday (TRADING_HOLIDAY, SETTLEMENT_HOLIDAY, SPECIAL_TIMING)
            - closed_exchanges: List of exchanges that are closed
            - open_exchanges: List of exchanges that are open with timing details
        """
        if date:
            return self._make_request("GET", f"/market-info/holidays/{date}")
        else:
            return self._make_request("GET", "/market-info/holidays")

    # Option Chain Methods

    def get_option_contracts(
        self, instrument_key: str, expiry_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get option contracts for an underlying symbol.

        This API retrieves option contracts for an underlying symbol and supports an
        optional parameter to fetch option contracts for a specific expiry date.

        Args:
            instrument_key: Key of an underlying symbol (e.g., "NSE_INDEX|Nifty 50")
            expiry_date: Optional expiry date in YYYY-MM-DD format

        Returns:
            List of option contracts with detailed information

        Example:
            ```python
            # Get all option contracts for NIFTY
            contracts = upstox.get_option_contracts("NSE_INDEX|Nifty 50")

            # Get option contracts for specific expiry date
            contracts = upstox.get_option_contracts(
                instrument_key="NSE_INDEX|Nifty 50",
                expiry_date="2024-02-15"
            )
            ```

        Response Format:
            Each contract object contains:
            - name: The name of the option
            - segment: Market segment (NSE_FO, BSE_FO, etc.)
            - exchange: Exchange (NSE, BSE, MCX)
            - expiry: Expiry date in YYYY-MM-DD format
            - instrument_key: Unique identifier for the option
            - trading_symbol: Symbol used for trading
            - instrument_type: Type of option (CE, PE)
            - strike_price: Strike price for the option
            - lot_size: Size of one lot
            - tick_size: Minimum price movement
            - underlying_symbol: Symbol of underlying asset
            - weekly: Boolean indicating if it's a weekly option
        """
        params = {"instrument_key": instrument_key}
        if expiry_date:
            params["expiry_date"] = expiry_date

        return self._make_request("GET", "/option/contract", params=params)

    def get_pc_option_chain(
        self, instrument_key: str, expiry_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get put/call option chain for an underlying symbol for a specific expiry date.

        This API retrieves put/call option chain data including market data and option Greeks
        for both call and put options at each strike price.

        Args:
            instrument_key: Key of an underlying symbol (e.g., "NSE_INDEX|Nifty 50")
            expiry_date: Expiry date in YYYY-MM-DD format

        Returns:
            List of option chain data with strike prices, PCR, and call/put option details

        Example:
            ```python
            # Get put/call option chain for NIFTY for specific expiry
            option_chain = upstox.get_pc_option_chain(
                instrument_key="NSE_INDEX|Nifty 50",
                expiry_date="2025-02-13"
            )
            ```

        Response Format:
            Each option chain object contains:
            - expiry: Expiry date in YYYY-MM-DD format
            - pcr: Put Call Ratio
            - strike_price: Strike price for the option
            - underlying_key: Instrument key for underlying asset
            - underlying_spot_price: Spot price for underlying asset
            - call_options: Call option data with market data and Greeks
            - put_options: Put option data with market data and Greeks

        Note:
            The Put/Call Option chain is currently not available for the MCX Exchange.
        """
        params = {"instrument_key": instrument_key, "expiry_date": expiry_date}

        return self._make_request("GET", "/option/chain", params=params)

    # Market Quote Methods

    def get_full_market_quote(self, instrument_keys: List[str]) -> Dict[str, Any]:
        """
        Get full market quotes for multiple instruments.

        Provides the complete market data snapshot of up to 500 instruments in one go.
        These snapshots are obtained directly from the exchanges at the time of request.

        Args:
            instrument_keys: List of instrument keys (max 500)

        Returns:
            Dictionary containing full market quote data for all instruments

        Raises:
            InputException: If more than 500 instrument keys are provided
            DataException: If data retrieval fails

        Note:
            Maximum 500 instrument keys can be requested in a single API call.
        """
        if len(instrument_keys) > 500:
            raise InputException(
                "Maximum 500 instrument keys can be requested in a single API call"
            )

        # Join instrument keys with comma
        instrument_key_str = ",".join(instrument_keys)
        params = {"instrument_key": instrument_key_str}

        return self._make_request("GET", "/market-quote/quotes", params=params)

    def get_ohlc_quotes_v3(
        self, instrument_keys: List[str], interval: str
    ) -> Dict[str, Any]:
        """
        Get OHLC quotes V3 for multiple instruments.

        V3 introduces the following enhancements:
        - live_ohlc: Provides the current OHLC candle
        - prev_ohlc: Delivers the previous minute's OHLC candle
        - volume: Includes trading volume data
        - ts: Returns the OHLC candle's start time

        Args:
            instrument_keys: List of instrument keys (max 500)
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 1d)

        Returns:
            Dictionary containing OHLC quote data for all instruments

        Raises:
            InputException: If more than 500 instrument keys are provided or invalid interval
            DataException: If data retrieval fails

        Note:
            - Maximum 500 instrument keys can be requested in a single API call
            - For a time interval of '1d', the API returns only the 'live_ohlc'
            - Previous day OHLC data is available in Historical Candle Data
        """
        if len(instrument_keys) > 500:
            raise InputException(
                "Maximum 500 instrument keys can be requested in a single API call"
            )

        # Validate interval
        valid_intervals = ["1m", "5m", "15m", "30m", "1h", "1d"]
        if interval not in valid_intervals:
            raise InputException(
                f"Invalid interval: {interval}. Valid intervals are: {', '.join(valid_intervals)}"
            )

        # Join instrument keys with comma
        instrument_key_str = ",".join(instrument_keys)
        params = {"instrument_key": instrument_key_str, "interval": interval}

        return self._make_request_v3("GET", "/market-quote/ohlc", params=params)

    def get_ltp_quotes_v3(self, instrument_keys: List[str]) -> Dict[str, Any]:
        """
        Get LTP (Last Traded Price) quotes V3 for multiple instruments.

        Args:
            instrument_keys: List of instrument keys (max 500)

        Returns:
            Dictionary containing LTP quote data for all instruments

        Raises:
            InputException: If more than 500 instrument keys are provided
            DataException: If data retrieval fails

        Note:
            Maximum 500 instrument keys can be requested in a single API call.
        """
        if len(instrument_keys) > 500:
            raise InputException(
                "Maximum 500 instrument keys can be requested in a single API call"
            )

        # Join instrument keys with comma
        instrument_key_str = ",".join(instrument_keys)
        params = {"instrument_key": instrument_key_str}

        return self._make_request_v3("GET", "/market-quote/ltp", params=params)

    def get_option_greeks(self, instrument_keys: List[str]) -> Dict[str, Any]:
        """
        Get option Greeks for multiple instruments.

        Args:
            instrument_keys: List of instrument keys (max 500)

        Returns:
            Dictionary containing option Greeks data for all instruments

        Raises:
            InputException: If more than 500 instrument keys are provided
            DataException: If data retrieval fails

        Note:
            Maximum 500 instrument keys can be requested in a single API call.
            This API is specifically for options and futures instruments.
        """
        if len(instrument_keys) > 500:
            raise InputException(
                "Maximum 500 instrument keys can be requested in a single API call"
            )

        # Join instrument keys with comma
        instrument_key_str = ",".join(instrument_keys)
        params = {"instrument_key": instrument_key_str}

        return self._make_request_v3(
            "GET", "/market-quote/option-greeks", params=params
        )

    # Historical Data Methods

    def get_historical_candle_data_v3(
        self,
        instrument_key: str,
        unit: str,
        interval: str,
        to_date: str,
        from_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get historical candle data using V3 API with custom time intervals.

        This API allows users to retrieve data in custom time intervals for each unit
        (minutes, hours, days, weeks, and months), enabling more granular data control
        and improved flexibility for analysis.

        Args:
            instrument_key: The unique identifier for the financial instrument
            unit: Specifies the unit for the candles (minutes, hours, days, weeks, months)
            interval: Specifies the interval for the candles
                     - minutes: 1, 2, 3, ..., 300
                     - hours: 1, 2, 3, 4, 5
                     - days, weeks, months: 1
            to_date: The ending date (inclusive) for the historical data range (YYYY-MM-DD)
            from_date: The starting date for the historical data range (YYYY-MM-DD) - optional

        Returns:
            Dictionary containing historical candle data with OHLC values

        Raises:
            InputException: If parameters are invalid
            DataException: If data retrieval fails

        Note:
            Historical availability and retrieval limits:
            - minutes: Available from January 2022, 1 month for 1-15 min, 1 quarter for >15 min
            - hours: Available from January 2022, 1 quarter leading up to to_date
            - days: Available from January 2000, 1 decade leading up to to_date
            - weeks: Available from January 2000, no limit
            - months: Available from January 2000, no limit
        """
        # Validate unit
        valid_units = ["minutes", "hours", "days", "weeks", "months"]
        if unit not in valid_units:
            raise InputException(
                f"Invalid unit: {unit}. Valid units are: {', '.join(valid_units)}"
            )

        # Validate interval based on unit
        if unit == "minutes":
            if not (1 <= int(interval) <= 300):
                raise InputException(
                    f"Invalid interval for minutes: {interval}. Must be between 1 and 300"
                )
        elif unit == "hours":
            if not (1 <= int(interval) <= 5):
                raise InputException(
                    f"Invalid interval for hours: {interval}. Must be between 1 and 5"
                )
        elif unit in ["days", "weeks", "months"]:
            if interval != "1":
                raise InputException(
                    f"Invalid interval for {unit}: {interval}. Must be 1"
                )

        # Build endpoint
        endpoint = f"/historical-candle/{instrument_key}/{unit}/{interval}/{to_date}"

        # Add from_date if provided
        if from_date:
            endpoint += f"/{from_date}"

        # Use V3 request method
        return self._make_request_v3("GET", endpoint)

    def get_intraday_candle_data_v3(
        self, instrument_key: str, unit: str, interval: str
    ) -> Dict[str, Any]:
        """
        Get intraday candle data using V3 API with custom time intervals.

        This API allows you to retrieve Open, High, Low, and Close (OHLC) values
        for the current trading day with customizable time intervals.

        Args:
            instrument_key: The unique identifier for the financial instrument
            unit: Specifies the unit for the candles (minutes, hours, days)
            interval: Specifies the interval for the candles
                     - minutes: 1, 2, 3, ..., 300
                     - hours: 1, 2, 3, 4, 5
                     - days: 1

        Returns:
            Dictionary containing intraday candle data with OHLC values

        Raises:
            InputException: If parameters are invalid
            DataException: If data retrieval fails

        Note:
            This API is particularly useful for traders and analysts who require
            detailed intraday data for technical analysis, backtesting, or
            algorithmic trading strategies.
        """
        # Validate unit
        valid_units = ["minutes", "hours", "days"]
        if unit not in valid_units:
            raise InputException(
                f"Invalid unit: {unit}. Valid units are: {', '.join(valid_units)}"
            )

        # Validate interval based on unit
        if unit == "minutes":
            if not (1 <= int(interval) <= 300):
                raise InputException(
                    f"Invalid interval for minutes: {interval}. Must be between 1 and 300"
                )
        elif unit == "hours":
            if not (1 <= int(interval) <= 5):
                raise InputException(
                    f"Invalid interval for hours: {interval}. Must be between 1 and 5"
                )
        elif unit == "days":
            if interval != "1":
                raise InputException(
                    f"Invalid interval for days: {interval}. Must be 1"
                )

        # Build endpoint and use V3 request method
        endpoint = f"/historical-candle/intraday/{instrument_key}/{unit}/{interval}"
        return self._make_request_v3("GET", endpoint)

    def __repr__(self):
        return f"Upstox(api_key='{self.api_key[:8]}...', access_token={'set' if self.access_token else 'not set'})"
