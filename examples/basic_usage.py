#!/usr/bin/env python3
"""
Basic usage example for Upstox Python client.

This example demonstrates:
1. Authentication flow
2. Getting user profile
3. Getting holdings
4. Getting market quotes
5. Placing orders
"""

import logging
from upstox import Upstox

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)


def main():
    # Initialize the client
    api_key = "your_api_key_here"
    upstox = Upstox(api_key=api_key, debug=True)

    print("=== Upstox Python Client - Basic Usage Example ===\n")

    # Step 1: Get login URL
    print("1. Getting login URL...")
    login_url = upstox.get_login_url(
        redirect_uri="https://your-redirect-uri.com/callback"
    )
    print(f"Login URL: {login_url}")
    print("Please visit this URL to authenticate and get the authorization code.\n")

    # Step 2: Generate session (you would do this after getting the auth code)
    print("2. Generating session...")
    try:
        # Replace with actual authorization code from login
        authorization_code = "your_authorization_code_here"
        api_secret = "your_api_secret_here"
        redirect_uri = "https://your-redirect-uri.com/callback"  # Must match the one used in get_login_url

        session_data = upstox.generate_session(
            authorization_code, api_secret, redirect_uri
        )
        print(f"Session generated successfully!")
        print(f"Access Token: {session_data['access_token'][:20]}...")
        print(f"Refresh Token: {session_data.get('refresh_token', 'N/A')[:20]}...")
        print()

    except Exception as e:
        print(f"Failed to generate session: {e}")
        print(
            "Please make sure you have valid authorization code, API secret, and redirect URI.\n"
        )
        return

    # Step 3: Get user profile
    print("3. Getting user profile...")
    try:
        profile = upstox.get_profile()
        print(f"User Name: {profile.get('name', 'N/A')}")
        print(f"Email: {profile.get('email', 'N/A')}")
        print(f"Mobile: {profile.get('mobile', 'N/A')}")
        print()

    except Exception as e:
        print(f"Failed to get profile: {e}\n")

    # Step 4: Get holdings
    print("4. Getting holdings...")
    try:
        holdings = upstox.get_holdings()
        print(f"Total holdings: {len(holdings)}")

        for holding in holdings[:3]:  # Show first 3 holdings
            symbol = holding.get("tradingsymbol", "N/A")
            quantity = holding.get("quantity", 0)
            avg_price = holding.get("average_price", 0)
            print(f"  {symbol}: {quantity} shares @ ₹{avg_price}")
        print()

    except Exception as e:
        print(f"Failed to get holdings: {e}\n")

    # Step 5: Get market quote
    print("5. Getting market quote...")
    try:
        quote = upstox.get_quote("RELIANCE-EQ")
        print(f"Symbol: {quote.get('symbol', 'N/A')}")
        print(f"LTP: ₹{quote.get('ltp', 'N/A')}")
        print(f"Change: {quote.get('change', 'N/A')}")
        print(f"Change %: {quote.get('change_percent', 'N/A')}%")
        print()

    except Exception as e:
        print(f"Failed to get quote: {e}\n")

    # Step 6: Get trading charges
    print("6. Getting trading charges...")
    try:
        charges = upstox.get_charges(
            symbol="RELIANCE-EQ", quantity=100, price=2500.0, product=upstox.PRODUCT_CNC
        )
        print(f"Brokerage: ₹{charges.get('brokerage', 'N/A')}")
        print(f"STT: ₹{charges.get('stt', 'N/A')}")
        print(
            f"Exchange Transaction Charges: ₹{charges.get('exchange_transaction_charges', 'N/A')}"
        )
        print(f"GST: ₹{charges.get('gst', 'N/A')}")
        print(f"SEBI Charges: ₹{charges.get('sebi_charges', 'N/A')}")
        print(f"Total Charges: ₹{charges.get('total_charges', 'N/A')}")
        print()

    except Exception as e:
        print(f"Failed to get charges: {e}\n")

    # Step 7: Extended Token Example (commented out for safety)
    print("7. Extended token example (commented out for safety)...")
    print(
        """
    # Example extended token generation (uncomment to test):
    try:
        extended_session_data = upstox.generate_extended_token(
            authorization_code="your_authorization_code_here",
            api_secret="your_api_secret_here",
            redirect_uri="https://your-redirect-uri.com/callback"
        )
        print(f"Extended token generated successfully!")
        print(f"Extended Token: {extended_session_data['extended_token'][:20]}...")
        print("Note: Extended tokens are valid for 1 year and for read-only operations")
    except Exception as e:
        print(f"Extended token generation failed: {e}")
    """
    )

    # Step 8: Place order (commented out for safety)
    print("8. Order placement example (commented out for safety)...")
    print(
        """
    # Example order placement (uncomment to test):
    try:
        order_id = upstox.place_order(
            symbol="RELIANCE-EQ",
            quantity=1,
            side=upstox.TRANSACTION_TYPE_BUY,
            order_type=upstox.ORDER_TYPE_MARKET,
            product=upstox.PRODUCT_CNC
        )
        print(f"Order placed successfully! Order ID: {order_id}")
    except Exception as e:
        print(f"Order placement failed: {e}")
    """
    )

    print("=== Example completed ===")


if __name__ == "__main__":
    main()
