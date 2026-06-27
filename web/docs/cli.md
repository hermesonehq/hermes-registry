# CLI reference (`hermesone`)

The [`hermesone`](https://www.npmjs.com/package/hermesone) npm package does two
things: it installs/updates the **Hermes One desktop app**, and it installs
**registry entries** into your local Hermes setup.

```bash
npm install -g hermesone
```

```
hermesone <command> [args]
```

| Command          | Description                                                                            |
| ---------------- | ------------------------------------------------------------------------------------- |
| `install [tag]`  | Download, verify (sha512), and install Hermes One — latest, or a pinned release tag.  |
| `update [tag]`   | Update Hermes One if a newer release is available.                                    |
| `plan [tag]`     | Show what would be downloaded (tag, asset, size, checksum) — no changes.              |
| `add <type/id>`  | Install a registry entry (skill / mcp / agent / workflow) into Hermes.                |
| `version`        | Print the currently installed Hermes One version.                                     |
| `help`           | Show usage.                                                                           |

## The app installer

```bash
hermesone plan        # preview the release, asset, size, expected checksum
hermesone install     # download + verify sha512 + install/launch
hermesone update      # only if a newer release exists
```

Every download is verified against the base64 sha512 in the release's
electron-builder manifest; a mismatch deletes the file and installs nothing. Pin
a release with a tag or `HERMESONE_VERSION`:

```bash
hermesone install v1.2.3
HERMESONE_VERSION=v1.2.3 hermesone install
```

The installed app version is tracked in `~/.hermesone/state.json`.

## `add` — install a registry entry

```bash
hermesone add mcp/github
hermesone add skill/plan
hermesone add agent/code-reviewer
hermesone add workflow/pr-triage
```

- `<type>` is one of `skill`, `mcp`, `agent`, `workflow`.
- `<id>` is the entry id — usually a single segment (`plan`, `github`), but it
  may be namespaced with `/` (e.g. an `author/name` entry).

What it does:

1. **Resolves** the entry from the registry web API (falling back to the raw
   `index.json` catalog if the API is unreachable).
2. **Installs** it, mirroring the desktop app's model so the Hermes agent picks
   it up:

   | Type       | Destination                                                       |
   | ---------- | ---------------------------------------------------------------- |
   | `skill`    | downloads the entry folder → `<profile>/skills/<category>/<id>/`  |
   | `mcp`      | splices a server block under `mcp_servers:` in `<profile>/config.yaml` |
   | `workflow` | downloads the entry folder → `<profile>/workflows/<id>/`          |
   | `agent`    | runs `hermes profile create <id> --clone`, then writes the agent's `AGENT.md` as the new profile's `SOUL.md` |

3. **Reports** the install to the registry so its public download counter ticks,
   and prints the new count. This call is best-effort — if the registry is
   unreachable the install still succeeds (the count is just omitted).

Installing an **agent** requires the Hermes agent CLI to be present; the command
errors with guidance if it isn't found.

### Flags & env

| Flag / Env                     | Effect                                                                 |
| ------------------------------ | --------------------------------------------------------------------- |
| `--profile <name>`             | Install into a named Hermes profile (default: the active profile).    |
| `-y`, `--yes`                  | Skip the confirmation prompt for `install` (non-interactive).         |
| `HERMES_HOME=<dir>`            | Hermes data directory (default `~/.hermes`; `%LOCALAPPDATA%\hermes` on Windows). |
| `HERMESONE_REGISTRY=<url>`     | Registry web base URL for `add` (default `https://registry.hermesone.org`). |
| `HERMESONE_VERSION=<tag>`      | Pin the desktop release tag for `install`/`update`.                   |
| `HERMESONE_ALLOW_UNVERIFIED=1` | Proceed even with no published checksum (not recommended).            |

Profiles: the default profile is `~/.hermes`; named profiles live under
`~/.hermes/profiles/<name>`. The active profile is read from
`~/.hermes/active_profile`.

## Interactive UX

In a TTY, `install` shows the release/asset/size/checksum, asks to confirm, then
renders a live spinner with a download progress bar. In a non-interactive
context (CI, pipes, agents) it skips the prompt and prints plain status lines.
Honors `NO_COLOR`.

## Programmatic API

```ts
import { add, install, plan, fetchEntry, reportInstall } from "hermesone";

await install();                         // install the desktop app
const res = await add("mcp/github");     // { type, id, name, installedTo, downloads }
```
