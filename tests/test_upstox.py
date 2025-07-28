#!/usr/bin/env python3
"""
Unit tests for Upstox Python client.

This module contains comprehensive tests for the Upstox client library.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from upstox import Upstox
from upstox.exceptions import (
    UpstoxException,
    TokenException,
    OrderException,
    PermissionException,
    InputException,
    NetworkException,
)


class TestUpstoxClient(unittest.TestCase):
    """Test cases for Upstox client."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.access_token = "test_access_token"
        self.upstox = Upstox(api_key=self.api_key, access_token=self.access_token)

    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.upstox.api_key, self.api_key)
        self.assertEqual(self.upstox.access_token, self.access_token)
        self.assertIsNotNone(self.upstox.session)

    def test_set_access_token(self):
        """Test setting access token."""
        new_token = "new_access_token"
        self.upstox.set_access_token(new_token)
        self.assertEqual(self.upstox.access_token, new_token)
        self.assertIn("Authorization", self.upstox.session.headers)

    def test_get_login_url(self):
        """Test getting login URL."""
        redirect_uri = "https://example.com/callback"
        login_url = self.upstox.get_login_url(redirect_uri)

        self.assertIn(self.api_key, login_url)
        self.assertIn("response_type=code", login_url)
        # URL encoding changes the redirect_uri, so check for encoded version
        self.assertIn("redirect_uri=", login_url)

    def test_get_login_url_with_state(self):
        """Test getting login URL with state parameter."""
        redirect_uri = "https://example.com/callback"
        state = "test_state"
        login_url = self.upstox.get_login_url(redirect_uri, state)

        self.assertIn(f"state={state}", login_url)

    @patch("requests.Session.post")
    def test_generate_session_success(self, mock_post):
        """Test successful session generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "refresh_token",
            "token_type": "Bearer",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        session_data = self.upstox.generate_session(
            "auth_code", "api_secret", "https://example.com/callback"
        )

        self.assertEqual(session_data["access_token"], "new_access_token")
        self.assertEqual(self.upstox.access_token, "new_access_token")

    @patch("requests.Session.post")
    def test_generate_session_failure(self, mock_post):
        """Test failed session generation."""
        import requests

        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        with self.assertRaises(TokenException):
            self.upstox.generate_session(
                "auth_code", "api_secret", "https://example.com/callback"
            )

    @patch("requests.Session.request")
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {"key": "value"},
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.upstox._make_request("GET", "/test")

        self.assertEqual(result, {"key": "value"})

    @patch("requests.Session.request")
    def test_make_request_401_error(self, mock_request):
        """Test 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        with self.assertRaises(TokenException):
            self.upstox._make_request("GET", "/test")

    @patch("requests.Session.request")
    def test_make_request_403_error(self, mock_request):
        """Test 403 permission error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_request.return_value = mock_response

        with self.assertRaises(PermissionException):
            self.upstox._make_request("GET", "/test")

    @patch("requests.Session.request")
    def test_make_request_400_error(self, mock_request):
        """Test 400 input error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_request.return_value = mock_response

        with self.assertRaises(InputException):
            self.upstox._make_request("GET", "/test")

    @patch("requests.Session.request")
    def test_make_request_429_error(self, mock_request):
        """Test 429 rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response

        with self.assertRaises(Exception):
            self.upstox._make_request("GET", "/test")

    @patch("requests.Session.request")
    def test_make_request_500_error(self, mock_request):
        """Test 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response

        with self.assertRaises(NetworkException):
            self.upstox._make_request("GET", "/test")

    @patch("requests.Session.request")
    def test_make_request_error_response(self, mock_request):
        """Test error response structure."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "error",
            "errors": [
                {
                    "error_code": "UDAPI1021",
                    "message": "Invalid instrument key format",
                    "property_path": None,
                    "invalid_value": None,
                }
            ],
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        with self.assertRaises(InputException) as context:
            self.upstox._make_request("GET", "/test")

        self.assertIn("Invalid instrument key format", str(context.exception))
        self.assertIn("UDAPI1021", str(context.exception))

    @patch("requests.Session.request")
    def test_make_request_backward_compatibility(self, mock_request):
        """Test backward compatibility with non-standard responses."""
        mock_response = Mock()
        mock_response.json.return_value = {"direct_data": "value"}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.upstox._make_request("GET", "/test")

        self.assertEqual(result, {"direct_data": "value"})

    @patch.object(Upstox, "_make_request")
    def test_get_profile(self, mock_make_request):
        """Test getting user profile."""
        mock_make_request.return_value = {
            "name": "Test User",
            "email": "test@example.com",
        }

        profile = self.upstox.get_profile()

        mock_make_request.assert_called_once_with("GET", "/user/profile")
        self.assertEqual(profile["name"], "Test User")

    @patch.object(Upstox, "_make_request")
    def test_get_holdings(self, mock_make_request):
        """Test getting holdings."""
        mock_make_request.return_value = [
            {"tradingsymbol": "RELIANCE-EQ", "quantity": 100},
            {"tradingsymbol": "TCS-EQ", "quantity": 50},
        ]

        holdings = self.upstox.get_holdings()

        mock_make_request.assert_called_once_with(
            "GET", "/portfolio/long-term-holdings"
        )
        self.assertEqual(len(holdings), 2)

    @patch.object(Upstox, "_make_request_hft")
    def test_place_order(self, mock_make_request):
        """Test placing an order."""
        mock_make_request.return_value = {"data": {"order_id": "12345"}}

        result = self.upstox.place_order_v3(
            quantity=10,
            product="cnc",
            validity="day",
            price=0,
            instrument_token="NSE_EQ|INE848E01016",
            order_type="market",
            transaction_type="buy",
        )

        self.assertEqual(result, {"data": {"order_id": "12345"}})

    @patch.object(Upstox, "_make_request_hft")
    def test_place_order_invalid_response(self, mock_make_request):
        """Test placing order with invalid response."""
        mock_make_request.return_value = {"data": {}}  # Missing order_id

        # The method should return the response as-is, not raise an exception
        result = self.upstox.place_order_v3(
            quantity=10,
            product="cnc",
            validity="day",
            price=0,
            instrument_token="NSE_EQ|INE848E01016",
            order_type="market",
            transaction_type="buy",
        )

        self.assertEqual(result, {"data": {}})

    @patch.object(Upstox, "_make_request_hft")
    def test_cancel_order(self, mock_make_request):
        """Test canceling an order."""
        mock_make_request.return_value = {"status": "cancelled"}

        result = self.upstox.cancel_order_v3("12345")

        mock_make_request.assert_called_once_with(
            "DELETE", "/order/cancel", json={"order_id": "12345"}
        )
        self.assertEqual(result["status"], "cancelled")

    @patch.object(Upstox, "_make_request_hft")
    def test_modify_order(self, mock_make_request):
        """Test modifying an order."""
        mock_make_request.return_value = {"status": "modified"}

        result = self.upstox.modify_order_v3(
            order_id="12345", quantity=20, price=2500.0
        )

        expected_data = {"order_id": "12345", "quantity": 20, "price": 2500.0}
        mock_make_request.assert_called_once_with(
            "PUT", "/order/modify", json=expected_data
        )
        self.assertEqual(result["status"], "modified")

    def test_constants(self):
        """Test class constants."""
        self.assertEqual(Upstox.ORDER_TYPE_MARKET, "market")
        self.assertEqual(Upstox.ORDER_TYPE_LIMIT, "limit")
        self.assertEqual(Upstox.TRANSACTION_TYPE_BUY, "buy")
        self.assertEqual(Upstox.TRANSACTION_TYPE_SELL, "sell")
        self.assertEqual(Upstox.PRODUCT_CNC, "cnc")
        self.assertEqual(Upstox.PRODUCT_MIS, "mis")
        self.assertEqual(Upstox.EXCHANGE_NSE, "NSE")
        self.assertEqual(Upstox.EXCHANGE_BSE, "BSE")

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.upstox)
        self.assertIn("Upstox", repr_str)
        self.assertIn("set", repr_str)  # access_token is set

    @patch("requests.Session.request")
    def test_get_historical_candle_data_v3_success(self, mock_request):
        """Test successful V3 historical candle data retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "candles": [
                    [
                        "2024-01-01T00:00:00+05:30",
                        100.0,
                        105.0,
                        98.0,
                        102.0,
                        1000000,
                        0,
                    ],
                    [
                        "2024-01-02T00:00:00+05:30",
                        102.0,
                        108.0,
                        101.0,
                        106.0,
                        1200000,
                        0,
                    ],
                ]
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        data = self.upstox.get_historical_candle_data_v3(
            instrument_key="NSE_EQ|INE848E01016",
            unit=self.upstox.UNIT_MINUTES,
            interval="5",
            to_date="2024-01-31",
        )

        # Check that the correct V3 URL was called
        expected_url = "https://api.upstox.com/v3/historical-candle/NSE_EQ|INE848E01016/minutes/5/2024-01-31"
        mock_request.assert_called_once_with("GET", expected_url, timeout=30)
        # The method should return the data portion of the response
        self.assertEqual(len(data["candles"]), 2)

    def test_get_historical_candle_data_v3_invalid_unit(self):
        """Test V3 historical data with invalid unit."""
        with self.assertRaises(InputException):
            self.upstox.get_historical_candle_data_v3(
                instrument_key="NSE_EQ|INE848E01016",
                unit="invalid_unit",
                interval="1",
                to_date="2024-01-31",
            )

    def test_get_historical_candle_data_v3_invalid_interval_minutes(self):
        """Test V3 historical data with invalid interval for minutes."""
        with self.assertRaises(InputException):
            self.upstox.get_historical_candle_data_v3(
                instrument_key="NSE_EQ|INE848E01016",
                unit=self.upstox.UNIT_MINUTES,
                interval="500",  # Invalid: should be 1-300
                to_date="2024-01-31",
            )

    def test_get_historical_candle_data_v3_invalid_interval_hours(self):
        """Test V3 historical data with invalid interval for hours."""
        with self.assertRaises(InputException):
            self.upstox.get_historical_candle_data_v3(
                instrument_key="NSE_EQ|INE848E01016",
                unit=self.upstox.UNIT_HOURS,
                interval="10",  # Invalid: should be 1-5
                to_date="2024-01-31",
            )

    def test_get_historical_candle_data_v3_invalid_interval_days(self):
        """Test V3 historical data with invalid interval for days."""
        with self.assertRaises(InputException):
            self.upstox.get_historical_candle_data_v3(
                instrument_key="NSE_EQ|INE848E01016",
                unit=self.upstox.UNIT_DAYS,
                interval="2",  # Invalid: should be 1
                to_date="2024-01-31",
            )

    @patch("requests.Session.request")
    def test_get_historical_candle_data_v3_with_from_date(self, mock_request):
        """Test V3 historical data with from_date parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "data": {"candles": []}}
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        self.upstox.get_historical_candle_data_v3(
            instrument_key="NSE_EQ|INE848E01016",
            unit=self.upstox.UNIT_MINUTES,
            interval="1",
            to_date="2024-01-31",
            from_date="2024-01-01",
        )

        # Check that the correct V3 URL was called with from_date
        expected_url = "https://api.upstox.com/v3/historical-candle/NSE_EQ|INE848E01016/minutes/1/2024-01-31/2024-01-01"
        mock_request.assert_called_once_with("GET", expected_url, timeout=30)

    def test_constants_v3(self):
        """Test V3 API constants."""
        self.assertEqual(Upstox.UNIT_MINUTES, "minutes")
        self.assertEqual(Upstox.UNIT_HOURS, "hours")
        self.assertEqual(Upstox.UNIT_DAYS, "days")
        self.assertEqual(Upstox.UNIT_WEEKS, "weeks")
        self.assertEqual(Upstox.UNIT_MONTHS, "months")

    @patch("requests.Session.request")
    def test_get_intraday_candle_data_v3_success(self, mock_request):
        """Test successful V3 intraday candle data retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "candles": [
                    [
                        "2024-01-12T15:15:00+05:30",
                        100.0,
                        105.0,
                        98.0,
                        102.0,
                        1000000,
                        0,
                    ],
                    [
                        "2024-01-12T14:45:00+05:30",
                        102.0,
                        108.0,
                        101.0,
                        106.0,
                        1200000,
                        0,
                    ],
                ]
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        data = self.upstox.get_intraday_candle_data_v3(
            instrument_key="NSE_EQ|INE848E01016",
            unit=self.upstox.UNIT_MINUTES,
            interval="5",
        )

        # Check that the correct V3 URL was called
        expected_url = "https://api.upstox.com/v3/historical-candle/intraday/NSE_EQ|INE848E01016/minutes/5"
        mock_request.assert_called_once_with("GET", expected_url, timeout=30)
        # The method should return the data portion of the response
        self.assertEqual(len(data["candles"]), 2)

    def test_get_intraday_candle_data_v3_invalid_unit(self):
        """Test V3 intraday data with invalid unit."""
        with self.assertRaises(InputException):
            self.upstox.get_intraday_candle_data_v3(
                instrument_key="NSE_EQ|INE848E01016", unit="invalid_unit", interval="5"
            )

    def test_get_intraday_candle_data_v3_invalid_interval(self):
        """Test V3 intraday data with invalid interval."""
        with self.assertRaises(InputException):
            self.upstox.get_intraday_candle_data_v3(
                instrument_key="NSE_EQ|INE848E01016",
                unit=self.upstox.UNIT_MINUTES,
                interval="500",  # Invalid: should be 1-300
            )

    @patch.object(Upstox, "_make_request")
    def test_get_full_market_quote_success(self, mock_make_request):
        """Test successful full market quote retrieval."""
        mock_make_request.return_value = {
            "NSE_EQ|INE848E01016": {
                "last_price": 2500.0,
                "volume": 1000000,
                "net_change": 50.0,
                "ohlc": {"open": 2450, "high": 2550, "low": 2400, "close": 2500},
            }
        }

        instrument_keys = ["NSE_EQ|INE848E01016"]
        data = self.upstox.get_full_market_quote(instrument_keys)

        mock_make_request.assert_called_once_with(
            "GET",
            "/market-quote/quotes",
            params={"instrument_key": "NSE_EQ|INE848E01016"},
        )
        self.assertIn("NSE_EQ|INE848E01016", data)
        self.assertEqual(data["NSE_EQ|INE848E01016"]["last_price"], 2500.0)

    def test_get_full_market_quote_too_many_keys(self):
        """Test full market quote with too many instrument keys."""
        too_many_keys = [f"TEST_KEY_{i}" for i in range(501)]

        with self.assertRaises(InputException):
            self.upstox.get_full_market_quote(too_many_keys)

    @patch.object(Upstox, "_make_request_v3")
    def test_get_ohlc_quotes_v3_success(self, mock_make_request_v3):
        """Test successful OHLC quotes V3 retrieval."""
        mock_make_request_v3.return_value = {
            "NSE_EQ|INE848E01016": {
                "live_ohlc": {"open": 2450, "high": 2550, "low": 2400, "close": 2500},
                "prev_ohlc": {"open": 2440, "high": 2540, "low": 2390, "close": 2490},
                "volume": 1000000,
                "ts": "2024-01-12T15:15:00+05:30",
            }
        }

        instrument_keys = ["NSE_EQ|INE848E01016"]
        data = self.upstox.get_ohlc_quotes_v3(instrument_keys, interval="5m")

        mock_make_request_v3.assert_called_once_with(
            "GET",
            "/market-quote/ohlc",
            params={"instrument_key": "NSE_EQ|INE848E01016", "interval": "5m"},
        )
        self.assertIn("NSE_EQ|INE848E01016", data)
        self.assertIn("live_ohlc", data["NSE_EQ|INE848E01016"])

    def test_get_ohlc_quotes_v3_invalid_interval(self):
        """Test OHLC quotes V3 with invalid interval."""
        instrument_keys = ["NSE_EQ|INE848E01016"]

        with self.assertRaises(InputException):
            self.upstox.get_ohlc_quotes_v3(instrument_keys, interval="invalid_interval")

    @patch.object(Upstox, "_make_request_v3")
    def test_get_ltp_quotes_v3_success(self, mock_make_request_v3):
        """Test successful LTP quotes V3 retrieval."""
        mock_make_request_v3.return_value = {
            "NSE_EQ|INE848E01016": {"ltp": 2500.0, "ts": "2024-01-12T15:15:00+05:30"}
        }

        instrument_keys = ["NSE_EQ|INE848E01016"]
        data = self.upstox.get_ltp_quotes_v3(instrument_keys)

        mock_make_request_v3.assert_called_once_with(
            "GET", "/market-quote/ltp", params={"instrument_key": "NSE_EQ|INE848E01016"}
        )
        self.assertIn("NSE_EQ|INE848E01016", data)
        self.assertEqual(data["NSE_EQ|INE848E01016"]["ltp"], 2500.0)

    @patch.object(Upstox, "_make_request_v3")
    def test_get_option_greeks_success(self, mock_make_request_v3):
        """Test successful option Greeks retrieval."""
        mock_make_request_v3.return_value = {
            "NFO_OPT|NIFTY24JAN18000CE": {
                "delta": 0.5,
                "gamma": 0.02,
                "theta": -0.01,
                "vega": 0.15,
            }
        }

        instrument_keys = ["NFO_OPT|NIFTY24JAN18000CE"]
        data = self.upstox.get_option_greeks(instrument_keys)

        mock_make_request_v3.assert_called_once_with(
            "GET",
            "/market-quote/option-greeks",
            params={"instrument_key": "NFO_OPT|NIFTY24JAN18000CE"},
        )
        self.assertIn("NFO_OPT|NIFTY24JAN18000CE", data)
        self.assertEqual(data["NFO_OPT|NIFTY24JAN18000CE"]["delta"], 0.5)

    @patch("requests.Session.request")
    def test_make_request_v3_success(self, mock_request):
        """Test successful V3 request method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {"v3_data": "value"},
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        data = self.upstox._make_request_v3("GET", "/test-endpoint")

        # Check that the correct V3 URL was called
        expected_url = "https://api.upstox.com/v3/test-endpoint"
        mock_request.assert_called_once_with("GET", expected_url, timeout=30)
        self.assertEqual(data, {"v3_data": "value"})

    @patch("requests.Session.request")
    def test_make_request_v3_error_response(self, mock_request):
        """Test V3 request method with error response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "error",
            "errors": [
                {
                    "error_code": "UDAPI1021",
                    "message": "Invalid instrument key format",
                    "property_path": None,
                    "invalid_value": None,
                }
            ],
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        with self.assertRaises(InputException) as context:
            self.upstox._make_request_v3("GET", "/test-endpoint")

        self.assertIn("Invalid instrument key format", str(context.exception))
        self.assertIn("UDAPI1021", str(context.exception))

    @patch.object(Upstox, "_make_request")
    def test_get_market_holidays_all(self, mock_make_request):
        """Test getting all market holidays for current year."""
        mock_make_request.return_value = [
            {
                "date": "2024-01-01",
                "description": "New Year Day",
                "holiday_type": "TRADING_HOLIDAY",
                "closed_exchanges": [],
                "open_exchanges": [
                    {
                        "exchange": "MCX",
                        "start_time": 1704079800000,
                        "end_time": 1704108600000,
                    }
                ],
            },
            {
                "date": "2024-01-26",
                "description": "Republic Day",
                "holiday_type": "TRADING_HOLIDAY",
                "closed_exchanges": ["NFO", "CDS", "BSE", "BCD", "MCX", "NSE", "BFO"],
                "open_exchanges": [],
            },
        ]

        holidays = self.upstox.get_market_holidays()

        mock_make_request.assert_called_once_with("GET", "/market-info/holidays")
        self.assertEqual(len(holidays), 2)
        self.assertEqual(holidays[0]["date"], "2024-01-01")
        self.assertEqual(holidays[1]["description"], "Republic Day")

    @patch.object(Upstox, "_make_request")
    def test_get_market_holidays_specific_date(self, mock_make_request):
        """Test getting market holidays for a specific date."""
        mock_make_request.return_value = [
            {
                "date": "2024-01-26",
                "description": "Republic Day",
                "holiday_type": "TRADING_HOLIDAY",
                "closed_exchanges": ["NFO", "CDS", "BSE", "BCD", "MCX", "NSE", "BFO"],
                "open_exchanges": [],
            }
        ]

        holidays = self.upstox.get_market_holidays(date="2024-01-26")

        mock_make_request.assert_called_once_with(
            "GET", "/market-info/holidays/2024-01-26"
        )
        self.assertEqual(len(holidays), 1)
        self.assertEqual(holidays[0]["date"], "2024-01-26")
        self.assertEqual(holidays[0]["holiday_type"], "TRADING_HOLIDAY")
        self.assertIn("NSE", holidays[0]["closed_exchanges"])

    @patch("requests.Session.post")
    def test_generate_extended_token_success(self, mock_post):
        """Test successful extended token generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "extended_token": "extended_token_here",
            "token_type": "extended",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        session_data = self.upstox.generate_extended_token(
            "auth_code", "api_secret", "https://example.com/callback"
        )

        self.assertEqual(session_data["extended_token"], "extended_token_here")

    @patch("requests.Session.post")
    def test_generate_extended_token_failure(self, mock_post):
        """Test failed extended token generation."""
        import requests

        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        with self.assertRaises(TokenException):
            self.upstox.generate_extended_token(
                "auth_code", "api_secret", "https://example.com/callback"
            )


if __name__ == "__main__":
    unittest.main()
