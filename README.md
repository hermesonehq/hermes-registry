<img width="100%" alt="HERMES DESKTOP" src="assets/header.webp" />

<br/>

A community package registry for the **Hermes** agent. It indexes installable
extensions — skills, MCP servers, agents, and workflows — that the Hermes Python
agent and its Electron desktop companion can discover and install.

Everything here is **free and open**. Skills, agents, and workflows are
self-contained (metadata + code live together). MCP entries are a catalog layer:
the manifest points at a pinned, already-published server (and a `source` link),
which the client installs at run time — so you can still browse and inspect any
artifact directly.

---

## What's in the registry

| Type         | Folder       | What it is                                               | Format                                                              |
| ------------ | ------------ | -------------------------------------------------------- | ------------------------------------------------------------------- |
| **Skill**    | `skills/`    | A task procedure Hermes can follow                       | `SKILL.md` + frontmatter ([agentskills.io](https://agentskills.io)) |
| **MCP**      | `mcp/`       | A Model Context Protocol server (tools/resources)        | `manifest.json`                                                     |
| **Agent**    | `agents/`    | A named subagent persona (system prompt + tools + model) | `manifest.json` + `AGENT.md`                                        |
| **Workflow** | `workflows/` | A multi-step recipe chaining skills / agents / MCPs      | `manifest.json` + `workflow.json`                                   |
| **Model**    | `models/`    | A provider's model catalog (context, modalities, etc.)   | `<provider>.json` ([models/README.md](models/README.md))            |

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
│       ├── manifest.json      # delegates to a pinned published server (npx/uvx/docker)
│       ├── icon.png
│       └── server/            # OPTIONAL — only when the source is first-party
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
├── models/                    # one <provider>.json per provider (model catalog)
│   ├── openai.json
│   └── anthropic.json
├── schemas/                   # JSON Schema per type (validation source of truth)
├── scripts/
│   ├── build_index.py         # scans folders → generates index/categories/models json
│   └── validate.py            # validates every manifest against its schema
├── index.json                 # GENERATED catalog — the registry endpoint
├── categories.json            # GENERATED taxonomy for the desktop gallery
├── models.json                # GENERATED model catalog (providers + their models)
└── README.md
```

---

## `index.json` — the catalog

Clients never crawl folders. A build step (`scripts/build_index.py`) scans every
entry — reading skill `SKILL.md` frontmatter and the `manifest.json` of MCPs /
agents / workflows — and emits a single `index.json`. The desktop gallery and the
Python agent both fetch this one file to discover everything available.

From there the client resolves the entry's `manifest.json` to install and run it
on demand — for MCP servers that's a pinned `npx` / `uvx` / `docker` launch with
user-supplied config injected at startup. See
[mcp/README.md → How a client pulls & runs an MCP](mcp/README.md#how-a-client-pulls--runs-an-mcp).

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
      "compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" },
      "acceptsFunding": false
    }
  ]
}
```

`index.json` is **generated, never hand-edited** — CI regenerates it on every
change so it can't drift from the folders. The same build step also emits
`models.json`, a dedicated catalog of model providers and the models they serve
(see [models/README.md](models/README.md)), so clients fetch one file instead of
crawling every `models/<provider>.json`.

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
  "source": "https://github.com/…",
  "tags": ["web", "data"],
  "icon": "icon.svg",
  "compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" },
  "dependencies": [{ "id": "mcp/postgres", "version": "^1" }],
  "permissions": ["network", "filesystem:read"],
  "funding": { "address": "0x…", "token": "HD", "chain": "base" }
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
"compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" }
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
address so users and agents can send a tip in the HD token on Base.

```json
"funding": {
  "address": "0x…",     // required if `funding` is present
  "token": "HD",        // HD token (Base network)
  "ca": "0xfda75f77a22b4f4b783bbbb21915ef64d149bba3",  // token contract address
  "chain": "base"
}
```

- Omit the `funding` block entirely and the artifact simply has no donate option.
- The desktop gallery shows a **Donate** action when an address is present.
- No pricing, no gating — all code stays free and public. This is a tip jar.

---

## Contributing

1. Fork this repo.
2. Add your entry:
   - **Skill** → `skills/<category>/<name>/SKILL.md` (agentskills.io frontmatter).
     See [skills/README.md](skills/README.md).
   - **MCP / agent / workflow** → `{type}/<name>/manifest.json` + entry file.
     See each type's README.
3. Add an icon if you have one (`icon.svg`, or 512×512 `icon.png`) — optional.
4. Validate locally:
   ```bash
   pip install -r requirements.txt
   python scripts/validate.py
   ```
5. Open a PR. The **Validate** workflow checks every entry on each PR (errors
   fail the check; warnings are allowed).

The catalog (`index.json` + `categories.json` + `models.json`) is **generated,
never hand-edited**. The **Build Index** workflow regenerates and commits it on every
push to `main` (the commit carries `[skip ci]` so it doesn't loop) — so `main`
always carries a fresh catalog.

### Guidelines

- IDs: skills use their `name`; MCP/agent/workflow may use `author/name` to avoid collisions.
- Bump `version` (semver) on every change.
- Declare honest `permissions` and `compatibility` (`hermes` + `desktop`).
- Keep entries self-contained — no secrets in the repo (MCP servers declare
  config via `configSchema`; secrets are supplied by the user at install time).

---

## License

See individual entries for their declared `license`. Registry tooling and
schemas are MIT unless noted otherwise.
