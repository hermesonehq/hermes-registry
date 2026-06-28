# Agents

An **agent** is a named subagent persona — a system prompt plus its preferred
model and tool allowlist — that Hermes can delegate work to.

## Folder layout

```
agents/<name>/
├── manifest.json     # metadata (validated against schemas/agent.schema.json)
├── AGENT.md          # the system prompt / persona (entry file)
└── icon.svg          # or icon.png (512×512)
```

## manifest.json

```json
{
  "schemaVersion": "1",
  "type": "agent",
  "id": "ziqx/code-reviewer",
  "name": "Code Reviewer",
  "version": "1.0.0",
  "description": "Reviews diffs for bugs and suggests fixes",
  "author": { "name": "ziqx", "url": "https://github.com/ziqx" },
  "license": "MIT",
  "tags": ["code", "review"],
  "icon": "icon.svg",
  "compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" },

  "entry": "AGENT.md",
  "model": "claude-opus-4-8",
  "tools": ["Read", "Grep", "Bash"],

  "funding": { "address": "0x…", "token": "HD", "chain": "base" }
}
```

- `model` — preferred model (clients may override).
- `tools` — the allowlist this agent is permitted to use.

## AGENT.md

The entry file is the system prompt that defines the persona — its role,
expertise, how it should behave, and its output format.

```markdown
# Code Reviewer

You are a meticulous code reviewer. Given a diff, find correctness bugs and
suggest minimal fixes. Be concise. Prioritise high-confidence findings …
```

## Checklist

- [ ] Folder name is the agent name (e.g. `code-reviewer`), matching the name part of `id`
- [ ] `manifest.json` validates (`python scripts/validate.py`)
- [ ] `AGENT.md` present and referenced by `entry`
- [ ] `tools` lists only what the agent needs
- [ ] Icon present (SVG, or 512×512 PNG)
- [ ] `version` bumped (semver) and `compatibility` honest
