#!/usr/bin/env python3
"""
Historical Data V3 Example for Upstox Python client.

This example demonstrates the new V3 historical candle data API with custom time intervals.
"""

import logging
from datetime import datetime, timedelta
from upstox import Upstox

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)


def main():
    # Initialize the client
    api_key = "your_api_key_here"
    access_token = "your_access_token_here"

    upstox = Upstox(api_key=api_key, access_token=access_token, debug=True)

    print("=== Upstox Historical Data V3 Example ===\n")

    # Example instrument key (you would get this from get_instruments API)
    instrument_key = "NSE_EQ|INE848E01016"  # Example: Reliance Industries

    # Get current date for to_date
    to_date = datetime.now().strftime("%Y-%m-%d")

    print("1. Getting 1-minute candle data for the last 7 days...")
    try:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_MINUTES,
            interval="1",
            to_date=to_date,
            from_date=from_date,
        )

        print(f"Status: {data.get('status', 'N/A')}")
        candles = data.get("data", {}).get("candles", [])
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
        print(f"Failed to get 1-minute data: {e}\n")

    print("2. Getting 5-minute candle data...")
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_MINUTES,
            interval="5",
            to_date=to_date,
        )

        print(f"Status: {data.get('status', 'N/A')}")
        candles = data.get("data", {}).get("candles", [])
        print(f"Number of candles: {len(candles)}")
        print()

    except Exception as e:
        print(f"Failed to get 5-minute data: {e}\n")

    print("3. Getting 1-hour candle data...")
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_HOURS,
            interval="1",
            to_date=to_date,
        )

        print(f"Status: {data.get('status', 'N/A')}")
        candles = data.get("data", {}).get("candles", [])
        print(f"Number of candles: {len(candles)}")
        print()

    except Exception as e:
        print(f"Failed to get 1-hour data: {e}\n")

    print("4. Getting daily candle data...")
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_DAYS,
            interval="1",
            to_date=to_date,
        )

        print(f"Status: {data.get('status', 'N/A')}")
        candles = data.get("data", {}).get("candles", [])
        print(f"Number of candles: {len(candles)}")

        if candles:
            print("Sample daily data:")
            for i, candle in enumerate(candles[:5]):  # Show first 5 candles
                timestamp, open_price, high, low, close, volume, open_interest = candle
                print(
                    f"  Day {i+1}: {timestamp} - O:{open_price} H:{high} L:{low} C:{close} V:{volume}"
                )
        print()

    except Exception as e:
        print(f"Failed to get daily data: {e}\n")

    print("5. Getting weekly candle data...")
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_WEEKS,
            interval="1",
            to_date=to_date,
        )

        print(f"Status: {data.get('status', 'N/A')}")
        candles = data.get("data", {}).get("candles", [])
        print(f"Number of candles: {len(candles)}")
        print()

    except Exception as e:
        print(f"Failed to get weekly data: {e}\n")

    print("6. Getting monthly candle data...")
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_MONTHS,
            interval="1",
            to_date=to_date,
        )

        print(f"Status: {data.get('status', 'N/A')}")
        candles = data.get("data", {}).get("candles", [])
        print(f"Number of candles: {len(candles)}")

        if candles:
            print("Sample monthly data:")
            for i, candle in enumerate(candles[:3]):  # Show first 3 candles
                timestamp, open_price, high, low, close, volume, open_interest = candle
                print(
                    f"  Month {i+1}: {timestamp} - O:{open_price} H:{high} L:{low} C:{close} V:{volume}"
                )
        print()

    except Exception as e:
        print(f"Failed to get monthly data: {e}\n")

    print("7. Error handling examples...")

    # Test invalid unit
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit="invalid_unit",
            interval="1",
            to_date=to_date,
        )
    except Exception as e:
        print(f"Invalid unit error (expected): {e}")

    # Test invalid interval for minutes
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_MINUTES,
            interval="500",  # Invalid: should be 1-300
            to_date=to_date,
        )
    except Exception as e:
        print(f"Invalid interval error (expected): {e}")

    # Test invalid interval for hours
    try:
        data = upstox.get_historical_candle_data_v3(
            instrument_key=instrument_key,
            unit=upstox.UNIT_HOURS,
            interval="10",  # Invalid: should be 1-5
            to_date=to_date,
        )
    except Exception as e:
        print(f"Invalid hours interval error (expected): {e}")

    print("\n=== Historical Data V3 Example Completed ===")
    print("\nKey Features of V3 API:")
    print("- Custom time intervals for minutes (1-300) and hours (1-5)")
    print("- Granular data control and improved flexibility")
    print("- Consistent response structure with legacy API")
    print("- Efficient handling of large data volumes")
    print("- Historical availability from January 2000 (days/weeks/months)")
    print("- Historical availability from January 2022 (minutes/hours)")
    print("- Uses V3 base URL: https://api.upstox.com/v3")
    print("- Different from V2 APIs which use: https://api.upstox.com/v2")


if __name__ == "__main__":
    main()
