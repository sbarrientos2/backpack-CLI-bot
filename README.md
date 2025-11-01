# Backpack Spot Trading Bot

A Python-based CLI trading bot for Backpack Exchange, focused on **spot trading** with keyboard-driven order execution for maximum speed.

## Features

- **Fast Order Placement**: Keyboard-driven market and limit orders
- **Tiered Orders**: Place multiple orders across a price range
- **Order Management**: View and cancel open orders
- **Real-time Updates**: Auto-refresh every 10 seconds
- **Balance Tracking**: Monitor available, locked, and staked balances
- **Clean Interface**: Minimalist terminal UI for distraction-free trading

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and add your Backpack API credentials:

```
BACKPACK_API_KEY=your_api_key
BACKPACK_API_SECRET=your_api_secret
```

## Usage

```bash
python main.py
```

## Keyboard Shortcuts

**Order Placement:**
- `b` - Buy market order
- `s` - Sell market order
- `l` - Limit buy order
- `k` - Limit sell order
- `tb` - Tiered buy (multiple orders across price range)
- `ts` - Tiered sell (multiple orders across price range)

**Order Management:**
- `o` - Refresh open orders
- `c` - Cancel all orders for current symbol
- `cr` - Cancel orders in price range

**General:**
- `sym` - Change trading symbol
- `r` - Refresh all data
- `h` - Show help
- `q` - Quit

## Project Structure

```
backpack-cli-bot/
├── main.py              # Entry point
├── config.py            # Configuration management
├── SECURITY.md          # Security best practices
├── api/
│   ├── __init__.py
│   └── backpack.py      # Backpack API client
├── core/
│   ├── __init__.py
│   └── order_manager.py # Order placement and management
├── ui/
│   ├── __init__.py
│   └── cli.py           # CLI interface (Spot trading only)
└── utils/
    ├── __init__.py
    └── helpers.py       # Utility functions
```

## Important Notes

- **Spot Trading Only**: This bot is designed for spot trading. It does not support perpetual futures.
- **Security**: Read [SECURITY.md](SECURITY.md) for API key security best practices
- **Auto-Refresh**: Data refreshes automatically every 10 seconds
- **Portfolio**: Shows total USDC/USDT balance (available + locked + staked)

## License

MIT
