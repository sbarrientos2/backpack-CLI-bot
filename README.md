# Ichibot for Backpack Exchange

A Python-based CLI trading bot for Backpack exchange, designed for manual/hybrid trading with keyboard-based execution for maximum speed.

## Features

- **Fast Order Placement**: Keyboard-driven order entry and execution
- **Position Management**: Track and manage open positions in real-time
- **Risk Management**: Built-in stop losses, position sizing, and risk limits
- **Real-time Market Data**: Live price feeds and order book updates
- **Low Latency**: Optimized for fast order execution

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

- `b` - Buy market order
- `s` - Sell market order
- `l` - Limit buy order
- `k` - Limit sell order
- `p` - View positions
- `o` - View open orders
- `c` - Cancel all orders
- `q` - Quit

## Project Structure

```
ichibot/
├── main.py              # Entry point
├── config.py            # Configuration management
├── api/
│   ├── __init__.py
│   └── backpack.py      # Backpack API client
├── core/
│   ├── __init__.py
│   ├── order_manager.py # Order placement and management
│   ├── position_manager.py # Position tracking
│   └── risk_manager.py  # Risk management logic
├── ui/
│   ├── __init__.py
│   └── cli.py           # CLI interface
└── utils/
    ├── __init__.py
    └── helpers.py       # Utility functions
```

## License

MIT
