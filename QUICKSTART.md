# Quick Start Guide

Get up and running with Ichibot for Backpack in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd /home/cbas/Programming/ichibot
pip install -r requirements.txt
```

## Step 2: Configure API Keys (2 minutes)

```bash
# Copy example config
cp .env.example .env

# Edit the file and add your Backpack API credentials
nano .env  # or use your preferred editor
```

Add your credentials:
```env
BACKPACK_API_KEY=your_api_key_here
BACKPACK_API_SECRET=your_api_secret_here
```

**Get API keys from:** Backpack Exchange → Account Settings → API Management

## Step 3: Run the Bot (1 minute)

```bash
python main.py
```

## Step 4: Your First Trade (1 minute)

1. The dashboard will appear showing your positions, orders, and balances
2. Press `b` to buy or `s` to sell
3. Enter quantity (e.g., `0.1` for 0.1 SOL)
4. Order executes immediately!

## Essential Commands

- `b` - Buy at market price
- `s` - Sell at market price
- `l` - Place limit buy order (enter as `quantity@price`, e.g., `1@100`)
- `k` - Place limit sell order
- `p` - Refresh positions
- `r` - Refresh all data
- `q` - Quit

## Pro Tips

- **Start small** - Test with tiny amounts first
- **Set limits** - Edit `MAX_POSITION_SIZE` in `.env` to control risk
- **Watch the price** - Check current price in header before trading
- **Use limits** - Limit orders give you price control vs market orders

## Safety First

⚠️ **Important:**
- Never share your API secret
- Start with small amounts
- Use only funds you can afford to lose
- Crypto trading is risky!

## Need Help?

- **Setup issues?** → See [SETUP.md](SETUP.md)
- **Trading help?** → See [TRADING_GUIDE.md](TRADING_GUIDE.md)
- **Full docs?** → See [README.md](README.md)

Happy trading! 🚀
