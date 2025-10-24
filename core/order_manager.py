"""Order management system."""

from typing import Dict, List, Optional
from datetime import datetime
from api.backpack import BackpackClient


class Order:
    """Represents a trading order."""

    def __init__(self, order_data: Dict):
        """Initialize order from API response.

        Args:
            order_data: Order data from API
        """
        self.order_id = order_data.get("id")
        self.client_order_id = order_data.get("clientId")
        self.symbol = order_data.get("symbol")
        self.side = order_data.get("side")
        self.order_type = order_data.get("orderType")
        self.price = float(order_data.get("price", 0))
        self.quantity = float(order_data.get("quantity", 0))
        self.filled_quantity = float(order_data.get("executedQuantity", 0))
        self.status = order_data.get("status")
        self.timestamp = order_data.get("timestamp")

    @property
    def remaining_quantity(self) -> float:
        """Get remaining unfilled quantity."""
        return self.quantity - self.filled_quantity

    @property
    def fill_percentage(self) -> float:
        """Get fill percentage."""
        if self.quantity == 0:
            return 0
        return (self.filled_quantity / self.quantity) * 100

    def __repr__(self) -> str:
        """String representation of order."""
        return (f"Order({self.order_id}, {self.symbol}, {self.side}, "
                f"{self.order_type}, {self.quantity}@{self.price}, "
                f"filled: {self.fill_percentage:.1f}%)")


class OrderManager:
    """Manages order placement and tracking."""

    def __init__(self, client: BackpackClient):
        """Initialize order manager.

        Args:
            client: Backpack API client
        """
        self.client = client
        self.open_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Order]:
        """Place a market order.

        Args:
            symbol: Trading pair symbol
            side: "Bid" for buy, "Ask" for sell
            quantity: Order quantity

        Returns:
            Order object if successful, None otherwise
        """
        try:
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type="Market",
                quantity=quantity
            )
            order = Order(response)
            self.open_orders[order.order_id] = order
            return order
        except Exception as e:
            print(f"Error placing market order: {e}")
            return None

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float,
                         time_in_force: str = "GTC") -> Optional[Order]:
        """Place a limit order.

        Args:
            symbol: Trading pair symbol
            side: "Bid" for buy, "Ask" for sell
            quantity: Order quantity
            price: Order price
            time_in_force: Time in force (GTC, IOC, FOK)

        Returns:
            Order object if successful, None otherwise
        """
        try:
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type="Limit",
                quantity=quantity,
                price=price,
                time_in_force=time_in_force
            )
            order = Order(response)
            self.open_orders[order.order_id] = order
            return order
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None

    def buy_market(self, symbol: str, quantity: float) -> Optional[Order]:
        """Convenience method for market buy.

        Args:
            symbol: Trading pair symbol
            quantity: Order quantity

        Returns:
            Order object if successful
        """
        return self.place_market_order(symbol, "Bid", quantity)

    def sell_market(self, symbol: str, quantity: float) -> Optional[Order]:
        """Convenience method for market sell.

        Args:
            symbol: Trading pair symbol
            quantity: Order quantity

        Returns:
            Order object if successful
        """
        return self.place_market_order(symbol, "Ask", quantity)

    def buy_limit(self, symbol: str, quantity: float, price: float) -> Optional[Order]:
        """Convenience method for limit buy.

        Args:
            symbol: Trading pair symbol
            quantity: Order quantity
            price: Order price

        Returns:
            Order object if successful
        """
        return self.place_limit_order(symbol, "Bid", quantity, price)

    def sell_limit(self, symbol: str, quantity: float, price: float) -> Optional[Order]:
        """Convenience method for limit sell.

        Args:
            symbol: Trading pair symbol
            quantity: Order quantity
            price: Order price

        Returns:
            Order object if successful
        """
        return self.place_limit_order(symbol, "Ask", quantity, price)

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel a specific order.

        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.cancel_order(symbol, order_id)
            if order_id in self.open_orders:
                order = self.open_orders.pop(order_id)
                self.order_history.append(order)
            return True
        except Exception as e:
            print(f"Error canceling order: {e}")
            return False

    def cancel_all_orders(self, symbol: str) -> bool:
        """Cancel all open orders for a symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.cancel_all_orders(symbol)
            # Move all open orders to history
            for order_id in list(self.open_orders.keys()):
                if self.open_orders[order_id].symbol == symbol:
                    order = self.open_orders.pop(order_id)
                    self.order_history.append(order)
            return True
        except Exception as e:
            print(f"Error canceling all orders: {e}")
            return False

    def refresh_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Refresh open orders from API.

        Args:
            symbol: Optional symbol to filter

        Returns:
            List of open orders
        """
        try:
            orders_data = self.client.get_open_orders(symbol)
            self.open_orders.clear()
            orders = []
            for order_data in orders_data:
                order = Order(order_data)
                self.open_orders[order.order_id] = order
                orders.append(order)
            return orders
        except Exception as e:
            print(f"Error refreshing orders: {e}")
            return []

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get open orders from local cache.

        Args:
            symbol: Optional symbol to filter

        Returns:
            List of open orders
        """
        if symbol:
            return [o for o in self.open_orders.values() if o.symbol == symbol]
        return list(self.open_orders.values())

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order object if found, None otherwise
        """
        return self.open_orders.get(order_id)

    def place_tiered_orders(self, symbol: str, side: str, total_value: float,
                           price_low: float, price_high: float, num_orders: int) -> List[Optional[Order]]:
        """Place multiple tiered limit orders across a price range.

        Args:
            symbol: Trading pair symbol
            side: "Bid" for buy, "Ask" for sell
            total_value: Total value to trade in quote currency (e.g., USDC)
            price_low: Lower price bound
            price_high: Higher price bound
            num_orders: Number of orders to place

        Returns:
            List of Order objects (None for failed orders)
        """
        if num_orders <= 0:
            print("Number of orders must be greater than 0")
            return []

        if price_low >= price_high:
            print("Lower price must be less than higher price")
            return []

        # Calculate price levels
        if num_orders == 1:
            # Single order at midpoint
            prices = [(price_low + price_high) / 2]
        else:
            # Distribute evenly across range
            price_step = (price_high - price_low) / (num_orders - 1)
            prices = [price_low + (i * price_step) for i in range(num_orders)]

        # Calculate value per order
        value_per_order = total_value / num_orders

        # Place orders
        orders = []
        print(f"\nPlacing {num_orders} tiered {side} orders:")
        print(f"Price range: ${price_low:.4f} - ${price_high:.4f}")
        print(f"Total value: ${total_value:.2f} (${value_per_order:.2f} per order)\n")

        for i, price in enumerate(prices, 1):
            # Calculate quantity for this price level
            quantity = value_per_order / price

            # Note: Precision rounding is handled automatically by the API client
            # based on the market's tick size and step size

            print(f"Order {i}/{num_orders}: {quantity:.4f} @ ${price:.4f} = ${value_per_order:.2f}")

            try:
                order = self.place_limit_order(symbol, side, quantity, price)
                orders.append(order)
                if order:
                    print(f"  ✓ Placed: Order ID {order.order_id}")
                else:
                    print(f"  ✗ Failed to place order")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                orders.append(None)

        successful = sum(1 for o in orders if o is not None)
        print(f"\nPlaced {successful}/{num_orders} orders successfully")

        return orders

    def tiered_buy(self, symbol: str, total_value: float, price_low: float,
                   price_high: float, num_orders: int) -> List[Optional[Order]]:
        """Convenience method for tiered buy orders.

        Args:
            symbol: Trading pair symbol
            total_value: Total value to buy in quote currency
            price_low: Lower price bound
            price_high: Higher price bound
            num_orders: Number of orders to place

        Returns:
            List of Order objects
        """
        return self.place_tiered_orders(symbol, "Bid", total_value, price_low, price_high, num_orders)

    def tiered_sell(self, symbol: str, total_value: float, price_low: float,
                    price_high: float, num_orders: int) -> List[Optional[Order]]:
        """Convenience method for tiered sell orders.

        Args:
            symbol: Trading pair symbol
            total_value: Total value to sell in quote currency
            price_low: Lower price bound
            price_high: Higher price bound
            num_orders: Number of orders to place

        Returns:
            List of Order objects
        """
        return self.place_tiered_orders(symbol, "Ask", total_value, price_low, price_high, num_orders)

    def tiered_sell_by_quantity(self, symbol: str, total_quantity: float, price_low: float,
                                price_high: float, num_orders: int) -> List[Optional[Order]]:
        """Place tiered sell orders by total quantity instead of total value.

        Args:
            symbol: Trading pair symbol
            total_quantity: Total quantity to sell (in base currency, e.g., SOL)
            price_low: Lower price bound
            price_high: Higher price bound
            num_orders: Number of orders to place

        Returns:
            List of Order objects
        """
        if num_orders <= 0:
            print("Number of orders must be greater than 0")
            return []

        if price_low >= price_high:
            print("Lower price must be less than higher price")
            return []

        # Calculate price levels
        if num_orders == 1:
            # Single order at midpoint
            prices = [(price_low + price_high) / 2]
        else:
            # Distribute evenly across range
            price_step = (price_high - price_low) / (num_orders - 1)
            prices = [price_low + (i * price_step) for i in range(num_orders)]

        # Calculate quantity per order
        quantity_per_order = total_quantity / num_orders

        # Place orders
        orders = []
        print(f"\nPlacing {num_orders} tiered sell orders:")
        print(f"Price range: ${price_low:.4f} - ${price_high:.4f}")
        print(f"Total quantity: {total_quantity:.4f} ({quantity_per_order:.4f} per order)\n")

        for i, price in enumerate(prices, 1):
            value_at_price = quantity_per_order * price

            print(f"Order {i}/{num_orders}: {quantity_per_order:.4f} @ ${price:.4f} = ${value_at_price:.2f}")

            try:
                order = self.place_limit_order(symbol, "Ask", quantity_per_order, price)
                orders.append(order)
                if order:
                    print(f"  ✓ Placed: Order ID {order.order_id}")
                else:
                    print(f"  ✗ Failed to place order")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                orders.append(None)

        successful = sum(1 for o in orders if o is not None)
        print(f"\nPlaced {successful}/{num_orders} orders successfully")

        return orders
