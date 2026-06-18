<!-- Design Reference Template for report_generator.py
     NOT rendered at runtime. Update both files together. -->

# Druckenmiller Strategy Synthesizer Report

**Generated:** {{metadata.generated_at}}
**Input Skills:** {{metadata.skills_loaded}} loaded ({{metadata.required_count}} required + {{metadata.optional_count}} optional)

---

## 1. Conviction Dashboard

| Metric | Value |
|--------|-------|
| **Conviction Score** | **{{conviction.conviction_score}}/100** |
| **Zone** | {{conviction.zone}} |
| **Recommended Exposure** | {{conviction.exposure_range}} |
| **Strongest Component** | {{conviction.strongest_component.label}} ({{conviction.strongest_component.score}}) |
| **Weakest Component** | {{conviction.weakest_component.label}} ({{conviction.weakest_component.score}}) |

> **Guidance:** {{conviction.guidance}}

**Recommended Actions:**

{{#each conviction.actions}}
- {{this}}
{{/each}}

---

## 2. Pattern Classification

**Detected Pattern:** {{pattern.label}} (match: {{pattern.match_strength}}%)

> {{pattern.description}}

| Pattern | Match Score |
|---------|-----------|
{{#each pattern.all_pattern_scores}}
| {{@key}} | {{this}} |
{{/each}}

---

## 3. Component Scores (7 Components)

| # | Component | Weight | Score | Weighted |
|---|-----------|--------|-------|----------|
{{#each conviction.component_scores}}
| {{@index}} | {{this.label}} | {{this.weight}} | {{this.score}} | {{this.weighted_contribution}} |
{{/each}}
| | **TOTAL** | **100%** | | **{{conviction.conviction_score}}** |

---

## 4. Input Skills Summary

### Required Skills

| Skill | Score | Zone/State | Key Signal |
|-------|-------|-----------|------------|
{{#each input_summary_required}}
| {{this.name}} | {{this.score}} | {{this.zone}} | {{this.signal}} |
{{/each}}

### Optional Skills

| Skill | Score | Key Signal |
|-------|-------|------------|
{{#each input_summary_optional}}
| {{this.name}} | {{this.score}} | {{this.signal}} |
{{/each}}

---

## 5. Target Allocation

| Asset Class | Allocation |
|-------------|-----------|
| Equity | {{allocation.target.equity}}% |
| Bonds | {{allocation.target.bonds}}% |
| Alternatives | {{allocation.target.alternatives}}% |
| Cash | {{allocation.target.cash}}% |

---

## 6. Position Sizing & Risk

| Parameter | Value |
|-----------|-------|
| Max Single Position | {{position_sizing.max_single_position}}% |
| Daily Volatility Target | {{position_sizing.daily_vol_target}}% |
| Max Open Positions | {{position_sizing.max_positions}} |

---

## 7. Druckenmiller Principle

> *"{{druckenmiller_quote}}"*
>
> — Stanley Druckenmiller

**Application:** {{druckenmiller_application}}

---

## Methodology

This report synthesizes outputs from 8 upstream analysis skills (5 required + 3 optional) into a single conviction score using Stanley Druckenmiller's investment philosophy.

**7 Components** (weighted 0-100):

1. Market Structure (18%): Breadth + Uptrend health
2. Distribution Risk (18%): Market Top risk (inverted)
3. Bottom Confirmation (12%): FTD Detector re-entry signal
4. Macro Alignment (18%): Macro Regime positioning
5. Theme Quality (12%): Theme Detector momentum
6. Setup Availability (10%): VCP + CANSLIM setups
7. Signal Convergence (12%): Cross-skill agreement

**4 Patterns:** Policy Pivot Anticipation, Unsustainable Distortion, Extreme Sentiment Contrarian, Wait & Observe

---

**Disclaimer:** This analysis is for educational and informational purposes only. Not investment advice. Past performance does not guarantee future results. Conduct your own research and consult a financial advisor before making investment decisions.
