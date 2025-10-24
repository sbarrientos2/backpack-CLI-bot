"""Utility helper functions."""

from typing import Union


def format_price(price: float, decimals: int = 4) -> str:
    """Format price for display.

    Args:
        price: Price value
        decimals: Number of decimal places

    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"


def format_quantity(quantity: float, decimals: int = 4) -> str:
    """Format quantity for display.

    Args:
        quantity: Quantity value
        decimals: Number of decimal places

    Returns:
        Formatted quantity string
    """
    return f"{quantity:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage for display.

    Args:
        value: Percentage value
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def format_currency(value: float, currency: str = "$", decimals: int = 2) -> str:
    """Format currency value for display.

    Args:
        value: Currency value
        currency: Currency symbol
        decimals: Number of decimal places

    Returns:
        Formatted currency string
    """
    return f"{currency}{value:,.{decimals}f}"


def calculate_position_size(portfolio_value: float, risk_percentage: float,
                           entry_price: float, stop_loss_price: float) -> float:
    """Calculate position size based on risk parameters.

    Args:
        portfolio_value: Total portfolio value
        risk_percentage: Risk percentage (e.g., 1.0 for 1%)
        entry_price: Entry price
        stop_loss_price: Stop loss price

    Returns:
        Position size in base currency
    """
    risk_amount = portfolio_value * (risk_percentage / 100)
    price_risk = abs(entry_price - stop_loss_price)

    if price_risk == 0:
        return 0

    return risk_amount / price_risk


def parse_order_input(input_str: str) -> dict:
    """Parse order input string.

    Format: "quantity@price" or just "quantity"

    Args:
        input_str: Input string

    Returns:
        Dictionary with quantity and optional price
    """
    parts = input_str.strip().split("@")

    try:
        quantity = float(parts[0].strip())
        price = float(parts[1].strip()) if len(parts) > 1 else None

        return {"quantity": quantity, "price": price}
    except (ValueError, IndexError):
        return {"quantity": 0, "price": None}


def calculate_pnl(entry_price: float, exit_price: float, quantity: float, side: str) -> float:
    """Calculate profit/loss.

    Args:
        entry_price: Entry price
        exit_price: Exit price
        quantity: Position quantity
        side: "Bid" for long, "Ask" for short

    Returns:
        PnL value
    """
    if side == "Bid":  # Long
        return (exit_price - entry_price) * quantity
    else:  # Short
        return (entry_price - exit_price) * quantity


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def color_pnl(pnl: float) -> str:
    """Get color code for PnL display.

    Args:
        pnl: PnL value

    Returns:
        Color name for rich library
    """
    if pnl > 0:
        return "green"
    elif pnl < 0:
        return "red"
    return "white"


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format.

    Args:
        symbol: Trading pair symbol

    Returns:
        True if valid, False otherwise
    """
    # Basic validation - should contain underscore
    return "_" in symbol and len(symbol.split("_")) == 2


def split_symbol(symbol: str) -> tuple[str, str]:
    """Split symbol into base and quote assets.

    Args:
        symbol: Trading pair symbol (e.g., "SOL_USDC")

    Returns:
        Tuple of (base_asset, quote_asset)
    """
    parts = symbol.split("_")
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", ""
