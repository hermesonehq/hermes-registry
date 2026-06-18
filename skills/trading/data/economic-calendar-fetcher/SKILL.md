---
name: economic-calendar-fetcher
description: 'Fetch upcoming economic events and data releases using FMP API. Retrieve
  scheduled central bank decisions, employment reports, inflation data, GDP releases,
  and other market-moving economic indicators for specified date ranges (default:
  next 7 days). The script outputs raw JSON or text; the assistant filters, assesses
  impact, and generates the Markdown report.'
version: 1.0.0
author: TraderMonty
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - calendar
    - earnings
    - data
    - trading
    category: trading
    source: https://github.com/tradermonty/claude-trading-skills
---

# Economic Calendar Fetcher

## Overview

Retrieve upcoming economic events and data releases from the Financial Modeling Prep (FMP) Economic Calendar API. This skill fetches scheduled economic indicators including central bank monetary policy decisions, employment reports, inflation data (CPI/PPI), GDP releases, retail sales, manufacturing data, and other market-moving events that impact financial markets.

The skill uses a Python script to query the FMP API and returns raw JSON or text output. The assistant then filters events, assesses market impact, and generates a chronological Markdown report for each scheduled event. No files are generated automatically.

**Key Capabilities:**
- Fetch economic events for specified date ranges (max 90 days)
- Support flexible API key provision (environment variable or CLI argument)
- Filter by impact level, country, or event type (filtering performed by the assistant)
- Present filtered results as structured Markdown reports with impact analysis (assistant-generated, not script-generated)
- Default to next 7 days for quick market outlook

**Data Source:**
- FMP Economic Calendar API: `https://financialmodelingprep.com/api/v3/economic_calendar`
- Covers major economies: US, EU, UK, Japan, China, Canada, Australia
- Event types: Central bank decisions, employment, inflation, GDP, trade, housing, surveys

## When to Use This Skill

Use this skill when the user requests:

1. **Economic Calendar Queries:**
   - "What economic events are coming up this week?"
   - "Show me the economic calendar for the next two weeks"
   - "When is the next FOMC meeting?"
   - "What major economic data is being released next month?"

2. **Market Event Planning:**
   - "What should I watch for in the markets this week?"
   - "Are there any high-impact economic releases coming?"
   - "When is the next jobs report / CPI release / GDP report?"

3. **Specific Date Range Requests:**
   - "Get economic events from January 1 to January 31"
   - "What's on the economic calendar for Q1 2025?"

4. **Country-Specific Queries:**
   - "Show me US economic data releases next week"
   - "What ECB events are scheduled?"
   - "When is Japan releasing their inflation data?"

**DO NOT use this skill for:**
- Past economic events (use market-news-analyst for historical analysis)
- Corporate earnings calendars (this skill excludes earnings)
- Real-time market data or live quotes
- Technical analysis or chart interpretation

## Prerequisites

- **FMP API Key** (required): Sign up at https://financialmodelingprep.com for a free key (250 requests/day). Set via `FMP_API_KEY` environment variable or pass `--api-key` to the script.
- **Python 3.10+**: Required to run `skills/economic-calendar-fetcher/scripts/get_economic_calendar.py`.
- **No third-party packages**: The script uses only the Python standard library.

## Workflow

Follow these steps to fetch and analyze the economic calendar:

### Step 1: Obtain FMP API Key

**Check for API key availability (in priority order):**

1. **Recommended:** Check if `FMP_API_KEY` environment variable is set — this keeps the key out of session logs
2. **Acceptable:** Use `--api-key` CLI argument for one-off runs
3. **Not recommended:** Asking the user to paste the key into chat — session logs may retain it
4. If user doesn't have an API key, provide instructions:
   - Visit https://financialmodelingprep.com
   - Sign up for free account (250 requests/day limit)
   - Navigate to API dashboard to obtain key

**Example user interaction:**
```
User: "Show me economic events for next week"
Assistant: "I'll fetch the economic calendar. I'll use the FMP_API_KEY environment variable if it's set. Otherwise, please pass the key via --api-key when running the script."
```

### Step 2: Determine Date Range

**Set appropriate date range based on user request:**

**Default (no specific dates):** Today + 7 days
**User specifies period:** Use exact dates (validate format: YYYY-MM-DD)
**Maximum range:** 90 days (FMP API limitation)

**Examples:**
- "Next week" → Today to +7 days
- "Next two weeks" → Today to +14 days
- "January 2025" → 2025-01-01 to 2025-01-31
- "Q1 2025" → 2025-01-01 to 2025-03-31

**Validate date range:**
- Ensure start date ≤ end date
- Ensure range ≤ 90 days
- Warn if querying past dates

### Step 3: Execute API Fetch Script

**Run the get_economic_calendar.py script with appropriate parameters:**

**Basic usage (default 7 days):**
```bash
python3 skills/economic-calendar-fetcher/scripts/get_economic_calendar.py --api-key YOUR_KEY
```

**With specific date range:**
```bash
python3 skills/economic-calendar-fetcher/scripts/get_economic_calendar.py \
  --from 2025-01-01 \
  --to 2025-01-31 \
  --api-key YOUR_KEY \
  --format json
```

**Using environment variable (no --api-key needed):**
```bash
export FMP_API_KEY=your_key_here
python3 skills/economic-calendar-fetcher/scripts/get_economic_calendar.py \
  --from 2025-01-01 \
  --to 2025-01-07
```

**Script parameters:**
- `--from`: Start date (YYYY-MM-DD) - default: today
- `--to`: End date (YYYY-MM-DD) - default: today + 7 days
- `--api-key`: FMP API key (optional if FMP_API_KEY env var set)
- `--format`: Output format (json or text) - default: json
- `--output`: Output file path (optional, default: stdout)

**Handle errors and empty results:**
- Invalid API key → Ask user to verify key
- Rate limit exceeded (429) → Suggest waiting or upgrading FMP tier
- Network errors → Check your connection and re-run the script
- Invalid date format → Provide correct format example
- **Unexpected empty list for a plausible current/future range:** Do not declare the calendar empty yet. Verify the same range against the primary v3 endpoint directly, then locally filter rows by parsed `date` because FMP may return adjacent-date rows. This applies even when the helper script itself returned `[]` (not only when a stable endpoint was used).

Direct v3 fallback probe:
```bash
python3 - <<'PY'
import os, json, urllib.parse, urllib.request, datetime
start = datetime.date.fromisoformat("YYYY-MM-DD")
end = datetime.date.fromisoformat("YYYY-MM-DD")
url = "https://financialmodelingprep.com/api/v3/economic_calendar?" + urllib.parse.urlencode({
    "from": start.isoformat(), "to": end.isoformat(), "apikey": os.environ["FMP_API_KEY"]
})
with urllib.request.urlopen(url, timeout=30) as r:
    data = json.loads(r.read())
filtered = [e for e in data if start <= datetime.date.fromisoformat(e["date"][:10]) <= end]
filtered.sort(key=lambda e: e.get("date", ""))
print(json.dumps(filtered, indent=2))
PY
```

### Step 4: Parse and Filter Events

**Process the JSON response from the script:**

1. **Parse event data:** Extract all events from API response
2. **Apply user filters if specified:**
   - Impact level: "High", "Medium", "Low"
   - Country: "US", "EU", "JP", "CN", etc.
   - Event type: FOMC, CPI, Employment, GDP, etc.
   - Currency: USD, EUR, JPY, etc.

**Filter examples:**
- "Show only high-impact events" → Filter impact == "High"
- "US events only" → Filter country == "US"
- "Central bank decisions" → Search event name for "Rate", "Policy", "FOMC", "ECB", "BOJ"

**Event data structure:**
```json
{
  "date": "2025-01-15 14:30:00",
  "country": "US",
  "event": "Consumer Price Index (CPI) YoY",
  "currency": "USD",
  "previous": 2.6,
  "estimate": 2.7,
  "actual": null,
  "change": null,
  "impact": "High",
  "changePercentage": null
}
```

### Step 5: Assess Market Impact

**Evaluate the market significance of each event:**

**Impact Level Classification (from FMP):**
- **High Impact:** Major market-moving events
  - FOMC rate decisions, ECB/BOJ policy meetings
  - Non-Farm Payrolls (NFP), CPI, GDP
  - Market typically shows 0.5-2%+ intraday volatility

- **Medium Impact:** Significant but less volatile
  - Retail Sales, Industrial Production
  - PMI surveys, Consumer Confidence
  - Housing data, Durable Goods Orders

- **Low Impact:** Minor indicators
  - Weekly jobless claims (unless extreme)
  - Regional manufacturing surveys
  - Minor auction results

**Additional Context Factors:**

1. **Current Market Sensitivity:**
   - High inflation environment → CPI/PPI elevated importance
   - Recession fears → Employment data more critical
   - Rate cut speculation → Central bank meetings crucial

2. **Surprise Potential:**
   - Compare estimate vs. previous reading
   - Large expected changes = higher attention
   - Consensus uncertainty = higher impact potential

3. **Event Clustering:**
   - Multiple related events same day = amplified impact
   - Example: CPI + Retail Sales + Fed speech = Very High impact day

4. **Forward Significance:**
   - Does this event influence upcoming central bank decisions?
   - Is this a preliminary or final reading?
   - Will this data be revised?

### Step 6: Generate Output Report

> **Responsibility:** The script outputs raw JSON or text. This step is performed by the assistant using the script's output. No Markdown files are generated automatically; results are displayed in chat and can be saved to `reports/` on request.

**Create structured markdown report with the following sections:**

**Report Header:**
```markdown
# Economic Calendar
**Period:** [Start Date] to [End Date]
**Report Generated:** [Timestamp]
**Total Events:** [Count]
**High Impact Events:** [Count]
```

**Event Listing (Chronological):**

For each event, provide:

```markdown
## [Date] - [Day of Week]

### [Event Name] ([Impact Level])
- **Country:** [Country Code] ([Currency])
- **Time:** [HH:MM UTC]
- **Previous:** [Value]
- **Estimate:** [Consensus Forecast]
- **Impact Assessment:** [Your analysis]

**Market Implications:**
[2-3 sentences on why this matters, what markets watch for, typical reaction patterns]

---
```

**Example Event Entry:**

```markdown
## 2025-01-15 - Wednesday

### Consumer Price Index (CPI) YoY (High Impact)
- **Country:** US (USD)
- **Time:** 14:30 UTC (8:30 AM ET)
- **Previous:** 2.6%
- **Estimate:** 2.7%
- **Impact Assessment:** Very High - Core inflation metric for Fed policy decisions

**Market Implications:**
CPI reading above estimate (>2.7%) likely strengthens hawkish Fed expectations, potentially pressuring equities and supporting USD. Reading at or below 2.7% could reinforce disinflation narrative and support risk assets. Options market pricing 1.2% S&P 500 move on release day.

---
```

**Summary Section:**

Add analytical summary at the end:

```markdown
## Key Takeaways

**Highest Impact Days:**
- [Date]: [Events] - [Combined impact rationale]
- [Date]: [Events] - [Combined impact rationale]

**Central Bank Activity:**
- [Summary of any scheduled Fed/ECB/BOJ meetings or speeches]

**Major Data Releases:**
- Employment: [NFP, Unemployment Rate dates]
- Inflation: [CPI, PPI dates]
- Growth: [GDP, Retail Sales dates]

**Market Positioning Considerations:**
[2-3 bullets on how traders might position around these events]

**Risk Events:**
[Highlight any particularly high-uncertainty or surprise-potential events]
```

**Filtering Notes:**

If user requested specific filters, note at top:
```markdown
**Filters Applied:**
- Impact Level: High only
- Country: US
- Events shown: [X] of [Y] total events in date range
```

**Output:**
- Results are displayed in chat. No files are generated automatically.
- To save **raw JSON/text data**: use `--output reports/economic_calendar_[START]_to_[END].json` when running the script.
- To save the **Markdown report**: ask the assistant to write it to `reports/` after generating it in chat.

## Assistant-Generated Report Format

**Markdown structure requirements:**

1. **Chronological ordering:** Events sorted by date and time (earliest first)
2. **Impact level indicators:** Use (High Impact), (Medium Impact), (Low Impact) labels
3. **Time zone clarity:** Always specify UTC; ET/PT conversions are performed by the assistant based on US DST calendar
4. **Data completeness:** Include all available fields (previous, estimate, actual if past)
5. **Null handling:** Display "N/A" or "No estimate" for null values
6. **Impact assessment:** Every high/medium impact event must have market implications analysis

**Table format option (for dense listings):**

```markdown
| Date/Time (UTC) | Event | Country | Impact | Previous | Estimate | Assessment |
|-----------------|-------|---------|--------|----------|----------|------------|
| 01-15 14:30 | CPI YoY | US | High | 2.6% | 2.7% | Core inflation metric |
```

**Language:** All reports in English

## Resources

**Python Script:**
- `skills/economic-calendar-fetcher/scripts/get_economic_calendar.py`: Main API fetch script with CLI interface

**Reference Documentation:**
- `references/fmp_api_documentation.md`: Complete FMP Economic Calendar API reference
  - Authentication and API key management
  - Request parameters and date formats
  - Response field definitions
  - Rate limits and error handling
  - Best practices for caching and efficiency

**API Details:**
- Primary endpoint: `https://financialmodelingprep.com/api/v3/economic_calendar`
- Stable endpoint caveat: if a helper script or docs use `https://financialmodelingprep.com/stable/economics-calendar` and it returns `404` or `[]` for an otherwise valid date range, fall back to the v3 endpoint above before declaring the calendar empty.
- Date-range caveat: v3 responses can include rows just outside the requested `from`/`to` window; after fetching, filter events locally by parsed `date` so only the requested date range is reported.
- Authentication: API key required (free tier: 250 requests/day)
- Max date range: 90 days per request
- Response format: JSON array of event objects
- Rate limits: 5 requests/second (free tier)

**Event Coverage:**
- Major economies: US, EU, UK, Japan, China, Canada, Australia, Switzerland
- Event categories: Monetary policy, Employment, Inflation, GDP, Trade, Housing, Surveys
- Update frequency: Real-time (events added/updated as scheduled)
- Historical data: Available for past events with actual values

**Usage Tips:**
1. Cache results to minimize API calls (events rarely change once scheduled)
2. Query 7-30 day ranges for optimal request efficiency
3. Don't query >6 months in future (sparse data, speculative dates)
4. Refresh cache daily for upcoming week to catch time changes
5. Use smaller ranges (1-7 days) for real-time event monitoring

**Error Handling:**
- API key errors: Clear user guidance for obtaining free key
- Rate limits (429): Suggest waiting or upgrading FMP tier; re-run the script after the wait
- Network failures: Check connection and re-run; no automatic retry or cache in the script
- Stable endpoint returns `404` or an empty list for a valid range: retry the same range through `https://financialmodelingprep.com/api/v3/economic_calendar`, then locally filter returned events to the requested dates before reporting.
- Invalid dates: Validation with helpful error messages
