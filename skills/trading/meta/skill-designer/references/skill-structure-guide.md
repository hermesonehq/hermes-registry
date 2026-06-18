# Skill Structure Guide

## Directory Layout

Every skill follows this standardized structure:

```
<skill-name>/
├── SKILL.md              # Required: Skill definition with YAML frontmatter
├── references/           # Knowledge bases loaded into Claude's context
├── scripts/             # Executable Python scripts (not auto-loaded)
│   └── tests/           # Test files for scripts
└── assets/              # Templates and resources for output generation
```

## SKILL.md Format

### YAML Frontmatter (Required)

```yaml
---
name: <skill-name>
description: <one-line trigger description>
---
```

- `name` MUST match the directory name exactly
- `description` defines when the skill should be triggered; keep it concise

### Body Sections (Required)

1. **Overview** -- What the skill does (2-3 sentences)
2. **When to Use** -- Bullet list of trigger conditions
3. **Prerequisites** -- Python version, API keys, dependencies
4. **Workflow** -- Step-by-step execution instructions (imperative form)
5. **Output Format** -- JSON and/or Markdown report structure
6. **Resources** -- List of reference files and scripts

## Writing Style

- Use imperative/infinitive verb forms: "Analyze the chart", "Generate report"
- Write instructions for Claude to execute, NOT user instructions
- Avoid "You should..." or "Claude will..." -- state actions directly
- Include concrete bash command examples with full paths

## Naming Conventions

- Directory name: lowercase, hyphen-separated (e.g., `position-sizer`)
- SKILL.md frontmatter `name:` must match directory name
- Scripts: `snake_case.py` (e.g., `check_data_quality.py`)
- Reports: `<skill>_<analysis-type>_<date>.{md,json}`
- Output directory: default to `reports/`

## Progressive Loading

1. Metadata (YAML frontmatter) loads first for skill detection
2. SKILL.md body loads when skill is invoked
3. References load conditionally based on analysis needs
4. Scripts execute on demand, never auto-loaded into context

## Script Requirements

- Check for API keys before making requests
- Validate date ranges and input parameters
- Provide helpful error messages to stderr
- Return proper exit codes (0 success, 1 error)
- Support retry logic with exponential backoff for rate limits
- Use relative paths or dynamic resolution (no hardcoded absolute paths)
- Default `--output-dir` to `reports/`

## Reference Document Patterns

- Use declarative statements of fact
- Include historical examples and case studies where applicable
- Provide decision frameworks and checklists
- Organize hierarchically (H2 for major sections, H3 for subsections)

## Analysis Output Requirements

All outputs must:
- Be saved to the `reports/` directory
- Include date/time stamps
- Use English language
- Provide probability assessments where applicable
- Include specific trigger levels for actionable scenarios
