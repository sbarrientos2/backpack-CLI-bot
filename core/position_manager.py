"""Position tracking and management."""

from typing import Dict, List, Optional
from datetime import datetime
from api.backpack import BackpackClient


class Position:
    """Represents a trading position."""

    def __init__(self, position_data: Dict):
        """Initialize position from API response.

        Args:
            position_data: Position data from API
        """
        self.symbol = position_data.get("symbol")
        self.side = position_data.get("side", "Long")  # Long or Short
        self.quantity = float(position_data.get("quantity", 0))
        self.entry_price = float(position_data.get("entryPrice", 0))
        self.mark_price = float(position_data.get("markPrice", 0))
        self.liquidation_price = float(position_data.get("liquidationPrice", 0))
        self.unrealized_pnl = float(position_data.get("unrealizedPnl", 0))
        self.realized_pnl = float(position_data.get("realizedPnl", 0))
        self.leverage = float(position_data.get("leverage", 1))
        self.margin = float(position_data.get("margin", 0))

    @property
    def notional_value(self) -> float:
        """Get notional value of position."""
        return self.quantity * self.mark_price

    @property
    def pnl_percentage(self) -> float:
        """Get PnL as percentage of entry."""
        if self.entry_price == 0:
            return 0

        if self.side == "Long":
            return ((self.mark_price - self.entry_price) / self.entry_price) * 100
        else:  # Short
            return ((self.entry_price - self.mark_price) / self.entry_price) * 100

    @property
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.side == "Long" and self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.side == "Short" and self.quantity > 0

    def update_mark_price(self, mark_price: float):
        """Update mark price and recalculate PnL.

        Args:
            mark_price: New mark price
        """
        self.mark_price = mark_price
        if self.side == "Long":
            self.unrealized_pnl = (mark_price - self.entry_price) * self.quantity
        else:  # Short
            self.unrealized_pnl = (self.entry_price - mark_price) * self.quantity

    def __repr__(self) -> str:
        """String representation of position."""
        return (f"Position({self.symbol}, {self.side}, qty={self.quantity:.4f}, "
                f"entry={self.entry_price:.4f}, mark={self.mark_price:.4f}, "
                f"pnl={self.unrealized_pnl:.2f} ({self.pnl_percentage:.2f}%))")


class PositionManager:
    """Manages trading positions."""

    def __init__(self, client: BackpackClient):
        """Initialize position manager.

        Args:
            client: Backpack API client
        """
        self.client = client
        self.positions: Dict[str, Position] = {}
        self.balances: Dict[str, float] = {}

    def refresh_positions(self) -> List[Position]:
        """Refresh positions from API.

        Returns:
            List of current positions
        """
        try:
            positions_data = self.client.get_positions()
            self.positions.clear()

            positions = []
            for pos_data in positions_data:
                position = Position(pos_data)
                if position.quantity > 0:  # Only track non-zero positions
                    self.positions[position.symbol] = position
                    positions.append(position)

            return positions
        except Exception as e:
            # Suppress 404 errors for positions (may not be available for spot-only accounts)
            if "404" not in str(e):
                print(f"Error refreshing positions: {e}")
            return []

    def refresh_balances(self):
        """Refresh account balances from API."""
        try:
            account_data = self.client.get_account()
            self.balances.clear()

            # Parse balance data based on Backpack API response
            # The API returns an object where keys are asset symbols
            # Format: { "BTC": { "available": "1.5", "locked": "0.25", "staked": "0" }, ... }
            for asset, balance_data in account_data.items():
                if isinstance(balance_data, dict):  # Ensure it's a balance object
                    free = float(balance_data.get("available", 0))
                    locked = float(balance_data.get("locked", 0))
                    self.balances[asset] = {
                        "free": free,
                        "locked": locked,
                        "total": free + locked
                    }
        except Exception as e:
            print(f"Error refreshing balances: {e}")

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            Position object if exists, None otherwise
        """
        return self.positions.get(symbol)

    def get_all_positions(self) -> List[Position]:
        """Get all positions.

        Returns:
            List of all positions
        """
        return list(self.positions.values())

    def get_balance(self, asset: str) -> Dict[str, float]:
        """Get balance for an asset.

        Args:
            asset: Asset symbol (e.g., "USDC", "SOL")

        Returns:
            Balance dictionary with free, locked, and total amounts
        """
        return self.balances.get(asset, {"free": 0, "locked": 0, "total": 0})

    def get_total_pnl(self) -> float:
        """Get total unrealized PnL across all positions.

        Returns:
            Total unrealized PnL
        """
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    def get_total_margin(self) -> float:
        """Get total margin used across all positions.

        Returns:
            Total margin used
        """
        return sum(pos.margin for pos in self.positions.values())

    def get_portfolio_value(self, quote_asset: str = "USDC") -> float:
        """Get total portfolio value.

        Args:
            quote_asset: Quote asset to calculate value in

        Returns:
            Total portfolio value
        """
        quote_balance = self.get_balance(quote_asset)
        total = quote_balance.get("total", 0)

        # Add unrealized PnL from positions
        total += self.get_total_pnl()

        return total

    def has_position(self, symbol: str) -> bool:
        """Check if there's an active position for a symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            True if position exists, False otherwise
        """
        return symbol in self.positions and self.positions[symbol].quantity > 0

    def update_position_price(self, symbol: str, mark_price: float):
        """Update mark price for a position.

        Args:
            symbol: Trading pair symbol
            mark_price: New mark price
        """
        if symbol in self.positions:
            self.positions[symbol].update_mark_price(mark_price)

    def get_position_summary(self) -> Dict:
        """Get summary of all positions.

        Returns:
            Dictionary with position statistics
        """
        num_positions = len(self.positions)
        num_long = sum(1 for pos in self.positions.values() if pos.is_long)
        num_short = sum(1 for pos in self.positions.values() if pos.is_short)
        total_pnl = self.get_total_pnl()
        total_margin = self.get_total_margin()

        winning_positions = sum(1 for pos in self.positions.values() if pos.unrealized_pnl > 0)
        losing_positions = sum(1 for pos in self.positions.values() if pos.unrealized_pnl < 0)

        return {
            "total_positions": num_positions,
            "long_positions": num_long,
            "short_positions": num_short,
            "total_pnl": total_pnl,
            "total_margin": total_margin,
            "winning_positions": winning_positions,
            "losing_positions": losing_positions,
            "portfolio_value": self.get_portfolio_value()
        }
