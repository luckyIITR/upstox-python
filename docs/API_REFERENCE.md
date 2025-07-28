# Upstox Python Client - API Reference

This document provides a comprehensive reference for the Upstox Python client library.

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Client Initialization](#client-initialization)
4. [User Profile](#user-profile)
5. [Orders](#orders)
6. [Portfolio](#portfolio)
7. [Market Data](#market-data)
8. [Mutual Funds](#mutual-funds)
9. [GTT Orders](#gtt-orders)
10. [WebSocket](#websocket)
11. [Error Handling](#error-handling)
12. [Constants](#constants)

## Installation

```bash
pip install upstox
```

## Authentication

The Upstox API uses OAuth2 for authentication. The flow involves:

1. Getting a login URL
2. User authentication
3. Receiving authorization code
4. Generating access token

### Getting Login URL

```python
from upstox import Upstox

upstox = Upstox(api_key="your_api_key")
login_url = upstox.get_login_url(
    redirect_uri="https://your-redirect-uri.com/callback",
    state="optional_state_parameter"
)
```

### Generating Session

```python
session_data = upstox.generate_session(
    authorization_code="code_from_redirect",
    api_secret="your_api_secret",
    redirect_uri="your_redirect_uri"  # Must match the one used in get_login_url
)
access_token = session_data['access_token']
upstox.set_access_token(access_token)
```

### Extended Tokens

For long-term read-only access, you can generate extended tokens:

```python
extended_data = upstox.generate_extended_token(
    authorization_code="code_from_redirect",
    api_secret="your_api_secret",
    redirect_uri="your_redirect_uri"
)
extended_token = extended_data['extended_token']
```

**Supported APIs with Extended Tokens:**
- Get Positions
- Get Holdings
- Get Order Details
- Get Order History
- Get Order Book

**Note**: Extended tokens are available for multi-client applications upon request. Contact Upstox support for enrollment.

## Client Initialization

```python
from upstox import Upstox

# Basic initialization
upstox = Upstox(api_key="your_api_key")

# With access token
upstox = Upstox(
    api_key="your_api_key",
    access_token="your_access_token",
    timeout=30,
    debug=True
)
```

### Parameters

- `api_key` (str): Your Upstox API key
- `access_token` (str, optional): Access token for authenticated requests
- `timeout` (int): Request timeout in seconds (default: 30)
- `debug` (bool): Enable debug logging (default: False)

## User Profile

### Get User Profile

```python
profile = upstox.get_profile()
```

Returns user profile information including name, email, mobile, etc.

### Get Trading Charges

```python
charges = upstox.get_charges(
    symbol="RELIANCE-EQ",
    quantity=100,
    price=2500.0,
    product=upstox.PRODUCT_CNC
)
```

### Get Margin Requirements

```python
margins = upstox.get_margins(
    symbol="RELIANCE-EQ",
    quantity=100,
    price=2500.0,
    product=upstox.PRODUCT_CNC
)
```

## Orders

### Place Order

```python
order_id = upstox.place_order(
    symbol="RELIANCE-EQ",
    quantity=10,
    side=upstox.TRANSACTION_TYPE_BUY,
    order_type=upstox.ORDER_TYPE_MARKET,
    product=upstox.PRODUCT_CNC,
    price=None,  # Required for limit orders
    trigger_price=None,  # For stop orders
    validity=upstox.VALIDITY_DAY,
    disclosed_quantity=None,
    tag="my_order_tag"
)
```

### Get Orders

```python
# Get all orders
orders = upstox.get_orders()

# Get specific order
order_details = upstox.get_orders(order_id="order_id")
```

### Cancel Order

```python
result = upstox.cancel_order(order_id="order_id")
```

### Modify Order

```python
result = upstox.modify_order(
    order_id="order_id",
    quantity=20,  # New quantity
    price=2500.0,  # New price
    order_type="limit",  # New order type
    trigger_price=2400.0  # New trigger price
)
```

## Portfolio

### Get Holdings

```python
holdings = upstox.get_holdings()
```

Returns list of long-term holdings.

### Get Positions

```python
positions = upstox.get_positions()
```

Returns current positions.

### Get Portfolio Summary

```python
portfolio = upstox.get_portfolio()
```

Returns portfolio summary.

### Get Trade P&L

```python
pnl = upstox.get_trade_profit_loss(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Market Data

### Get Quote

```python
quote = upstox.get_quote("RELIANCE-EQ")
```

### Get Historical Data

```python
# Legacy API
historical_data = upstox.get_historical_data(
    symbol="RELIANCE-EQ",
    interval="1D",  # 1D, 1W, 1M, etc.
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# V3 API with custom intervals
v3_data = upstox.get_historical_candle_data_v3(
    instrument_key="NSE_EQ|INE848E01016",
    unit=upstox.UNIT_MINUTES,  # minutes, hours, days, weeks, months
    interval="5",  # 1-300 for minutes, 1-5 for hours, 1 for others
    to_date="2024-01-31",
    from_date="2024-01-01"  # optional
)
```

**V3 API Features:**
- Custom time intervals for minutes (1-300) and hours (1-5)
- Granular data control and improved flexibility
- Consistent response structure with legacy API
- Efficient handling of large data volumes
- Historical availability from January 2000 (days/weeks/months)
- Historical availability from January 2022 (minutes/hours)
- **Uses V3 base URL**: `https://api.upstox.com/v3` (different from V2 APIs)

### Get Instruments

```python
instruments = upstox.get_instruments("NSE")
```

### Get Market Info

```python
market_info = upstox.get_market_info()
```

### Get Option Chain

```python
option_chain = upstox.get_option_chain("NIFTY24JAN18000CE")
```

### Get Intraday Candle Data V3

```python
# Get 5-minute intraday data for current trading day
intraday_data = upstox.get_intraday_candle_data_v3(
    instrument_key="NSE_EQ|INE848E01016",
    unit=upstox.UNIT_MINUTES,
    interval="5"
)
```

**Features:**
- Custom time intervals for minutes (1-300), hours (1-5), and days (1)
- Real-time OHLC data for current trading day
- Useful for technical analysis and algorithmic trading
- **Uses V3 base URL**: `https://api.upstox.com/v3`

### Get Full Market Quotes

```python
# Get full market quotes for multiple instruments (up to 500)
instrument_keys = ["NSE_EQ|INE848E01016", "NSE_EQ|INE009A01021"]
full_quotes = upstox.get_full_market_quote(instrument_keys)
```

**Features:**
- Complete market data snapshot for up to 500 instruments
- Includes OHLC, depth, volume, and other market data
- Real-time data from exchanges

### Get OHLC Quotes V3

```python
# Get 5-minute OHLC quotes with enhanced features
instrument_keys = ["NSE_EQ|INE848E01016", "NSE_EQ|INE009A01021"]
ohlc_quotes = upstox.get_ohlc_quotes_v3(instrument_keys, interval="5m")
```

**Features:**
- `live_ohlc`: Current OHLC candle
- `prev_ohlc`: Previous minute's OHLC candle
- `volume`: Trading volume data
- `ts`: OHLC candle's start time
- Supports intervals: 1m, 5m, 15m, 30m, 1h, 1d

### Get LTP Quotes V3

```python
# Get Last Traded Price quotes for multiple instruments
instrument_keys = ["NSE_EQ|INE848E01016", "NSE_EQ|INE009A01021"]
ltp_quotes = upstox.get_ltp_quotes_v3(instrument_keys)
```

**Features:**
- Real-time Last Traded Price data
- Supports up to 500 instruments per request
- Includes timestamp information

### Get Option Greeks

```python
# Get option Greeks for derivatives
option_keys = ["NFO_OPT|NIFTY24JAN18000CE", "NFO_OPT|NIFTY24JAN18000PE"]
greeks = upstox.get_option_greeks(option_keys)
```

**Features:**
- Delta, Gamma, Theta, and Vega values
- Specifically for options and futures instruments
- Supports up to 500 instruments per request

### Custom V3 API Requests

```python
# Make custom requests to any V3 API endpoint
custom_data = upstox.make_v3_request('GET', '/custom-endpoint', params={'key': 'value'})

# POST request with JSON data
response = upstox.make_v3_request('POST', '/custom-endpoint', json={'data': 'value'})

# PUT request with form data
response = upstox.make_v3_request('PUT', '/custom-endpoint', data={'field': 'value'})
```

**Features:**
- Access to any V3 API endpoint not covered by specific methods
- Same error handling and response parsing as other methods
- Uses V3 base URL (`https://api.upstox.com/v3`)
- Supports all HTTP methods (GET, POST, PUT, DELETE)
- Full parameter support (params, json, data, headers, etc.)

**Use Cases:**
- New V3 APIs not yet implemented in the client library
- Custom endpoints specific to your application
- Experimental or beta V3 APIs
- Direct access to V3 API functionality

## Mutual Funds

### Place Mutual Fund Order

```python
mf_order_id = upstox.place_mf_order(
    symbol="INF090I01239",
    amount=5000.0,
    side=upstox.TRANSACTION_TYPE_BUY,
    tag="mf_order"
)
```

### Get Mutual Fund Orders

```python
mf_orders = upstox.get_mf_orders()
```

### Cancel Mutual Fund Order

```python
result = upstox.cancel_mf_order(order_id="mf_order_id")
```

### Get Mutual Fund Holdings

```python
mf_holdings = upstox.get_mf_holdings()
```

### Get Mutual Fund Instruments

```python
mf_instruments = upstox.get_mf_instruments()
```

## GTT Orders

### Place GTT Order

```python
gtt_id = upstox.place_gtt(
    symbol="RELIANCE-EQ",
    quantity=5,
    side=upstox.TRANSACTION_TYPE_SELL,
    trigger_price=2600.0,
    order_type=upstox.ORDER_TYPE_LIMIT,
    price=2595.0,
    validity=30  # Days
)
```

### Get GTT Orders

```python
gtt_orders = upstox.get_gtt_orders()
```

### Cancel GTT Order

```python
result = upstox.cancel_gtt(gtt_id="gtt_id")
```

### Modify GTT Order

```python
result = upstox.modify_gtt(
    gtt_id="gtt_id",
    trigger_price=2650.0,
    price=2645.0
)
```

## WebSocket

### Initialize WebSocket

```python
ws = upstox.get_websocket()
```

### Set Callbacks

```python
def on_ticks(ws, ticks):
    print(f"Received ticks: {ticks}")

def on_connect(ws, response):
    print("Connected to WebSocket")

def on_close(ws, code, reason):
    print(f"WebSocket closed: {code} - {reason}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_order_update(ws, order_update):
    print(f"Order update: {order_update}")

ws.on_ticks = on_ticks
ws.on_connect = on_connect
ws.on_close = on_close
ws.on_error = on_error
ws.on_order_update = on_order_update
```

### Connect and Subscribe

```python
# Connect
ws.connect(threaded=True)

# Subscribe to tokens
tokens = ["NSE:RELIANCE-EQ", "NSE:TCS-EQ"]
ws.subscribe(tokens)

# Set streaming mode
ws.set_mode(ws.MODE_FULL, tokens)
```

### WebSocket Methods

- `connect(threaded=True)`: Establish connection
- `subscribe(tokens)`: Subscribe to market data
- `unsubscribe(tokens)`: Unsubscribe from market data
- `set_mode(mode, tokens)`: Set streaming mode
- `resubscribe()`: Resubscribe to all tokens
- `close(code=None, reason=None)`: Close connection
- `stop()`: Stop WebSocket client
- `is_connected()`: Check connection status

## Error Handling

The library raises specific exceptions for different error scenarios:

```python
from upstox.exceptions import (
    UpstoxException, TokenException, OrderException,
    PermissionException, InputException, NetworkException
)

try:
    order_id = upstox.place_order(...)
except TokenException as e:
    print(f"Authentication error: {e}")
except OrderException as e:
    print(f"Order error: {e}")
except PermissionException as e:
    print(f"Permission error: {e}")
except InputException as e:
    print(f"Input error: {e}")
except NetworkException as e:
    print(f"Network error: {e}")
except UpstoxException as e:
    print(f"General error: {e}")
```

### Exception Types

- `UpstoxException`: Base exception class
- `TokenException`: Authentication and token-related errors
- `OrderException`: Order-related errors
- `PermissionException`: Permission errors
- `InputException`: Input validation errors
- `NetworkException`: Network and server errors
- `DataException`: Data-related errors
- `RateLimitException`: Rate limit exceeded
- `ValidationException`: Validation errors
- `ConfigurationException`: Configuration errors

## Constants

### Order Types

```python
upstox.ORDER_TYPE_MARKET = "market"
upstox.ORDER_TYPE_LIMIT = "limit"
upstox.ORDER_TYPE_STOP_LOSS = "stop_loss"
upstox.ORDER_TYPE_STOP_LOSS_MARKET = "stop_loss_market"
```

### Transaction Types

```python
upstox.TRANSACTION_TYPE_BUY = "buy"
upstox.TRANSACTION_TYPE_SELL = "sell"
```

### Product Types

```python
upstox.PRODUCT_CNC = "cnc"    # Cash and Carry
upstox.PRODUCT_MIS = "mis"    # Margin Intraday Square Off
upstox.PRODUCT_NRML = "nrml"  # Normal
upstox.PRODUCT_CO = "co"      # Cover Order
upstox.PRODUCT_BO = "bo"      # Bracket Order
```

### Validity Types

```python
upstox.VALIDITY_DAY = "day"   # Day
upstox.VALIDITY_IOC = "ioc"   # Immediate or Cancel
upstox.VALIDITY_FOK = "fok"   # Fill or Kill
```

### Exchanges

```python
upstox.EXCHANGE_NSE = "NSE"
upstox.EXCHANGE_BSE = "BSE"
upstox.EXCHANGE_NFO = "NFO"
upstox.EXCHANGE_CDS = "CDS"
upstox.EXCHANGE_MCX = "MCX"
```

### Historical Data V3 Units

```python
upstox.UNIT_MINUTES = "minutes"
upstox.UNIT_HOURS = "hours"
upstox.UNIT_DAYS = "days"
upstox.UNIT_WEEKS = "weeks"
upstox.UNIT_MONTHS = "months"
```

### Historical Data V3 Intervals

- **Minutes**: 1, 2, 3, ..., 300
- **Hours**: 1, 2, 3, 4, 5
- **Days, Weeks, Months**: 1

### WebSocket Modes

```python
ws.MODE_LTP = "ltp"      # Last Traded Price
ws.MODE_QUOTE = "quote"  # Quote
ws.MODE_FULL = "full"    # Full market data
```

## Rate Limits

The library automatically handles rate limits as per Upstox API guidelines. If you hit rate limits, the library will retry with exponential backoff.

## Best Practices

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Token Management**: Store and reuse access tokens
3. **Rate Limiting**: Respect API rate limits
4. **Logging**: Enable debug logging for development
5. **WebSocket**: Use threaded mode for WebSocket connections
6. **Validation**: Validate inputs before making API calls

## Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: Basic authentication and API usage
- `websocket_example.py`: Real-time data streaming
- `order_management.py`: Order placement and management

## Support

For support and questions:
- Check the [Upstox API Documentation](https://upstox.com/developer/api-documentation/open-api)
- Create an issue on GitHub
- Contact Upstox support 