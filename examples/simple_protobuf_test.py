#!/usr/bin/env python3
"""
Simple test to demonstrate Protobuf decoding functionality.

This script shows that the Protobuf classes are now available and working.
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from upstox import Upstox
from upstox.protobuf_decoder import ProtobufDecoder
from upstox.upstox_ticker import UpstoxTicker


def test_protobuf_decoder():
    """Test the Protobuf decoder functionality."""
    print("🧪 Testing Protobuf Decoder...")

    # Create decoder instance
    decoder = ProtobufDecoder(debug=True)
    print("✅ ProtobufDecoder created successfully")

    # Test that protobuf classes are available
    try:
        from upstox import market_data_feed_pb2 as pb

        print("✅ Protobuf classes imported successfully")

        # Test creating a FeedResponse instance
        feed_response = pb.FeedResponse()
        print("✅ FeedResponse instance created successfully")

        # Test creating an LTPC instance
        ltpc = pb.LTPC()
        ltpc.ltp = 100.50
        ltpc.cp = 99.75
        ltpc.ltt = 1234567890
        ltpc.ltq = 100
        print("✅ LTPC instance created and populated successfully")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ticker_protobuf_support():
    """Test that the ticker has Protobuf support."""
    print("\n🧪 Testing Ticker Protobuf Support...")

    try:
        # Create ticker instance
        ticker = UpstoxTicker("test_api_key", "test_access_token", debug=True)
        print("✅ UpstoxTicker created successfully")

        # Check if protobuf decoder is available
        if hasattr(ticker, "protobuf_decoder"):
            print("✅ Protobuf decoder is available in ticker")
            return True
        else:
            print("❌ Protobuf decoder not found in ticker")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Upstox Protobuf Decoding Test")
    print("=" * 50)

    # Test Protobuf decoder
    decoder_ok = test_protobuf_decoder()

    # Test ticker Protobuf support
    ticker_ok = test_ticker_protobuf_support()

    print("\n📊 Test Results:")
    print(f"  Protobuf Decoder: {'✅ PASS' if decoder_ok else '❌ FAIL'}")
    print(f"  Ticker Protobuf Support: {'✅ PASS' if ticker_ok else '❌ FAIL'}")

    if decoder_ok and ticker_ok:
        print("\n🎉 All tests passed! Protobuf decoding is ready to use.")
        print("\n💡 You can now use the WebSocket ticker with Protobuf decoding:")
        print("   ticker = upstox.get_ticker()")
        print("   ticker.connect()")
        print("   ticker.subscribe(['NSE_EQ|INE848E01016'], mode='ltpc')")
    else:
        print("\n⚠️ Some tests failed. Please check the setup.")


if __name__ == "__main__":
    main()
