# PEAD Strategy - Post-Earnings Announcement Drift

## What is PEAD

Post-Earnings Announcement Drift (PEAD) is one of the most robust anomalies in financial markets. Stocks that report positive earnings surprises (and gap up on the announcement) tend to continue drifting higher over the following weeks and months. This drift represents a systematic underreaction by the market to new earnings information.

## Academic Foundation

### Ball & Brown (1968)
The seminal paper by Ray Ball and Philip Brown first documented that stock prices continue to drift in the direction of earnings surprises for up to 60 days after the announcement. This was one of the earliest challenges to the Efficient Market Hypothesis.

### Bernard & Thomas (1989)
Victor Bernard and Jacob Thomas provided the most comprehensive analysis of PEAD. Their findings showed:
- Stocks in the highest earnings surprise decile outperformed the lowest decile by approximately 4% in the 60 days following the announcement
- The drift was strongest in the first 2-3 weeks post-announcement
- Smaller, less liquid stocks exhibited stronger drift
- The anomaly persisted across different time periods and market conditions

### Foster, Olsen & Shevlin (1984)
Confirmed that the drift is proportional to the magnitude of the earnings surprise, with larger surprises producing more persistent drift.

## Why It Works: Market Underreaction

PEAD exists because of several behavioral and structural factors:

1. **Anchoring Bias**: Analysts and investors anchor to prior earnings estimates and adjust insufficiently to new information
2. **Gradual Information Diffusion**: Not all market participants process earnings information simultaneously; institutional investors, retail traders, and algorithmic systems react on different timelines
3. **Confirmation Bias**: Investors who were bearish before earnings may dismiss a positive surprise as a one-time event
4. **Liquidity Constraints**: Large institutional investors cannot immediately establish full positions without moving the market
5. **Post-Earnings Volatility Risk**: Many traders avoid the immediate post-earnings period due to elevated implied volatility, creating a delayed response

## Weekly Candle Approach

This screener uses weekly candle analysis rather than daily candles for several reasons:

### Why Weekly Candles

1. **Noise Reduction**: Weekly candles filter out intraday and daily noise, revealing the true post-earnings trend
2. **Institutional Footprints**: Large institutions typically build positions over weeks, not days; weekly candles capture their accumulation patterns
3. **Clear Pattern Recognition**: Red and green weekly candles provide unambiguous signals about buyer/seller dominance
4. **Manageable Monitoring**: Weekly cadence allows systematic monitoring without requiring daily attention

### Red Candle Pullback Pattern

The core pattern this screener identifies:

1. **Earnings Gap-Up**: Stock gaps up 3%+ on earnings announcement (green weekly candle)
2. **Post-Earnings Drift**: Stock may continue higher for 1-2 weeks (green candles)
3. **Red Candle Pullback**: An orderly pullback produces a red weekly candle (close < open)
4. **Breakout Signal**: When the next green candle closes above the red candle's high, this signals the pullback is complete and the PEAD trend is resuming

This pattern works because:
- The red candle represents profit-taking by short-term traders
- The lower wick of the red candle reveals where institutional buyers are willing to support the stock
- The breakout above the red candle high confirms that demand exceeds supply

## Stage-Based Monitoring System

The screener classifies each stock into one of four stages:

### MONITORING
- Stock has gapped up on earnings within the watch window
- No red weekly candle has formed yet
- Action: Add to watchlist, check weekly for red candle formation

### SIGNAL_READY
- A red weekly candle has formed after the earnings gap-up
- No breakout above the red candle high yet
- Action: Set price alert at red candle high; prepare order for breakout

### BREAKOUT
- Current weekly candle is green AND price is above the red candle high
- This is the actionable trade signal
- Action: Enter position with stop below red candle low

### EXPIRED
- More than 5 weeks (configurable) have passed since earnings
- The PEAD effect diminishes significantly after this window
- Action: Remove from watchlist

## Historical Performance Characteristics

Based on academic research and practical observations:

- **Win Rate**: PEAD strategies historically show 55-65% win rates
- **Average Winner vs. Loser**: Winners tend to be 1.5-2.5x larger than losers
- **Optimal Holding Period**: 2-6 weeks post-entry for the core PEAD drift
- **Sector Sensitivity**: Technology and growth sectors tend to show stronger PEAD effects
- **Market Cap Effect**: Mid-cap stocks ($2B-$20B) often show the strongest drift due to analyst coverage gaps
- **Earnings Quality**: Stocks with revenue beats in addition to EPS beats show stronger drift

## Key Differences from Other Momentum Strategies

Unlike pure price momentum strategies, PEAD is fundamentally driven:
- It requires a specific catalyst (earnings announcement)
- The thesis is grounded in information underreaction, not just trend following
- It has a defined entry window (post-earnings) and monitoring period
- Risk management is anchored to the red candle pattern, not arbitrary stop levels
