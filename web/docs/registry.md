# The registry

A community package registry for the **Hermes** agent. It indexes installable
extensions — skills, MCP servers, agents, and workflows — plus model catalogs,
that the Hermes Python agent and its Electron desktop companion can discover and
install.

The registry is a **catalog, not a package mirror**. Skills, agents, and
workflows are self-contained (metadata + code live together). MCP entries are a
catalog layer: the manifest points at a pinned, already-published server (with a
`source` link), which the client installs at run time.

## Entry types

| Type         | Folder       | What it is                                               | Format                                          |
| ------------ | ------------ | -------------------------------------------------------- | ----------------------------------------------- |
| **Skill**    | `skills/`    | A task procedure Hermes can follow                       | `SKILL.md` + YAML frontmatter (agentskills.io)  |
| **MCP**      | `mcp/`       | A Model Context Protocol server (tools / resources)      | `manifest.json`                                 |
| **Agent**    | `agents/`    | A named subagent persona (system prompt + tools + model) | `manifest.json` + `AGENT.md`                    |
| **Workflow** | `workflows/` | A multi-step recipe chaining skills / agents / MCPs      | `manifest.json` + `workflow.json`               |
| **Model**    | `models/`    | A provider's model catalog (context, modalities, …)      | `<provider>.json`                               |

Two formats by design:

- **Skills** follow the [agentskills.io](https://agentskills.io) open standard —
  a single `SKILL.md` with frontmatter, nested by `category/skill-name/`, no
  separate manifest. Registry extras (`compatibility`, `funding`) live under
  `metadata.hermes` in the frontmatter.
- **MCPs, agents, and workflows** use the registry's `manifest.json` schema
  (under `schemas/`); the folder is `{type}/{name}`.

## The catalog (`index.json`)

`index.json` is the **generated** catalog — a flat list of every entry with its
`type`, `id`, `path`, version, tags, and `compatibility`. Alongside it,
`categories.json` (taxonomy) and `models.json` (model providers) are generated
too.

- Source of truth: the per-entry folders in the repo.
- Generator: `scripts/build_index.py` (deterministic, sorted output).
- **Never hand-edit** the generated files — CI regenerates them on every change.

Clients never clone the repo. They fetch `index.json`, render the gallery,
check each entry's `compatibility` against the running Hermes/desktop versions,
collect any required config from the entry's schema, and install on demand from
the pinned coordinates in the manifest.

## Compatibility

Each manifest declares the versions it supports:

```json
"compatibility": { "hermes": ">=0.3.0", "desktop": ">=0.6.0" }
```

`hermes` is the Python agent's version range; `desktop` is the Hermes One app's
range. All registry MCPs are supported from Hermes One **0.6** onward.

## This site vs. the catalog

The catalog lives on GitHub and is the single source of truth. This `web/` app
ingests `index.json` / `models.json` / the entry folders into Postgres so it can
record real installs (download counters), serve paginated full-text search, and
scale to many entries — without shipping the whole catalog to the browser. See
the **[API reference](api.md)**.
