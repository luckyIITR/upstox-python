#!/usr/bin/env python3
"""
Market Quotes V3 Example for Upstox Python client.

This example demonstrates the new V3 market quote APIs and intraday candle data.
"""

import logging
from upstox import Upstox

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)


def main():
    # Initialize the client
    api_key = "your_api_key_here"
    access_token = "your_access_token_here"

    upstox = Upstox(api_key=api_key, access_token=access_token, debug=True)

    print("=== Upstox Market Quotes V3 Example ===\n")

    # Example instrument keys
    instrument_keys = [
        "NSE_EQ|INE848E01016",  # Reliance Industries
        "NSE_EQ|INE009A01021",  # TCS
        "NSE_EQ|INE002A01018",  # Infosys
    ]

    print("1. Getting Intraday Candle Data V3...")
    try:
        # Get 5-minute intraday candle data
        data = upstox.get_intraday_candle_data_v3(
            instrument_key=instrument_keys[0], unit=upstox.UNIT_MINUTES, interval="5"
        )

        print(f"Status: Success")
        candles = data.get("candles", [])
        print(f"Number of candles: {len(candles)}")

        if candles:
            print("Sample candle data:")
            for i, candle in enumerate(candles[:3]):  # Show first 3 candles
                timestamp, open_price, high, low, close, volume, open_interest = candle
                print(
                    f"  Candle {i+1}: {timestamp} - O:{open_price} H:{high} L:{low} C:{close} V:{volume}"
                )
        print()

    except Exception as e:
        print(f"Failed to get intraday data: {e}\n")

    print("2. Getting Full Market Quotes...")
    try:
        data = upstox.get_full_market_quote(instrument_keys)

        print(f"Status: Success")
        print(f"Number of instruments: {len(data)}")

        # Show sample data for first instrument
        if data:
            first_key = list(data.keys())[0]
            first_instrument = data[first_key]
            print(f"Sample data for {first_key}:")
            print(f"  Last Price: {first_instrument.get('last_price', 'N/A')}")
            print(f"  Volume: {first_instrument.get('volume', 'N/A')}")
            print(f"  Net Change: {first_instrument.get('net_change', 'N/A')}")

            # Show OHLC data
            ohlc = first_instrument.get("ohlc", {})
            if ohlc:
                print(
                    f"  OHLC - O:{ohlc.get('open')} H:{ohlc.get('high')} L:{ohlc.get('low')} C:{ohlc.get('close')}"
                )
        print()

    except Exception as e:
        print(f"Failed to get full market quotes: {e}\n")

    print("3. Getting OHLC Quotes V3...")
    try:
        data = upstox.get_ohlc_quotes_v3(instrument_keys, interval="5m")

        print(f"Status: Success")
        print(f"Number of instruments: {len(data)}")

        # Show sample data for first instrument
        if data:
            first_key = list(data.keys())[0]
            first_instrument = data[first_key]
            print(f"Sample data for {first_key}:")

            # Show live OHLC
            live_ohlc = first_instrument.get("live_ohlc", {})
            if live_ohlc:
                print(
                    f"  Live OHLC - O:{live_ohlc.get('open')} H:{live_ohlc.get('high')} L:{live_ohlc.get('low')} C:{live_ohlc.get('close')}"
                )

            # Show previous OHLC
            prev_ohlc = first_instrument.get("prev_ohlc", {})
            if prev_ohlc:
                print(
                    f"  Previous OHLC - O:{prev_ohlc.get('open')} H:{prev_ohlc.get('high')} L:{prev_ohlc.get('low')} C:{prev_ohlc.get('close')}"
                )

            # Show volume and timestamp
            print(f"  Volume: {first_instrument.get('volume', 'N/A')}")
            print(f"  Timestamp: {first_instrument.get('ts', 'N/A')}")
        print()

    except Exception as e:
        print(f"Failed to get OHLC quotes V3: {e}\n")

    print("4. Getting LTP Quotes V3...")
    try:
        data = upstox.get_ltp_quotes_v3(instrument_keys)

        print(f"Status: Success")
        print(f"Number of instruments: {len(data)}")

        # Show sample data for first instrument
        if data:
            first_key = list(data.keys())[0]
            first_instrument = data[first_key]
            print(f"Sample data for {first_key}:")
            print(f"  Last Traded Price: {first_instrument.get('ltp', 'N/A')}")
            print(f"  Timestamp: {first_instrument.get('ts', 'N/A')}")
        print()

    except Exception as e:
        print(f"Failed to get LTP quotes V3: {e}\n")

    print("5. Getting Option Greeks...")
    try:
        # Example option instrument keys (you would get these from get_instruments API)
        option_instrument_keys = [
            "NFO_OPT|NIFTY24JAN18000CE",
            "NFO_OPT|NIFTY24JAN18000PE",
        ]

        data = upstox.get_option_greeks(option_instrument_keys)

        print(f"Status: Success")
        print(f"Number of instruments: {len(data)}")

        # Show sample data for first instrument
        if data:
            first_key = list(data.keys())[0]
            first_instrument = data[first_key]
            print(f"Sample data for {first_key}:")
            print(f"  Delta: {first_instrument.get('delta', 'N/A')}")
            print(f"  Gamma: {first_instrument.get('gamma', 'N/A')}")
            print(f"  Theta: {first_instrument.get('theta', 'N/A')}")
            print(f"  Vega: {first_instrument.get('vega', 'N/A')}")
        print()

    except Exception as e:
        print(f"Failed to get option Greeks: {e}\n")

    print("6. Custom V3 API Requests...")
    try:
        # Example of using the custom V3 request method for any V3 endpoint
        # This is useful for APIs that don't have specific methods yet

        # Custom GET request to V3 API
        custom_data = upstox.make_v3_request(
            "GET",
            "/some-custom-endpoint",
            params={"param1": "value1", "param2": "value2"},
        )
        print(f"Custom V3 GET response: {custom_data}")

        # Custom POST request to V3 API
        custom_post_data = upstox.make_v3_request(
            "POST", "/some-custom-endpoint", json={"data": "value", "action": "create"}
        )
        print(f"Custom V3 POST response: {custom_post_data}")

    except Exception as e:
        print(f"Custom V3 request error (expected if endpoint doesn't exist): {e}")

    print("7. Error handling examples...")

    # Test invalid unit for intraday
    try:
        data = upstox.get_intraday_candle_data_v3(
            instrument_key=instrument_keys[0], unit="invalid_unit", interval="5"
        )
    except Exception as e:
        print(f"Invalid unit error (expected): {e}")

    # Test invalid interval for OHLC
    try:
        data = upstox.get_ohlc_quotes_v3(instrument_keys, interval="invalid_interval")
    except Exception as e:
        print(f"Invalid interval error (expected): {e}")

    # Test too many instrument keys
    try:
        too_many_keys = [f"TEST_KEY_{i}" for i in range(501)]
        data = upstox.get_full_market_quote(too_many_keys)
    except Exception as e:
        print(f"Too many keys error (expected): {e}")

    print("\n=== Market Quotes V3 Example Completed ===")
    print("\nKey Features of V3 APIs:")
    print("- Intraday candle data with custom time intervals")
    print("- Full market quotes for up to 500 instruments")
    print("- OHLC quotes with live and previous candle data")
    print("- LTP quotes for real-time pricing")
    print("- Option Greeks for derivatives analysis")
    print("- Enhanced error handling and validation")
    print("- Standardized response structure")


if __name__ == "__main__":
    main()
