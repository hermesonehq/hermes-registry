# Workflows

A **workflow** is a multi-step recipe that chains skills, agents, and MCP tools
into a repeatable pipeline.

## Folder layout

```
workflows/<name>/
├── manifest.json     # metadata (validated against schemas/workflow.schema.json)
├── workflow.json     # the steps (entry file)
└── icon.svg          # or icon.png (512×512)
```

## manifest.json

```json
{
  "schemaVersion": "1",
  "type": "workflow",
  "id": "ziqx/pr-triage",
  "name": "PR Triage",
  "version": "1.0.0",
  "description": "Label, summarise, and assign incoming pull requests",
  "author": { "name": "ziqx", "url": "https://github.com/ziqx" },
  "license": "MIT",
  "tags": ["github", "automation"],
  "icon": "icon.svg",
  "compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" },

  "entry": "workflow.json",
  "requires": ["agents/ziqx/code-reviewer", "mcp/ziqx/github"],

  "funding": { "address": "0x…", "token": "HD", "chain": "base" }
}
```

- `requires` — IDs of other registry entries this workflow depends on. The
  installer resolves these so they're present before the workflow runs.

## workflow.json

The entry file describes the ordered steps. Each step names what it runs
(a skill, agent, or MCP tool) and how its output feeds the next.

```json
{
  "name": "PR Triage",
  "steps": [
    { "id": "fetch", "uses": "mcp/ziqx/github", "tool": "get_pr" },
    { "id": "review", "uses": "agents/ziqx/code-reviewer", "input": "${fetch.diff}" },
    { "id": "label", "uses": "mcp/ziqx/github", "tool": "add_labels",
      "input": "${review.labels}" }
  ]
}
```

## Checklist

- [ ] Folder name is the workflow name (e.g. `pr-triage`), matching the name part of `id`
- [ ] `manifest.json` validates (`python scripts/validate.py`)
- [ ] `workflow.json` present and referenced by `entry`
- [ ] Every dependency listed in `requires` exists in the registry
- [ ] Icon present (SVG, or 512×512 PNG)
- [ ] `version` bumped (semver) and `compatibility` honest
