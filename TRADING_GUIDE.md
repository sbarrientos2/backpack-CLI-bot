# Trading Guide

## Understanding the Interface

### Dashboard Layout

The main dashboard shows:

1. **Header** - Current symbol, price, portfolio value, and total PnL
2. **Positions** - Active trading positions with entry price, current price, and PnL
3. **Open Orders** - Pending limit orders
4. **Balances** - Available funds by asset
5. **Help** - Keyboard shortcuts reference

### Keyboard Commands

| Key | Action | Description |
|-----|--------|-------------|
| `b` | Buy Market | Execute instant buy at market price |
| `s` | Sell Market | Execute instant sell at market price |
| `l` | Limit Buy | Place limit buy order |
| `k` | Limit Sell | Place limit sell order |
| `p` | Refresh Positions | Update position data from exchange |
| `o` | Refresh Orders | Update order data from exchange |
| `c` | Cancel All | Cancel all open orders for current symbol |
| `sym` | Change Symbol | Switch to different trading pair |
| `r` | Refresh All | Refresh all data |
| `h` | Help | Show keyboard shortcuts |
| `q` | Quit | Exit the application |

## Placing Orders

### Market Orders

Market orders execute immediately at the best available price.

**To place a market buy:**
1. Press `b`
2. Enter quantity (e.g., `10`)
3. Order executes immediately

**To place a market sell:**
1. Press `s`
2. Enter quantity (e.g., `10`)
3. Order executes immediately

**Use market orders when:**
- You need immediate execution
- You're trading liquid markets
- Price slippage is acceptable

### Limit Orders

Limit orders execute only at your specified price or better.

**To place a limit buy:**
1. Press `l`
2. Enter quantity@price (e.g., `10@100.5`)
3. Order waits in order book until filled

**To place a limit sell:**
1. Press `k`
2. Enter quantity@price (e.g., `10@105.5`)
3. Order waits in order book until filled

**Use limit orders when:**
- You want price control
- You're patient for fills
- You want to avoid slippage

## Risk Management

The bot includes built-in risk management:

### Position Sizing

The bot will reject orders that:
- Exceed maximum position size (set in config)
- Exceed portfolio risk percentage
- Would over-leverage your account

### Risk Parameters

Configure in `.env`:

```env
MAX_POSITION_SIZE=1000    # Max $1000 per position
RISK_PERCENTAGE=1.0       # Risk 1% of portfolio per trade
```

### Stop Losses

While the bot doesn't automatically place stop losses, you should:

1. Calculate stop loss price before entering
2. Set mental stop loss
3. Manually close position if hit
4. Or place stop-limit orders separately

**Example:**
- Entry: $100
- Stop loss: $98 (2% risk)
- Position size: Based on risk tolerance

## Position Management

### Monitoring Positions

- Positions table shows real-time PnL
- Green = profitable, Red = losing
- Entry price vs current mark price
- Percentage gain/loss

### Closing Positions

To close a position:
1. Use market sell (for long) or market buy (for short)
2. Enter quantity equal to your position size
3. Position closes and PnL realizes

### Partial Closes

You can close portions of positions:
- Close 50% by selling half your quantity
- Scale out at different price levels
- Take profits while maintaining exposure

## Trading Strategies

### Scalping

- Use market orders for speed
- Small positions, quick profits
- Watch for tight spreads
- Exit quickly

### Swing Trading

- Use limit orders for better fills
- Hold positions hours to days
- Set wider stops
- Less frequent trading

### Position Trading

- Longer-term holds
- Focus on fundamentals
- Larger positions
- Wider risk parameters

## Best Practices

### Before Trading

1. **Check balances** - Ensure sufficient funds
2. **Verify symbol** - Confirm correct trading pair
3. **Check price** - Ensure reasonable current price
4. **Calculate risk** - Know your stop loss and position size

### During Trading

1. **Start small** - Test with minimal size first
2. **Monitor positions** - Regularly refresh data
3. **Stay disciplined** - Follow your trading plan
4. **Take breaks** - Avoid overtrading

### After Trading

1. **Review trades** - Learn from winners and losers
2. **Track performance** - Monitor PnL over time
3. **Adjust limits** - Modify risk parameters as needed
4. **Secure profits** - Withdraw or rebalance periodically

## Common Mistakes to Avoid

1. **Overleveraging** - Using too much margin
2. **Revenge trading** - Trying to recover losses quickly
3. **FOMO** - Chasing pumps
4. **Ignoring risk** - Not using stop losses
5. **Overtrading** - Too many trades, high fees

## Risk Warnings

- **Crypto is volatile** - Prices can move quickly
- **Use only risk capital** - Money you can afford to lose
- **Start small** - Test thoroughly before scaling up
- **API security** - Protect your API keys
- **Exchange risk** - Exchanges can fail or be hacked
- **No guarantees** - Past performance ≠ future results

## Getting Help

If you experience issues:

1. Check the logs for error messages
2. Verify API credentials
3. Ensure exchange is operational
4. Review this guide and README
5. Report bugs on GitHub

Happy trading! 📈
