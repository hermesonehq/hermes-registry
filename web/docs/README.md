# Hermes Registry — Docs

The Hermes registry is a community catalog of installable extensions for the
**Hermes** agent and the **Hermes One** desktop app — skills, MCP servers,
agents, workflows, and model catalogs. This site (the `web/` app) is its
frontend, in the spirit of [npmjs.com](https://www.npmjs.com): browse, search,
and open a detail page for every entry, backed by a public read API and
per-entry install counters.

## Start here

- **[Getting started](getting-started.md)** — install Hermes One, get the
  `hermesone` CLI, and `add` your first entry.
- **[The registry](registry.md)** — what's in it, the entry types, and how the
  catalog (`index.json`) is built.
- **[CLI reference](cli.md)** — every `hermesone` command, including `add`.
- **[Publishing an entry](publishing.md)** — contribute a skill, MCP, agent, or
  workflow.
- **[API reference](api.md)** — the public read API and the download endpoint.

## At a glance

| Type         | Folder       | Format                                  |
| ------------ | ------------ | --------------------------------------- |
| **Skill**    | `skills/`    | `SKILL.md` + frontmatter (agentskills.io) |
| **MCP**      | `mcp/`       | `manifest.json`                         |
| **Agent**    | `agents/`    | `manifest.json` + `AGENT.md`            |
| **Workflow** | `workflows/` | `manifest.json` + `workflow.json`       |
| **Model**    | `models/`    | `<provider>.json`                       |

Everything in the registry is free and open. The catalog is the single source
of truth on GitHub; this site ingests it into Postgres so it can record installs
and serve fast search.
