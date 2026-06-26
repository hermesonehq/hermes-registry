# Hermes Registry — Web

A Next.js website for browsing the Hermes registry, in the spirit of
[npmjs.com](https://www.npmjs.com): search every skill, MCP server, agent, and
workflow, and open a clean detail page for each — plus a public read API and
per-entry install counters.

The registry repo stays the single source of truth. A **seed step** ingests
`index.json`, `models.json`, and the per-entry folders (`skills/`, `mcp/`,
`agents/`, `workflows/`) into **Postgres**, which the app then queries at request
time. This lets the site record **downloads** (real `hermesone add` installs),
serve a paginated/full-text search without shipping the whole catalog to the
browser, and scale to many thousands of entries.

## Stack

- **Next.js 15** (App Router, standalone output) + **React 19** + **TypeScript**
- **Postgres** via **Drizzle ORM** (`postgres` driver); Postgres FTS for search
- **Tailwind CSS v4**, monochrome theme (Manrope), light/dark
- `react-markdown` + `rehype-highlight` for `SKILL.md` / `AGENT.md`
- `gray-matter` (skill frontmatter, at seed time)

## Run with Docker (recommended)

```bash
cp .env.example .env        # at the repo root; edit POSTGRES_PASSWORD
docker compose up --build   # db + one-shot migrate/seed + app
# → http://localhost:3000
```

`docker compose` brings up Postgres, runs migrations and the seed once, then
starts the app. Re-running is safe: the seed is idempotent and **never resets
download counters**. After regenerating the catalog
(`scripts/build_index.py`), re-run the `migrate` service to re-seed.

## Develop (without Docker)

```bash
# Postgres reachable at DATABASE_URL:
export DATABASE_URL=postgres://hermes:hermes@localhost:5432/hermes
cd web
npm install
npm run db:setup   # migrate + seed (reads ../ as REGISTRY_ROOT by default)
npm run dev        # http://localhost:3000
```

Scripts: `db:migrate`, `db:seed`, `db:setup` (both).

## Data model (Postgres)

| Table | Purpose |
| --- | --- |
| `entries` (PK `type,id`) | catalog rows + `downloads` counter + `search_tsv` (trigger-maintained FTS vector) |
| `entry_content` | per-entry `manifest` / `markdown` / `frontmatter` / `workflow` / `readme` + icon bytes |
| `providers` | model catalog (models as JSON) |
| `download_events` | append-only install log (the counter is the fast read) |

## How it's wired

| Path | What it is |
| --- | --- |
| `src/db/{schema,client}.ts` | Drizzle schema + connection |
| `drizzle/*.sql`, `scripts/migrate.ts` | hand-written migrations + runner |
| `scripts/seed.ts` | ingest the registry into Postgres (idempotent) |
| `src/lib/registry.ts` | all data access: list/detail/stats/facets, `getEntriesPage`, `incrementDownload` |
| `src/components/BrowseClient.tsx` | URL-driven, server-paginated browse/search UI |
| `src/app/api/**` | public read API + download endpoint (see below) |
| `src/app/registry-icon/[...path]` | serves entry icons from Postgres |
| `src/components/detail/DetailView.tsx` | the shared, type-aware detail page |

Pages are **dynamic server components** that query Postgres per request, so
download counts are always live and new entries appear without a rebuild.

## API

- `GET /api/entries?type=&category=&tag=&q=&sort=&page=&limit=` — paginated list + facets
- `GET /api/entries/:type/:id` — entry metadata + resolved detail
- `POST /api/entries/:type/:id/download` — increment installs (called by the `hermesone` CLI); body `{ version?, source? }`
- `GET /api/models`, `GET /api/models/:provider`

All read endpoints send permissive CORS.
