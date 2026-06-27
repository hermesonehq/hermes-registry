# Publishing an entry

Anyone can add a skill, MCP server, agent, or workflow to the registry by opening
a pull request against the catalog repo. The catalog is the single source of
truth; CI validates your entry and regenerates `index.json`.

## 1. Pick the type and folder

| Type       | Folder layout                                                        |
| ---------- | ------------------------------------------------------------------- |
| Skill      | `skills/<category>/<name>/SKILL.md` (+ optional `scripts/` etc.)     |
| MCP        | `mcp/<name>/manifest.json` (+ `icon.svg`/`icon.png`, optional `server/`) |
| Agent      | `agents/<name>/manifest.json` + `AGENT.md`                          |
| Workflow   | `workflows/<name>/manifest.json` + `workflow.json`                  |

The folder name is the entry name and matches the name part of `id`.

## 2. Write the manifest (MCP / agent / workflow)

Manifests validate against the schemas in `schemas/`. The common core
(`schemas/manifest.base.json`) requires:

```json
{
  "schemaVersion": "1",
  "type": "mcp",
  "id": "github",
  "name": "GitHub",
  "version": "1.1.0",
  "description": "Manage repos, issues, and pull requests via the GitHub API.",
  "author": { "name": "GitHub", "url": "https://github.com/github/github-mcp-server" },
  "license": "MIT",
  "source": "https://github.com/github/github-mcp-server",
  "tags": ["github", "git"],
  "icon": "icon.svg",
  "compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" }
}
```

Type-specific fields:

- **MCP** — `transport` (`stdio` | `http`), then `command`+`args` (stdio) or
  `url` (http), optional `env`, and a `configSchema` declaring user-supplied
  secrets. **Pin** the package/image the client launches (`@scope/pkg@1.2.3`,
  `pkg@1.2.3`, `image:v1.2.3` — never bare `latest`). Point `source` at the
  upstream code. Never commit secrets — declare them in `configSchema`.
- **Agent** — `model`, `tools`, and an `entry` (defaults to `AGENT.md`) holding
  the persona.
- **Workflow** — `entry`, `requires` (the skills/agents/MCPs it chains), and the
  steps in `workflow.json`.

Skills carry no manifest: all metadata lives in the `SKILL.md` frontmatter
(agentskills.io), with registry extras under `metadata.hermes`.

## 3. Validate locally

```bash
python scripts/validate.py
```

This checks every manifest against its schema and reports errors (warnings for
missing recommended skill fields are fine).

## 4. Open a PR

Do **not** edit the generated catalog (`index.json`, `categories.json`,
`models.json`) — CI regenerates them via `scripts/build_index.py` on merge.

### Checklist

- [ ] Folder name matches the name part of `id`.
- [ ] Manifest validates (`python scripts/validate.py`).
- [ ] The declared `command`/`args` (or `url`) actually launches the server.
- [ ] Package/image version is **pinned** (no bare names, no `latest`).
- [ ] `source` points at the upstream code.
- [ ] All required secrets declared in `configSchema` — none hardcoded.
- [ ] Icon present (SVG, or 512×512 PNG).
- [ ] `version` bumped (semver) and `compatibility` honest.

See the per-type `README.md` in `mcp/`, `agents/`, `workflows/`, and `skills/`
for the full details.
