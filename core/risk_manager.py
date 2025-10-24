"""Risk management system."""

from typing import Optional, Dict
from config import config


class RiskManager:
    """Manages trading risk and position sizing."""

    def __init__(self, max_position_size: float = None, risk_percentage: float = None):
        """Initialize risk manager.

        Args:
            max_position_size: Maximum position size in quote currency
            risk_percentage: Maximum risk per trade as percentage of portfolio
        """
        self.max_position_size = max_position_size or config.MAX_POSITION_SIZE
        self.risk_percentage = risk_percentage or config.RISK_PERCENTAGE
        self.max_leverage = 5  # Maximum allowed leverage
        self.max_portfolio_risk = 10.0  # Maximum total portfolio risk percentage

    def calculate_position_size(self, portfolio_value: float, entry_price: float,
                               stop_loss_price: Optional[float] = None,
                               risk_amount: Optional[float] = None) -> float:
        """Calculate position size based on risk parameters.

        Args:
            portfolio_value: Total portfolio value
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price (optional)
            risk_amount: Fixed risk amount (optional, overrides risk_percentage)

        Returns:
            Recommended position size in base currency
        """
        # Calculate risk amount
        if risk_amount is None:
            risk_amount = portfolio_value * (self.risk_percentage / 100)

        # If stop loss is provided, use it to calculate position size
        if stop_loss_price and stop_loss_price > 0:
            price_risk = abs(entry_price - stop_loss_price)
            if price_risk > 0:
                position_size = risk_amount / price_risk
            else:
                position_size = 0
        else:
            # Without stop loss, use a conservative default (e.g., 2% price risk)
            default_price_risk = entry_price * 0.02
            position_size = risk_amount / default_price_risk

        # Apply maximum position size limit
        max_quantity = self.max_position_size / entry_price
        position_size = min(position_size, max_quantity)

        return position_size

    def validate_order(self, symbol: str, side: str, quantity: float, price: float,
                      current_positions: Dict, portfolio_value: float) -> tuple[bool, str]:
        """Validate an order against risk parameters.

        Args:
            symbol: Trading pair symbol
            side: Order side ("Bid" or "Ask")
            quantity: Order quantity
            price: Order price
            current_positions: Dictionary of current positions
            portfolio_value: Total portfolio value

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Calculate order value
        order_value = quantity * price

        # Check if order exceeds max position size
        if order_value > self.max_position_size:
            return False, f"Order value ${order_value:.2f} exceeds max position size ${self.max_position_size:.2f}"

        # Check if order exceeds portfolio risk (skip if portfolio value is zero)
        if portfolio_value > 0:
            portfolio_risk_pct = (order_value / portfolio_value) * 100
            # Allow up to 50% of portfolio per order (reasonable for manual trading)
            if portfolio_risk_pct > 50:
                return False, f"Order represents {portfolio_risk_pct:.1f}% of portfolio, exceeds 50% limit"

            # Check total portfolio exposure
            total_exposure = order_value
            for pos in current_positions.values():
                total_exposure += abs(pos.notional_value)

            total_exposure_pct = (total_exposure / portfolio_value) * 100
            # Allow up to 200% total exposure (reasonable with leverage)
            if total_exposure_pct > 200:
                return False, f"Total portfolio exposure {total_exposure_pct:.1f}% exceeds 200% limit"

        # Check leverage (for margin/futures trading)
        if hasattr(current_positions.get(symbol), 'leverage'):
            position = current_positions.get(symbol)
            if position and position.leverage > self.max_leverage:
                return False, f"Position leverage {position.leverage}x exceeds max {self.max_leverage}x"

        return True, "OK"

    def calculate_stop_loss(self, entry_price: float, side: str,
                           risk_percentage: Optional[float] = None) -> float:
        """Calculate stop loss price based on risk percentage.

        Args:
            entry_price: Entry price
            side: "Bid" for long, "Ask" for short
            risk_percentage: Risk percentage (default uses self.risk_percentage)

        Returns:
            Stop loss price
        """
        risk_pct = risk_percentage or self.risk_percentage

        if side == "Bid":  # Long position
            stop_loss = entry_price * (1 - risk_pct / 100)
        else:  # Short position
            stop_loss = entry_price * (1 + risk_pct / 100)

        return stop_loss

    def calculate_take_profit(self, entry_price: float, side: str,
                             risk_reward_ratio: float = 2.0) -> float:
        """Calculate take profit price based on risk-reward ratio.

        Args:
            entry_price: Entry price
            side: "Bid" for long, "Ask" for short
            risk_reward_ratio: Risk-reward ratio (default 2:1)

        Returns:
            Take profit price
        """
        stop_loss = self.calculate_stop_loss(entry_price, side)
        risk_amount = abs(entry_price - stop_loss)

        if side == "Bid":  # Long position
            take_profit = entry_price + (risk_amount * risk_reward_ratio)
        else:  # Short position
            take_profit = entry_price - (risk_amount * risk_reward_ratio)

        return take_profit

    def check_position_risk(self, position, portfolio_value: float) -> Dict:
        """Check risk metrics for a position.

        Args:
            position: Position object
            portfolio_value: Total portfolio value

        Returns:
            Dictionary with risk metrics
        """
        position_size_pct = (position.notional_value / portfolio_value) * 100
        pnl_pct = position.pnl_percentage

        # Calculate distance to liquidation (if applicable)
        liquidation_distance = None
        if position.liquidation_price > 0:
            if position.is_long:
                liquidation_distance = ((position.mark_price - position.liquidation_price) /
                                      position.mark_price) * 100
            else:
                liquidation_distance = ((position.liquidation_price - position.mark_price) /
                                      position.mark_price) * 100

        return {
            "symbol": position.symbol,
            "size_percentage": position_size_pct,
            "pnl_percentage": pnl_pct,
            "liquidation_distance": liquidation_distance,
            "is_high_risk": position_size_pct > self.risk_percentage * 3,
            "needs_attention": liquidation_distance is not None and liquidation_distance < 10
        }

    def get_max_quantity(self, price: float, portfolio_value: Optional[float] = None) -> float:
        """Get maximum allowed quantity for a given price.

        Args:
            price: Price per unit
            portfolio_value: Total portfolio value (optional)

        Returns:
            Maximum quantity
        """
        if price <= 0:
            return 0

        # Based on max position size
        max_qty_by_size = self.max_position_size / price

        # Based on portfolio risk (if portfolio value provided)
        if portfolio_value:
            risk_amount = portfolio_value * (self.risk_percentage / 100)
            max_qty_by_risk = risk_amount / (price * 0.02)  # Assume 2% stop loss
            return min(max_qty_by_size, max_qty_by_risk)

        return max_qty_by_size

    def should_close_position(self, position, stop_loss: Optional[float] = None,
                            take_profit: Optional[float] = None) -> tuple[bool, str]:
        """Check if a position should be closed based on stop loss or take profit.

        Args:
            position: Position object
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Tuple of (should_close, reason)
        """
        mark_price = position.mark_price

        # Check stop loss
        if stop_loss:
            if position.is_long and mark_price <= stop_loss:
                return True, f"Stop loss hit at {mark_price}"
            elif position.is_short and mark_price >= stop_loss:
                return True, f"Stop loss hit at {mark_price}"

        # Check take profit
        if take_profit:
            if position.is_long and mark_price >= take_profit:
                return True, f"Take profit hit at {mark_price}"
            elif position.is_short and mark_price <= take_profit:
                return True, f"Take profit hit at {mark_price}"

        # Check if close to liquidation
        if hasattr(position, 'liquidation_price') and position.liquidation_price > 0:
            if position.is_long:
                distance = ((mark_price - position.liquidation_price) / mark_price) * 100
                if distance < 5:  # Less than 5% from liquidation
                    return True, f"Close to liquidation (distance: {distance:.2f}%)"
            else:
                distance = ((position.liquidation_price - mark_price) / mark_price) * 100
                if distance < 5:
                    return True, f"Close to liquidation (distance: {distance:.2f}%)"

        return False, ""
