# Upstox Python Client

A Python client library for the Upstox API that provides easy access to trading, portfolio management, and market data functionality. This library follows the official [Upstox API documentation](https://upstox.com/developer/api-documentation/open-api) and authentication flow.

## Features

- **Authentication**: OAuth2 based authentication flow with extended token support
- **Trading**: Place, modify, and cancel orders
- **Portfolio**: Get holdings, positions, and portfolio details
- **Market Data**: Real-time quotes, historical data, and market information
- **WebSocket**: Real-time data streaming
- **Mutual Funds**: Mutual fund orders and holdings
- **GTT Orders**: Good Till Triggered orders
- **Charges & Margins**: Get trading charges and margin requirements
- **Historical Data V3**: Enhanced historical candle data with custom intervals
- **Intraday Data V3**: Real-time intraday candle data with custom intervals
- **Market Quotes V3**: Full market quotes, OHLC quotes, LTP quotes for multiple instruments
- **Option Greeks**: Delta, Gamma, Theta, Vega values for derivatives

## Installation

```bash
pip install upstox
```

### Protobuf Setup (for WebSocket functionality)

The WebSocket ticker uses Protobuf encoding for efficient data transmission. To enable Protobuf decoding:

1. **Install Protocol Buffers compiler**:
   ```bash
   # macOS
   brew install protobuf
   
   # Ubuntu/Debian
   sudo apt-get install protobuf-compiler
   
   # Windows: Download from https://github.com/protocolbuffers/protobuf/releases
   ```

2. **Generate Protobuf classes**:
   ```bash
   python generate_protobuf.py
   ```

3. **Install Python Protobuf library** (included in requirements.txt):
   ```bash
   pip install protobuf>=4.21.0
   ```

## Quick Start

```python
import logging
from upstox import Upstox

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the client
upstox = Upstox(api_key="your_api_key")

# Get login URL
login_url = upstox.get_login_url()
print(f"Login URL: {login_url}")

# After user login, get the authorization code from redirect URL
# Then generate session
data = upstox.generate_session("authorization_code_here", api_secret="your_secret", redirect_uri="https://your-redirect-uri.com/callback")
upstox.set_access_token(data["access_token"])

# Get user profile
profile = upstox.get_profile()
print(f"User: {profile['name']}")

# Get holdings
holdings = upstox.get_holdings()
print(f"Holdings: {holdings}")

# Real-time market data with WebSocket
ticker = upstox.get_ticker()

def on_market_data(data):
    print(f"{data['instrument_key']}: ₹{data['ltpc'].get('ltp')}")

ticker.set_callbacks(on_market_data=on_market_data)
ticker.connect()
ticker.subscribe(['NSE_EQ|INE848E01016'], mode='ltpc')

# Place an order
try:
    order_id = upstox.place_order(
        symbol="RELIANCE-EQ",
        quantity=1,
        side="buy",
        order_type="market",
        product="cnc"
    )
    print(f"Order placed with ID: {order_id}")
except Exception as e:
    print(f"Order placement failed: {e}")

## WebSocket Real-time Data

The library provides a WebSocket client for real-time market data streaming:

```python
# Get WebSocket ticker instance
ticker = upstox.get_ticker()

# Set up callbacks
def on_market_data(data):
    instrument = data['instrument_key']
    ltp = data['ltpc'].get('ltp', 'N/A')
    print(f"{instrument}: ₹{ltp}")

def on_market_status(segment_status):
    print("Market segments:", segment_status)

ticker.set_callbacks(
    on_market_data=on_market_data,
    on_market_status=on_market_status
)

# Connect and subscribe
ticker.connect()
ticker.subscribe(['NSE_EQ|INE848E01016'], mode='ltpc')

# Keep connection alive
import time
time.sleep(60)

# Disconnect
ticker.disconnect()
```

### Subscription Modes

- **LTPC**: Latest Trading Price and Close Price (up to 5000 instruments)
- **Option Greeks**: Delta, Gamma, Theta, Vega, Rho (up to 3000 instruments)
- **Full**: LTPC + 5 market levels + extended metadata (up to 2000 instruments)
- **Full D30**: LTPC + 30 market levels + extended metadata (up to 2000 instruments)

### Features

- **Automatic Reconnection**: Handles connection drops automatically
- **Heartbeat Support**: Maintains connection with ping/pong frames
- **Multiple Modes**: Support for different subscription modes
- **Callback System**: Event-driven data processing
- **Context Manager**: Use with `with` statement for automatic cleanup
- **Protobuf Decoding**: Full support for Protobuf-encoded messages using official schema

## Authentication Flow

### Web Application Flow

1. **Initialize client and get login URL**:
   ```python
   upstox = Upstox(api_key="your_api_key")
   login_url = upstox.get_login_url()
   ```

2. **Redirect user to login URL**

3. **Handle callback and get authorization code**:
   ```python
   # In your callback endpoint
   authorization_code = request.args.get('code')
   ```

4. **Generate session**:
   ```python
   data = upstox.generate_session(authorization_code, api_secret="your_secret", redirect_uri="your_redirect_uri")
   access_token = data["access_token"]
   ```

5. **Store access token and use for API calls**:
   ```python
   upstox.set_access_token(access_token)
   ```

### Extended Tokens

For long-term read-only access, you can generate extended tokens that are valid for one year:

```python
# Generate extended token for read-only operations
extended_data = upstox.generate_extended_token(
    authorization_code="your_auth_code",
    api_secret="your_secret",
    redirect_uri="your_redirect_uri"
)
extended_token = extended_data["extended_token"]
```

**Note**: Extended tokens are available for multi-client applications upon request. Contact Upstox support for enrollment.

## API Examples

### Orders

```python
# Place order
order_id = upstox.place_order(
    symbol="INFY-EQ",
    quantity=10,
    side="buy",
    order_type="limit",
    price=1500.50,
    product="cnc"
)

# Get orders
orders = upstox.get_orders()

# Cancel order
upstox.cancel_order(order_id)

# Modify order
upstox.modify_order(
    order_id=order_id,
    quantity=15,
    price=1501.00
)
```

### Portfolio

```python
# Get holdings
holdings = upstox.get_holdings()

# Get positions
positions = upstox.get_positions()

# Get portfolio
portfolio = upstox.get_portfolio()
```

### Market Data

```python
# Get quote
quote = upstox.get_quote("RELIANCE-EQ")

# Get historical data (legacy API)
historical_data = upstox.get_historical_data(
    symbol="RELIANCE-EQ",
    interval="1D",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get historical candle data V3 (new API with custom intervals)
v3_data = upstox.get_historical_candle_data_v3(
    instrument_key="NSE_EQ|INE848E01016",
    unit=upstox.UNIT_MINUTES,
    interval="5",
    to_date="2024-01-31",
    from_date="2024-01-01"
)

# Get intraday candle data V3
intraday_data = upstox.get_intraday_candle_data_v3(
    instrument_key="NSE_EQ|INE848E01016",
    unit=upstox.UNIT_MINUTES,
    interval="5"
)

# Get full market quotes for multiple instruments
instrument_keys = ["NSE_EQ|INE848E01016", "NSE_EQ|INE009A01021"]
full_quotes = upstox.get_full_market_quote(instrument_keys)

# Get OHLC quotes V3
ohlc_quotes = upstox.get_ohlc_quotes_v3(instrument_keys, interval="5m")

# Get LTP quotes V3
ltp_quotes = upstox.get_ltp_quotes_v3(instrument_keys)

# Get option Greeks for derivatives
option_keys = ["NFO_OPT|NIFTY24JAN18000CE"]
greeks = upstox.get_option_greeks(option_keys)

# Custom V3 API requests (for any V3 endpoint not covered by specific methods)
custom_data = upstox.make_v3_request('GET', '/custom-endpoint', params={'key': 'value'})

# Get instruments
instruments = upstox.get_instruments("NSE")
```

### WebSocket (Real-time Data)

```python
def on_ticks(ws, ticks):
    print(f"Ticks: {ticks}")

def on_connect(ws, response):
    print("Connected to WebSocket")
    ws.subscribe(["NSE:RELIANCE-EQ"])
    ws.set_mode("full", ["NSE:RELIANCE-EQ"])

def on_close(ws, code, reason):
    print("WebSocket connection closed")

# Initialize WebSocket
ws = upstox.get_websocket()

# Set callbacks
ws.on_ticks = on_ticks
ws.on_connect = on_connect
ws.on_close = on_close

# Connect
ws.connect()
```

## Error Handling

The library raises specific exceptions for different error scenarios:

```python
from upstox.exceptions import UpstoxException, OrderException, TokenException

try:
    order_id = upstox.place_order(...)
except OrderException as e:
    print(f"Order error: {e}")
except TokenException as e:
    print(f"Token error: {e}")
except UpstoxException as e:
    print(f"General error: {e}")
```

## Rate Limits

The library automatically handles rate limits as per Upstox API guidelines. If you hit rate limits, the library will retry with exponential backoff.

## Documentation

- [Upstox API Documentation](https://upstox.com/developer/api-documentation/open-api)
- [Python Client Documentation](https://github.com/upstox/upstox-python)

## License

This library is licensed under the MIT License.

## Support

For support and questions:
- Create an issue on GitHub
- Contact Upstox support
- Check the [API documentation](https://upstox.com/developer/api-documentation/open-api) 