# Workflow Contracts Reference

## Overview

Multi-skill workflows chain several skills in sequence, where the output of
step N feeds into step N+1. A **data contract** defines what each skill
produces and what its downstream consumer expects. When contracts are
violated -- missing fields, incompatible formats, wrong file patterns --
the handoff breaks silently.

## Contract Schema

Each skill contract specifies:

| Field | Description |
|-------|-------------|
| `output_format` | File format produced: `json`, `md`, `json+md`, `yaml` |
| `output_pattern` | Glob pattern for output filenames |
| `output_fields` | Required top-level fields in JSON/YAML output |
| `api_keys` | Environment variables needed to run the skill |

## Handoff Contract Schema

A handoff contract between producer and consumer specifies:

| Field | Description |
|-------|-------------|
| `mechanism` | How data flows: `file_param` (CLI arg), `directory`, `stdin` |
| `param` | CLI parameter(s) the consumer uses to accept input |
| `required_fields` | Fields the consumer reads from the producer's output |
| `description` | Human-readable explanation of the data flow |

## Known Handoff Contracts

### Earnings Momentum Trading Pipeline

```
earnings-trade-analyzer → pead-screener
  mechanism: file_param (--candidates-json)
  required_fields: symbol, grade, gap_pct
```

PEAD Screener's Mode B reads the earnings-trade-analyzer JSON output via
`--candidates-json`. The consumer filters by `grade >= B` and uses `symbol`
to fetch weekly candle data.

### Edge Research Pipeline

```
edge-candidate-agent → edge-hint-extractor
  mechanism: file_param (--market-summary, --anomalies)
  required_fields: market_summary, anomalies

edge-hint-extractor → edge-concept-synthesizer
  mechanism: file_param (--hints)
  required_fields: hints

edge-concept-synthesizer → edge-strategy-designer
  mechanism: file_param (--concepts)
  required_fields: concepts

edge-strategy-designer → edge-strategy-reviewer
  mechanism: file_param (--drafts-dir)
  required_fields: strategy_name, entry, exit
```

### Trade Execution Pipeline

```
screener skills → position-sizer
  mechanism: manual (user copies entry/stop from screener output)
  required_fields: (none -- user provides values)

analysis skills → data-quality-checker
  mechanism: file_param (--file)
  required_fields: (validates markdown content, not specific fields)
```

## Workflows Without Explicit Contracts

Some workflows (Daily Market Monitoring, Weekly Strategy Review) consist of
independent analysis steps that do not pass data between them. Each step
produces a standalone report. These workflows are validated for skill
existence and naming conventions only.

## File Naming Conventions

| Component | Convention | Example |
|-----------|-----------|---------|
| Skill directory | lowercase-hyphen | `earnings-trade-analyzer` |
| Python scripts | snake_case.py | `analyze_earnings_trades.py` |
| Output files | `<prefix>_YYYY-MM-DD_HHMMSS.{json,md}` | `integration_test_2026-03-01_120000.json` |
| SKILL.md name | must match directory name | `name: earnings-trade-analyzer` |

## Adding New Contracts

When creating a new multi-skill workflow:

1. Define each skill's output contract (format, fields, pattern)
2. Define handoff contracts for consecutive steps with data dependencies
3. Add the contracts to the `SKILL_CONTRACTS` and `HANDOFF_CONTRACTS`
   dictionaries in `validate_workflows.py`
4. Run the integration tester to verify the new workflow
