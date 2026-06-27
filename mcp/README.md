# MCP Servers

An **MCP** entry is a [Model Context Protocol](https://modelcontextprotocol.io)
server that exposes tools and/or resources to Hermes.

The registry is a **catalog, not a package mirror**. An MCP entry is normally
just a `manifest.json` that tells the client how to launch an already-published
server (`npx` / `uvx` / `docker`). The client installs it at run time. This keeps
the registry small and lets upstream security fixes flow without us re-vendoring.

- **Third-party servers** → manifest delegates to the published package. Pin the
  version (see below) and point `source` at the upstream code.
- **First-party servers** (authored for Hermes, where this repo *is* upstream) →
  ship the code in a `server/` folder and run it from there.

## Folder layout

```
mcp/<name>/
├── manifest.json     # metadata (validated against schemas/mcp.schema.json)
├── icon.svg          # or icon.png (512×512)
└── server/           # OPTIONAL — only for first-party servers whose source lives here
```

## manifest.json

```json
{
  "schemaVersion": "1",
  "type": "mcp",
  "id": "ziqx/postgres",
  "name": "Postgres MCP",
  "version": "1.0.0",
  "description": "Query and inspect Postgres databases",
  "author": { "name": "ziqx", "url": "https://github.com/ziqx" },
  "license": "MIT",
  "source": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
  "tags": ["database", "sql"],
  "icon": "icon.png",
  "compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" },
  "permissions": ["network"],

  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres@0.6.2"],
  "env": { "PGCONNECT_TIMEOUT": "10" },
  "configSchema": {
    "type": "object",
    "properties": {
      "DATABASE_URL": { "type": "string", "description": "Postgres connection string" }
    },
    "required": ["DATABASE_URL"]
  },

  "funding": { "address": "0x…", "token": "H1", "chain": "base" }
}
```

### Transport

- `stdio` — Hermes spawns `command` + `args` and talks over stdin/stdout.
- `http` — provide a `url` instead of `command`/`args`.

### Pin the version

Always pin the package/image the client launches, so what installs today still
installs next year and `compatibility` stays honest:

- `npx`   → `["-y", "@scope/pkg@1.2.3"]`
- `uvx`   → `["pkg-name@1.2.3"]`
- `docker`→ `"ghcr.io/org/image:v1.2.3"` (a tag, never bare `latest`)

### `source`

Point `source` at the upstream code (a repo URL or `tree/<ref>/path`). The
gallery surfaces it as a **View source** link so users can audit a server even
though its code isn't vendored here. For first-party servers, point it at the
local `server/` folder on the registry repo.

## How a client pulls & runs an MCP

Clients — the Hermes Python agent and the Electron desktop app — never clone
this repo. The whole flow is driven by `index.json` plus the entry's
`manifest.json`:

1. **Discover** — fetch `index.json`, list the MCP entries, render the gallery.
2. **Check compatibility** — compare the running Hermes / desktop versions
   against the entry's `compatibility` ranges; entries that don't match are
   greyed out or labelled.
3. **Collect config** — build a form from `configSchema` and ask the user for
   the required values (secrets, paths). They're stored in the OS keychain —
   never written to this repo, never to disk in plaintext.
4. **Install + launch** — spawn the pinned `command` + `args`. The launcher
   pulls and caches the server on first run; later launches are offline-fast:
   - `npx -y` → installs the npm package into the npx cache
   - `uvx`    → installs the PyPI package into the uv cache
   - `docker run` → pulls the pinned image
5. **Connect** — `stdio`: speak MCP over the child process's stdin/stdout;
   `http`: connect to `url`. The server's tools/resources now show up to the
   agent.

Nothing is "installed" into the registry or pre-built by us — the client
materialises the server on demand from the pinned coordinates in the manifest.

### Where config values go

`configSchema` says *what* the user must supply. Each property's `description`
says *where* it goes at launch — a client wires it one of two ways:

- **Environment variable** — tokens/secrets named like env vars
  (`BRAVE_API_KEY`, `SLACK_BOT_TOKEN`, `NOTION_TOKEN`,
  `GITHUB_PERSONAL_ACCESS_TOKEN`). The client sets them in the child process's
  environment, merged over the manifest's static `env`.
- **Appended to `args`** — values the server reads from the command line
  (postgres' connection string as the first positional arg; sqlite's
  `--db-path`; git's `--repository`; filesystem's allowed directories).

Worked example — the postgres entry, once the user supplies `DATABASE_URL`,
resolves to this spawn:

```sh
# env: PGCONNECT_TIMEOUT=10
npx -y @modelcontextprotocol/server-postgres@0.6.2 "postgresql://user:pass@host:5432/db"
```

> The env-vs-args destination currently lives in the property `description`, so
> it's human-readable but not machine-explicit. If you want clients to wire
> config fully deterministically, we can add an explicit marker to the schema
> (e.g. `x-target: "env" | "arg"`). Until then, follow the descriptions.

## Secrets & config

**Never commit secrets.** Declare what the server needs via `configSchema`. The
user supplies those values at install time (the desktop app stores them in the
OS keychain). The registry only ships the schema, not the values.

## Checklist

- [ ] Folder name is the MCP name (e.g. `postgres`), matching the name part of `id`
- [ ] `manifest.json` validates (`python scripts/validate.py`)
- [ ] The declared `command`/`args` (or `url`) actually launches the server
- [ ] Package/image version is **pinned** (no bare names, no `latest`)
- [ ] `source` points at the upstream code
- [ ] All required secrets declared in `configSchema` — none hardcoded
- [ ] Icon present (SVG, or 512×512 PNG)
- [ ] `version` bumped (semver) and `compatibility` honest
