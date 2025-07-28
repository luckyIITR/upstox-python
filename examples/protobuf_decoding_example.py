"""
Protobuf Decoding Example for Upstox WebSocket Ticker

This example demonstrates how the Upstox WebSocket ticker handles Protobuf-encoded
messages using the official Market Data V3 Proto schema.
"""

import time
import json
from upstox import Upstox


def main():
    """Main function demonstrating Protobuf decoding."""

    # Initialize Upstox client
    api_key = "your_api_key_here"
    access_token = "your_access_token_here"

    upstox = Upstox(api_key, access_token)

    # Get WebSocket ticker instance
    ticker = upstox.get_ticker()

    # Define callback functions
    def on_connect():
        """Called when WebSocket connects."""
        print("✅ Connected to Upstox WebSocket feed")
        print("📡 Protobuf decoding is enabled")

    def on_disconnect(close_status_code, close_msg):
        """Called when WebSocket disconnects."""
        print(f"❌ Disconnected from WebSocket: {close_status_code} - {close_msg}")

    def on_error(error):
        """Called when WebSocket errors occur."""
        print(f"⚠️ WebSocket error: {error}")

    def on_market_status(segment_status):
        """Called when market status updates are received."""
        print("📊 Market Status Update (Protobuf decoded):")
        for segment, status in segment_status.items():
            print(f"  {segment}: {status}")

    def on_market_data(data):
        """Called when market data updates are received (Protobuf decoded)."""
        instrument_key = data["instrument_key"]
        request_mode = data.get("requestMode", "unknown")

        print(f"\n📈 Market Data for {instrument_key} (Mode: {request_mode}):")

        # LTPC Data (always available)
        if "ltpc" in data:
            ltpc = data["ltpc"]
            print(f"  LTPC:")
            print(f"    Last Traded Price: ₹{ltpc.get('ltp', 'N/A')}")
            print(f"    Close Price: ₹{ltpc.get('cp', 'N/A')}")
            print(f"    Last Traded Time: {ltpc.get('ltt', 'N/A')}")
            print(f"    Last Traded Quantity: {ltpc.get('ltq', 'N/A')}")

        # Market Level Data (for full modes)
        if "marketLevel" in data and "bidAskQuote" in data["marketLevel"]:
            bid_ask_quotes = data["marketLevel"]["bidAskQuote"]
            print(f"  Market Levels ({len(bid_ask_quotes)} levels):")
            for i, quote in enumerate(bid_ask_quotes[:3]):  # Show first 3 levels
                print(
                    f"    Level {i+1}: Bid {quote.get('bidQ', 'N/A')} @ ₹{quote.get('bidP', 'N/A')} | Ask {quote.get('askQ', 'N/A')} @ ₹{quote.get('askP', 'N/A')}"
                )

        # Option Greeks (for derivatives)
        if "optionGreeks" in data:
            greeks = data["optionGreeks"]
            print(f"  Option Greeks:")
            print(f"    Delta: {greeks.get('delta', 'N/A')}")
            print(f"    Gamma: {greeks.get('gamma', 'N/A')}")
            print(f"    Theta: {greeks.get('theta', 'N/A')}")
            print(f"    Vega: {greeks.get('vega', 'N/A')}")
            print(f"    Rho: {greeks.get('rho', 'N/A')}")

        # Market OHLC Data
        if "marketOHLC" in data and "ohlc" in data["marketOHLC"]:
            ohlc_data = data["marketOHLC"]["ohlc"]
            print(f"  OHLC Data:")
            for ohlc in ohlc_data:
                interval = ohlc.get("interval", "N/A")
                print(
                    f"    {interval}: O:₹{ohlc.get('open', 'N/A')} H:₹{ohlc.get('high', 'N/A')} L:₹{ohlc.get('low', 'N/A')} C:₹{ohlc.get('close', 'N/A')} V:{ohlc.get('vol', 'N/A')}"
                )

        # Additional market data (for full modes)
        if "atp" in data:
            print(f"  Additional Data:")
            print(f"    Average Traded Price: ₹{data.get('atp', 'N/A')}")
            print(f"    Volume Traded Today: {data.get('vtt', 'N/A')}")
            print(f"    Open Interest: {data.get('oi', 'N/A')}")
            print(f"    Implied Volatility: {data.get('iv', 'N/A')}")
            print(f"    Total Buy Quantity: {data.get('tbq', 'N/A')}")
            print(f"    Total Sell Quantity: {data.get('tsq', 'N/A')}")

    def on_message(data):
        """Called for all messages (including Protobuf decoded)."""
        # Uncomment to see raw decoded data
        # print(f"Raw decoded data: {json.dumps(data, indent=2)}")
        pass

    # Set up callbacks
    ticker.set_callbacks(
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        on_error=on_error,
        on_market_status=on_market_status,
        on_market_data=on_market_data,
        on_message=on_message,
    )

    try:
        # Connect to WebSocket
        print("🔌 Connecting to Upstox WebSocket...")
        ticker.connect()

        # Example instrument keys (replace with actual instrument keys)
        instrument_keys = [
            "NSE_EQ|INE848E01016",  # SBIN
            "NSE_EQ|INE002A01018",  # RELIANCE
            "NSE_INDEX|Nifty Bank",  # Nifty Bank Index
            "NSE_FO|45450",  # Example F&O instrument
        ]

        # Subscribe to different modes to demonstrate Protobuf decoding
        print("\n📡 Subscribing to market data with Protobuf decoding...")

        # LTPC mode (basic data)
        print("  Subscribing to LTPC mode...")
        ticker.subscribe(instrument_keys[:1], mode="ltpc")

        time.sleep(2)

        # Full mode (comprehensive data)
        print("  Subscribing to Full mode...")
        ticker.subscribe(instrument_keys[1:2], mode="full")

        time.sleep(2)

        # Option Greeks mode (derivatives data)
        print("  Subscribing to Option Greeks mode...")
        ticker.subscribe(instrument_keys[2:], mode="option_greeks")

        # Keep connection alive and receive data
        print("\n🎧 Listening for Protobuf-encoded market data updates...")
        print("Press Ctrl+C to stop")

        # Listen for 60 seconds
        start_time = time.time()
        while time.time() - start_time < 60:
            time.sleep(1)

            # Show subscription status periodically
            if int(time.time() - start_time) % 10 == 0:
                status = ticker.get_subscription_status()
                print(
                    f"\n📊 Status: Connected={status['is_connected']}, Subscriptions={len(status['subscriptions'])}"
                )

    except KeyboardInterrupt:
        print("\n⏹️ Stopping by user request...")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Disconnect
        print("🔌 Disconnecting...")
        ticker.disconnect()
        print("✅ Disconnected")


def protobuf_decoding_demo():
    """Demonstrate Protobuf decoding capabilities."""

    api_key = "your_api_key_here"
    access_token = "your_access_token_here"

    upstox = Upstox(api_key, access_token)

    # Use context manager for automatic cleanup
    with upstox.get_ticker() as ticker:
        # Set up callbacks
        def on_market_data(data):
            """Process Protobuf-decoded market data."""
            instrument = data["instrument_key"]
            mode = data.get("requestMode", "unknown")

            # Extract data based on mode
            if mode == "ltpc":
                ltp = data.get("ltpc", {}).get("ltp", "N/A")
                print(f"{instrument} (LTPC): ₹{ltp}")

            elif mode == "full":
                ltp = data.get("ltpc", {}).get("ltp", "N/A")
                bid_ask = data.get("marketLevel", {}).get("bidAskQuote", [])
                if bid_ask:
                    best_bid = bid_ask[0].get("bidP", "N/A")
                    best_ask = bid_ask[0].get("askP", "N/A")
                    print(
                        f"{instrument} (Full): ₹{ltp} | Bid: ₹{best_bid} | Ask: ₹{best_ask}"
                    )
                else:
                    print(f"{instrument} (Full): ₹{ltp}")

            elif mode == "option_greeks":
                ltp = data.get("ltpc", {}).get("ltp", "N/A")
                delta = data.get("optionGreeks", {}).get("delta", "N/A")
                print(f"{instrument} (Greeks): ₹{ltp} | Delta: {delta}")

        ticker.set_callbacks(on_market_data=on_market_data)

        # Subscribe to different modes
        instruments = [
            "NSE_EQ|INE848E01016",  # SBIN
            "NSE_EQ|INE002A01018",  # RELIANCE
            "NSE_FO|45450",  # F&O instrument
        ]

        ticker.subscribe(instruments[:1], mode="ltpc")
        ticker.subscribe(instruments[1:2], mode="full")
        ticker.subscribe(instruments[2:], mode="option_greeks")

        print("Listening for 30 seconds with Protobuf decoding...")
        time.sleep(30)


def protobuf_error_handling():
    """Demonstrate Protobuf error handling."""

    api_key = "your_api_key_here"
    access_token = "your_access_token_here"

    upstox = Upstox(api_key, access_token)
    ticker = upstox.get_ticker()

    def on_error(error):
        """Handle Protobuf decoding errors."""
        print(f"Protobuf Error: {error}")

    def on_market_data(data):
        """Handle successfully decoded data."""
        print(f"Successfully decoded data for {data.get('instrument_key', 'unknown')}")

    ticker.set_callbacks(on_error=on_error, on_market_data=on_market_data)

    try:
        ticker.connect()
        ticker.subscribe(["NSE_EQ|INE848E01016"], mode="ltpc")
        time.sleep(10)
    finally:
        ticker.disconnect()


if __name__ == "__main__":
    print("🚀 Upstox Protobuf Decoding Examples")
    print("=" * 50)

    # Uncomment the example you want to run

    # Basic Protobuf decoding example
    main()

    # Advanced Protobuf decoding with different modes
    # protobuf_decoding_demo()

    # Protobuf error handling example
    # protobuf_error_handling()
