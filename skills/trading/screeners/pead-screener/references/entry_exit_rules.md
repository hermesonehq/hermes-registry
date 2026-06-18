# PEAD Entry and Exit Rules

## Entry Rules

### Primary Entry: Red Candle Breakout
- **Trigger**: Weekly candle closes above the red candle's high on a green candle (close >= open)
- **Entry Price**: At or slightly above the red candle high
- **Confirmation**: Volume on the breakout week should be above the 4-week average
- **Timing**: Enter after the weekly close confirms the breakout (end of Friday session)

### Gap Minimum Requirement
- Minimum 3% gap-up on earnings day to qualify as a PEAD candidate
- Larger gaps (5%+) generally indicate stronger earnings surprises and more persistent drift
- Gaps below 3% may represent noise rather than genuine earnings surprise

### Pre-Entry Checklist
1. Earnings gap-up was at least 3%
2. A clear red weekly candle has formed (not a doji or inside bar)
3. Current weekly candle is green with close above red candle high
4. ADV20 (20-day average dollar volume) is at least $25M for adequate liquidity
5. Stock price is above $10 to avoid penny stock volatility
6. Within the 5-week monitoring window from earnings date

## Exit Rules

### Stop-Loss
- **Level**: Below the red candle's low
- **Type**: Hard stop (not mental stop)
- **Rationale**: If price drops below the red candle low, the pullback pattern has failed and institutional support has broken

### Profit Target
- **Primary Target**: 2R (2x the risk from entry to stop)
- **Calculation**: Target = Entry + (Entry - Stop) x 2.0
- **Example**: Entry at $100, Stop at $95 (5% risk) -> Target at $110 (10% gain, 2:1 R:R)

### Trailing Stop (Optional)
- After reaching 1R profit, move stop to breakeven
- After reaching 1.5R profit, trail stop at 1R below current price
- This locks in profits while allowing the PEAD drift to continue

### Time-Based Exit
- If the position has not reached the profit target within 4 weeks of entry, consider closing for a scratch or small profit/loss
- PEAD drift weakens significantly after 6-8 weeks post-earnings

## Position Sizing

### Risk-Based Sizing
- Risk no more than 1-2% of portfolio value per trade
- Position size = (Portfolio x Risk%) / (Entry - Stop)
- Example: $100K portfolio, 1% risk = $1,000 risk budget
  - Entry $100, Stop $95 = $5 risk per share
  - Position = $1,000 / $5 = 200 shares ($20,000 position)

### Liquidity-Based Constraints
- Never take a position larger than 1% of ADV20 (20-day average dollar volume)
- This ensures the position can be exited within a single day without significant market impact
- Example: ADV20 = $50M -> Max position = $500K

### Portfolio-Level Constraints
- Maximum 3-5 PEAD positions simultaneously
- Diversify across sectors to avoid correlated earnings risk
- Reduce position size if multiple PEAD trades are open

## Monitoring Window

### Duration
- Default: 5 weeks from earnings date
- The PEAD effect is strongest in weeks 1-3 and diminishes by weeks 4-5
- After 5 weeks without a breakout signal, remove from monitoring

### Weekly Review Process
1. Check if a red candle has formed (MONITORING -> SIGNAL_READY)
2. Check if breakout has occurred (SIGNAL_READY -> BREAKOUT)
3. Review volume on the breakout candle for confirmation
4. Calculate risk/reward based on current red candle levels
5. Verify liquidity is still adequate for entry

## Special Situations

### Multiple Red Candles
- If multiple red candles form, use the most recent one for entry/stop levels
- Multiple red candles may indicate weakening momentum; reduce position size

### Gap-and-Go (No Red Candle)
- Some stocks gap up and never pull back meaningfully
- These are not PEAD screener candidates (require red candle for defined risk)
- Consider alternative entry strategies if conviction is high

### Earnings in Consecutive Quarters
- A stock that gaps up on earnings for 2+ consecutive quarters shows persistent fundamental strength
- These are higher-conviction PEAD candidates when they form the red candle pattern
