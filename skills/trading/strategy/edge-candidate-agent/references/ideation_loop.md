# Ideation Loop (Human + LLM)

Use this reference when generating hints before running auto detection.

## Hint File Schema (`hints.yaml`)

```yaml
hints:
  - title: "AI leaders breaking out after shallow pullback"
    observation: "Large-cap semis recovered above key moving averages"
    preferred_entry_family: "pivot_breakout"
    symbols: ["NVDA", "AVGO", "SMCI"]
    regime_bias: "RiskOn"
    mechanism_tag: "behavior"
```

## LLM CLI Integration Contract

`auto_detect_candidates.py --llm-ideas-cmd "<command>"` passes JSON to stdin:

```json
{
  "as_of": "YYYY-MM-DD",
  "market_summary": {...},
  "anomalies": [...],
  "instruction": "Generate concise edge hints ..."
}
```

The command must print either:

- `[{...}, {...}]` (YAML/JSON list), or
- `{"hints": [{...}, {...}]}`.

Each hint supports:

- `title`
- `observation`
- `preferred_entry_family` (`pivot_breakout` or `gap_up_continuation`)
- `symbols` (optional)
- `regime_bias` (optional)
- `mechanism_tag` (optional)

## Suggested Daily Loop

1. Run detector without LLM hints and review `anomalies.json`.
2. Generate or edit `hints.yaml` from observed market behavior.
3. Re-run detector with `--hints` (and optionally `--llm-ideas-cmd`).
4. Compare exported ticket quality over time and keep only stable ideas.
