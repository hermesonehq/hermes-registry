# Hermes Registry

A community package registry for the **Hermes** agent. It indexes installable
extensions — skills, MCP servers, agents, and workflows — that the Hermes Python
agent and its Electron desktop companion can discover and install.

Everything here is **free and open**. Each entry is self-contained (metadata +
code live together), so you can browse, clone, and inspect any artifact directly.

---

## What's in the registry

| Type | Folder | What it is | Format |
|------|--------|------------|--------|
| **Skill** | `skills/` | A task procedure Hermes can follow | `SKILL.md` + frontmatter ([agentskills.io](https://agentskills.io)) |
| **MCP** | `mcp/` | A Model Context Protocol server (tools/resources) | `manifest.json` |
| **Agent** | `agents/` | A named subagent persona (system prompt + tools + model) | `manifest.json` + `AGENT.md` |
| **Workflow** | `workflows/` | A multi-step recipe chaining skills / agents / MCPs | `manifest.json` + `workflow.json` |

Two formats by design:

- **Skills** follow the [agentskills.io](https://agentskills.io) open standard —
  a single `SKILL.md` with YAML frontmatter, **no separate manifest** — nested by
  `category/skill-name/`. This lets them drop into Hermes unchanged. Registry
  extras (`compatibility`, `funding`) live under `metadata.hermes` in the
  frontmatter. See [skills/README.md](skills/README.md).
- **MCPs, agents, and workflows** use the registry's `manifest.json` schema (in
  `schemas/`), folder = `{type}/{name}`.

```
hermes-registry/
├── skills/                        # agentskills.io format, nested by category
│   └── software-development/
│       └── plan/
│           ├── SKILL.md           # frontmatter holds all metadata
│           └── scripts/           # optional references/ scripts/ templates/
├── mcp/
│   └── postgres/
│       ├── manifest.json
│       ├── icon.png
│       └── server/            # MCP server source
├── agents/
│   └── code-reviewer/
│       ├── manifest.json
│       ├── AGENT.md
│       └── icon.svg
├── workflows/
│   └── pr-triage/
│       ├── manifest.json
│       ├── workflow.json
│       └── icon.svg
├── schemas/                   # JSON Schema per type (validation source of truth)
├── scripts/
│   ├── build_index.py         # scans folders → generates index.json
│   └── validate.py            # validates every manifest against its schema
├── index.json                 # GENERATED catalog — the registry endpoint
├── categories.json            # taxonomy for the desktop gallery
└── README.md
```

---

## `index.json` — the catalog

Clients never crawl folders. A build step (`scripts/build_index.py`) scans every
entry — reading skill `SKILL.md` frontmatter and the `manifest.json` of MCPs /
agents / workflows — and emits a single `index.json`. The desktop gallery and the
Python agent both fetch this one file to discover everything available.

```json
{
  "schemaVersion": "1",
  "generated": "2026-06-02T00:00:00Z",
  "entries": [
    {
      "id": "plan",
      "type": "skill",
      "category": "software-development",
      "name": "plan",
      "version": "1.0.0",
      "description": "Plan mode: write markdown plan to .hermes/plans/, no exec.",
      "tags": ["planning", "workflow"],
      "author": "Hermes Agent",
      "path": "skills/software-development/plan",
      "icon": null,
      "checksum": "sha256:…",
      "compatibility": { "hermes": ">=0.3.0", "desktop": ">=1.2.0" },
      "acceptsFunding": false
    }
  ]
}
```

`index.json` is **generated, never hand-edited** — CI regenerates it on every
change so it can't drift from the folders.

---

## The manifest

Every artifact has a `manifest.json` sharing a common core, plus type-specific
fields. All manifests are validated in CI against the schemas in `schemas/`.

### Shared core (all types)

```json
{
  "schemaVersion": "1",
  "type": "skill | mcp | agent | workflow",
  "id": "ziqx/web-scraper",
  "name": "Web Scraper",
  "version": "1.2.0",
  "description": "Scrape and structure web pages",
  "author": { "name": "ziqx", "url": "https://…" },
  "license": "MIT",
  "tags": ["web", "data"],
  "icon": "icon.svg",
  "compatibility": { "hermes": ">=0.3.0", "desktop": ">=1.2.0" },
  "dependencies": [{ "id": "mcp/postgres", "version": "^1" }],
  "permissions": ["network", "filesystem:read"],
  "funding": { "address": "0x…", "token": "HERMES", "chain": "base" }
}
```

### Type-specific fields

- **skill** — `entry: "SKILL.md"`
- **mcp** — `transport` (`stdio` | `http`), `command`, `args`, `env`, `configSchema`
- **agent** — `entry: "AGENT.md"`, `model`, `tools: [...]`
- **workflow** — `entry: "workflow.json"`, `requires: [<ids>]`

---

## Compatibility

Each entry declares the versions it works with. Both fields are
[semver](https://semver.org/) ranges (`>=`, `^`, `~`, `*`).

```json
"compatibility": { "hermes": ">=0.3.0", "desktop": ">=1.2.0" }
```

- The **Python agent** checks `hermes`.
- The **Electron desktop app** checks both `desktop` (for itself) and `hermes`
  (for the running agent), and greys out / labels entries it can't install yet.

---

## Icons

Each entry has one icon, referenced by the `icon` field in its manifest.

- **Preferred:** `icon.svg` (scales freely, ~1 KB)
- **Fallback:** `icon.png`, square, **512×512**, transparent background
- **Size caps:** SVG ≤ 50 KB, PNG ≤ 256 KB

The `icon` field is just a filename, so either format works. `build_index.py`
resolves it to a full path in `index.json` for the gallery.

---

## Funding (optional)

Everything in the registry is free. Authors may **optionally** add a wallet
address so users and agents can send a tip in the Hermes token on Base.

```json
"funding": {
  "address": "0x…",     // required if `funding` is present
  "token": "HERMES",    // Hermes token (Base network)
  "chain": "base"
}
```

- Omit the `funding` block entirely and the artifact simply has no donate option.
- The desktop gallery shows a **Donate** action when an address is present.
- No pricing, no gating — all code stays free and public. This is a tip jar.

---

## Contributing

1. Fork this repo.
2. Create a folder under the right type: `skills/<name>/`, `mcp/<name>/`,
   `agents/<name>/`, or `workflows/<name>/`.
3. Add a `manifest.json`, an `icon.svg` (or 512×512 `icon.png`), and the entry
   file for that type.
4. Run validation locally:
   ```bash
   python scripts/validate.py
   ```
5. Open a PR. CI validates every manifest against its schema, checks icons, and
   regenerates `index.json`.

### Guidelines

- Use `author/name` IDs (e.g. `ziqx/web-scraper`) to avoid collisions.
- Bump `version` (semver) on every change.
- Declare honest `permissions` and `compatibility`.
- Keep entries self-contained — no secrets in the repo (MCP servers declare
  config via `configSchema`; secrets are supplied by the user at install time).

---

## License

See individual entries for their declared `license`. Registry tooling and
schemas are MIT unless noted otherwise.
