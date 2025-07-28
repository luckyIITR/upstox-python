#!/usr/bin/env python3
"""
Order management example for Upstox Python client.

This example demonstrates:
1. Placing different types of orders
2. Getting order history
3. Modifying orders
4. Canceling orders
5. Error handling
"""

import logging
from upstox import Upstox
from upstox.exceptions import OrderException, TokenException

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)


def main():
    # Initialize the client
    api_key = "your_api_key_here"
    access_token = "your_access_token_here"

    upstox = Upstox(api_key=api_key, access_token=access_token, debug=True)

    print("=== Upstox Order Management Example ===\n")

    # Example 1: Place a market order
    print("1. Placing a market order...")
    try:
        order_id = upstox.place_order(
            symbol="RELIANCE-EQ",
            quantity=1,
            side=upstox.TRANSACTION_TYPE_BUY,
            order_type=upstox.ORDER_TYPE_MARKET,
            product=upstox.PRODUCT_CNC,
            tag="example_market_order",
        )
        print(f"Market order placed successfully! Order ID: {order_id}")

        # Store order ID for later use
        market_order_id = order_id

    except OrderException as e:
        print(f"Order placement failed: {e}")
        market_order_id = None
    except TokenException as e:
        print(f"Authentication error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        market_order_id = None

    print()

    # Example 2: Place a limit order
    print("2. Placing a limit order...")
    try:
        order_id = upstox.place_order(
            symbol="TCS-EQ",
            quantity=5,
            side=upstox.TRANSACTION_TYPE_BUY,
            order_type=upstox.ORDER_TYPE_LIMIT,
            price=3500.0,  # Limit price
            product=upstox.PRODUCT_CNC,
            validity=upstox.VALIDITY_DAY,
            tag="example_limit_order",
        )
        print(f"Limit order placed successfully! Order ID: {order_id}")

        # Store order ID for modification
        limit_order_id = order_id

    except OrderException as e:
        print(f"Order placement failed: {e}")
        limit_order_id = None
    except Exception as e:
        print(f"Unexpected error: {e}")
        limit_order_id = None

    print()

    # Example 3: Place a stop loss order
    print("3. Placing a stop loss order...")
    try:
        order_id = upstox.place_order(
            symbol="INFY-EQ",
            quantity=10,
            side=upstox.TRANSACTION_TYPE_SELL,
            order_type=upstox.ORDER_TYPE_STOP_LOSS,
            trigger_price=1500.0,  # Trigger price
            price=1495.0,  # Stop loss price
            product=upstox.PRODUCT_MIS,
            tag="example_stop_loss",
        )
        print(f"Stop loss order placed successfully! Order ID: {order_id}")

    except OrderException as e:
        print(f"Order placement failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print()

    # Example 4: Get order history
    print("4. Getting order history...")
    try:
        orders = upstox.get_orders()
        print(f"Total orders: {len(orders)}")

        # Show recent orders
        for order in orders[:5]:
            order_id = order.get("order_id", "N/A")
            symbol = order.get("tradingsymbol", "N/A")
            side = order.get("side", "N/A")
            quantity = order.get("quantity", 0)
            status = order.get("status", "N/A")
            print(f"  {order_id}: {symbol} {side} {quantity} - {status}")

    except Exception as e:
        print(f"Failed to get orders: {e}")

    print()

    # Example 5: Modify an order (if we have a limit order)
    if limit_order_id:
        print("5. Modifying limit order...")
        try:
            # Modify the limit order
            result = upstox.modify_order(
                order_id=limit_order_id,
                quantity=10,  # Increase quantity
                price=3450.0,  # Lower the price
            )
            print(f"Order modified successfully!")
            print(f"Modified order details: {result}")

        except OrderException as e:
            print(f"Order modification failed: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    print()

    # Example 6: Cancel an order (if we have a market order)
    if market_order_id:
        print("6. Canceling market order...")
        try:
            result = upstox.cancel_order(market_order_id)
            print(f"Order canceled successfully!")
            print(f"Cancel response: {result}")

        except OrderException as e:
            print(f"Order cancellation failed: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    print()

    # Example 7: Get specific order details
    if limit_order_id:
        print("7. Getting specific order details...")
        try:
            order_details = upstox.get_orders(order_id=limit_order_id)
            print(f"Order details: {order_details}")

        except Exception as e:
            print(f"Failed to get order details: {e}")

    print()

    # Example 8: Place mutual fund order
    print("8. Placing mutual fund order...")
    try:
        mf_order_id = upstox.place_mf_order(
            symbol="INF090I01239",  # Example mutual fund symbol
            amount=5000.0,  # Amount in rupees
            side=upstox.TRANSACTION_TYPE_BUY,
            tag="example_mf_order",
        )
        print(f"Mutual fund order placed successfully! Order ID: {mf_order_id}")

    except OrderException as e:
        print(f"Mutual fund order placement failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print()

    # Example 9: Place GTT (Good Till Triggered) order
    print("9. Placing GTT order...")
    try:
        gtt_id = upstox.place_gtt(
            symbol="RELIANCE-EQ",
            quantity=5,
            side=upstox.TRANSACTION_TYPE_SELL,
            trigger_price=2600.0,
            order_type=upstox.ORDER_TYPE_LIMIT,
            price=2595.0,
            validity=30,  # 30 days
        )
        print(f"GTT order placed successfully! GTT ID: {gtt_id}")

    except OrderException as e:
        print(f"GTT order placement failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print()

    # Example 10: Get GTT orders
    print("10. Getting GTT orders...")
    try:
        gtt_orders = upstox.get_gtt_orders()
        print(f"Total GTT orders: {len(gtt_orders)}")

        for gtt in gtt_orders[:3]:
            gtt_id = gtt.get("id", "N/A")
            symbol = gtt.get("tradingsymbol", "N/A")
            trigger_price = gtt.get("trigger_price", "N/A")
            status = gtt.get("status", "N/A")
            print(f"  {gtt_id}: {symbol} @ ₹{trigger_price} - {status}")

    except Exception as e:
        print(f"Failed to get GTT orders: {e}")

    print("\n=== Order Management Example Completed ===")


if __name__ == "__main__":
    main()
