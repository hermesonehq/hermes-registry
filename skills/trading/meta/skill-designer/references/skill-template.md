# SKILL.md Template

Use this template when creating a new skill's SKILL.md file.

```markdown
---
name: <skill-name>
description: <One-line description of when to trigger this skill. Be specific about user intent.>
---

# <Skill Display Name>

## Overview

<2-3 sentences describing what the skill does and its primary value.>

## When to Use

- <Specific trigger condition 1>
- <Specific trigger condition 2>
- <Specific trigger condition 3>

## Prerequisites

- Python 3.9+
- <API key requirements or "No API keys required">
- <Any third-party packages or "Standard library only">

## Workflow

### Step 1: <Action Name>

<Description of what to do in this step.>

```bash
python3 skills/<skill-name>/scripts/<script_name>.py \
  --param1 value1 \
  --output-dir reports/
```

### Step 2: <Action Name>

<Description of what to do in this step.>

### Step 3: <Action Name>

<Description of what to do in this step.>

## Output Format

### JSON Report

```json
{
  "schema_version": "1.0",
  "<key>": "<value>"
}
```

### Markdown Report

<Description of markdown report structure and contents.>

Reports are saved to `reports/` with filenames `<prefix>_YYYY-MM-DD_HHMMSS.{json,md}`.

## Resources

- `scripts/<script_name>.py` -- <Brief description>
- `references/<ref_name>.md` -- <Brief description>

## Key Principles

1. <Principle 1>
2. <Principle 2>
3. <Principle 3>
```
