# Skills

A **skill** is a task procedure Hermes can follow. Skills use the
[agentskills.io](https://agentskills.io) open standard — a single `SKILL.md`
with YAML frontmatter — so they drop into Hermes unchanged.

> Skills use the agentskills.io format (no separate `manifest.json`). MCPs,
> agents, and workflows use the registry's `manifest.json` schema.

## Folder layout

Skills nest by **category**, then skill name:

```
skills/<category>/<name>/
├── SKILL.md          # required — frontmatter + instructions
├── references/       # optional — supporting docs
├── scripts/          # optional — executable helpers
├── templates/        # optional — output examples
├── assets/           # optional — other files
└── icon.svg          # optional — SVG or 512×512 PNG
```

Categories in this registry: `software-development`, `github`, `research`,
`productivity`, … (create a new category folder if yours doesn't fit).

## SKILL.md frontmatter

```yaml
---
name: plan
description: "Plan mode: write markdown plan to .hermes/plans/, no exec."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
prerequisites:                       # optional
  env_vars: [SOME_API_KEY]
  commands: [curl]
metadata:
  hermes:
    tags: [planning, workflow]
    category: software-development
    related_skills: [writing-plans]
    # --- registry extensions (optional) ---
    compatibility: { hermes: ">=0.3.0", desktop: ">=0.6.0" }
    funding: { address: "0x…", token: "H1", chain: "base" }
---

# Plan Mode

Use this skill when the user wants a plan instead of execution.

## Core behavior
…
```

### Fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | ✅ | Unique within its category |
| `description` | ✅ | One line; when/what the skill does |
| `version` | ✅ | Semver |
| `author` | ✅ | Name or org |
| `license` | ✅ | SPDX id (e.g. `MIT`) |
| `platforms` | ✅ | Any of `linux`, `macos`, `windows` |
| `prerequisites` | optional | `env_vars`, `commands` the skill needs |
| `metadata.hermes.tags` | recommended | For search/browse |
| `metadata.hermes.category` | recommended | Matches the folder |
| `metadata.hermes.related_skills` | optional | Cross-links |
| `metadata.hermes.compatibility` | optional | Registry extension — `{ hermes, desktop }` semver ranges |
| `metadata.hermes.funding` | optional | Registry extension — tip-jar wallet `{ address, token, chain }` |

The registry's `compatibility` and `funding` live under `metadata.hermes` so the
file stays a valid agentskills.io skill. `build_index.py` reads the frontmatter
(not a manifest) to build `index.json`.

## Body

After the frontmatter, write the actual procedure — what the skill does, when to
use it, and the step-by-step instructions. Reference files in `references/`,
`scripts/`, or `templates/` as needed.

## Checklist

- [ ] Under the right `category/` folder; folder name is the skill `name`
- [ ] `SKILL.md` has valid frontmatter (`python scripts/validate.py`)
- [ ] `prerequisites` honest — no secrets committed
- [ ] `version` bumped (semver)
- [ ] Icon optional, but if present: SVG or 512×512 PNG

## Attribution

The skills currently in this registry were imported from
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
(MIT, © 2025 Nous Research). Each `SKILL.md` retains its original `author` and
`license` frontmatter.
