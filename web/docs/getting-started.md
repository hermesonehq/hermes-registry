# Getting started

This guide takes you from nothing to a working Hermes setup with your first
registry entry installed.

## 1. Install Hermes One (the desktop app)

The `hermesone` npm package installs and updates the Hermes One desktop app. It
detects your OS/arch, downloads the matching release, verifies its sha512
checksum, and installs it.

```bash
npm install -g hermesone     # exposes the `hermesone` command
hermesone install            # download + verify + launch the installer
```

Prefer to preview first? `hermesone plan` prints the release, asset, size, and
expected checksum without changing anything. See the **[CLI reference](cli.md)**
for pinning a version and platform behavior.

> The desktop app and the Hermes Python agent share a data directory at
> `~/.hermes` (`%LOCALAPPDATA%\hermes` on Windows). Registry entries you install
> land there.

## 2. Browse the registry

Open the registry site and search across every skill, MCP server, agent, and
workflow. Each detail page shows the manifest, docs, install count, and the
exact install command.

## 3. Add your first entry

Every detail page gives you a one-liner:

```bash
hermesone add <type>/<id>
```

For example:

```bash
hermesone add mcp/github           # an MCP server
hermesone add skill/plan           # a skill
hermesone add workflow/pr-triage   # a workflow
hermesone add agent/code-reviewer  # an agent
```

`add` installs the entry into your active Hermes profile and pings the registry
so the entry's public download counter ticks. Where each type lands:

| Type       | Destination                                                   |
| ---------- | ------------------------------------------------------------ |
| `skill`    | `<profile>/skills/<category>/<id>/`                          |
| `mcp`      | a block under `mcp_servers:` in `<profile>/config.yaml`      |
| `workflow` | `<profile>/workflows/<id>/`                                  |
| `agent`    | a cloned Hermes profile named `<id>` (its `AGENT.md` → `SOUL.md`) |

`<profile>` is `~/.hermes` for the default profile, or
`~/.hermes/profiles/<name>` for a named one. Target a specific profile with
`--profile <name>`.

## 4. Use it

Launch Hermes One (or run the Hermes agent). Installed skills, MCP servers, and
workflows are picked up automatically; an installed agent appears as its own
profile.

## Next steps

- **[The registry](registry.md)** — understand the entry types and catalog.
- **[Publishing an entry](publishing.md)** — share your own.
