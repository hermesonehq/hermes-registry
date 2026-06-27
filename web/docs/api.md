# API reference

The registry site exposes a small **public read API** plus a download endpoint
the `hermesone` CLI calls on install. All read endpoints send permissive CORS
(`Access-Control-Allow-Origin: *`), so they're usable from the browser.

Base URL: your deployment (e.g. `https://registry.hermesone.org`).

## Entries

### `GET /api/entries`

Paginated, filtered list with facets.

Query params: `type`, `category`, `tag`, `q` (full-text), `sort`
(`name` | `downloads` | `type` | `relevance`), `page`, `limit` (max 100).

```jsonc
{
  "total": 237,
  "page": 1,
  "limit": 24,
  "pageCount": 10,
  "entries": [ /* entry rows incl. live `downloads` */ ],
  "facets": { "types": [...], "categories": [...], "tags": [...] }
}
```

### `GET /api/entries/:type/:id`

One entry's metadata plus resolved detail.

- `:type` is singular: `skill` | `mcp` | `agent` | `workflow`.
- `:id` is the entry id (URL-encode it if it contains `/`).

```jsonc
{
  "entry": { "type": "mcp", "id": "github", "name": "GitHub", "version": "1.1.0",
             "path": "mcp/github", "category": null, "downloads": 42, "...": "..." },
  "manifest": { /* the entry's manifest.json */ },
  "markdown": "…",     // SKILL.md / AGENT.md when present
  "frontmatter": {},   // skills
  "workflow": null,    // workflows
  "readme": null
}
```

Returns `404 { "error": "not_found" }` for unknown entries.

### `POST /api/entries/:type/:id/download`

Records an install: increments the entry's counter, appends an event, and
returns the new total. Called by `hermesone add`.

Request body (optional):

```json
{ "version": "1.1.0", "source": "cli" }
```

Response:

```json
{ "ok": true, "type": "mcp", "id": "github", "downloads": 43 }
```

`404 { "error": "not_found" }` if the entry doesn't exist. `OPTIONS` is handled
for CORS preflight.

> The `entries.downloads` column is the fast read; every install also appends to
> an append-only `download_events` log (with a hashed IP) for analytics.

## Models

### `GET /api/models`

The full model catalog (providers + their models).

### `GET /api/models/:provider`

One provider's catalog.

## Data flow

The catalog on GitHub is the source of truth. A seed step ingests `index.json`,
`models.json`, and the per-entry folders into Postgres; pages and these
endpoints query Postgres per request, so download counts are always live and new
entries appear without a rebuild. Re-seeding never resets download counters. See
`web/WEB.md` for the data model and deployment.
