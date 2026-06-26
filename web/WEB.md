# Hermes Registry — Web

A Next.js website for browsing the Hermes registry, in the spirit of
[npmjs.com](https://www.npmjs.com): search every skill, MCP server, agent, and
workflow, and open a clean detail page for each.

The site is **read-only over the registry data that already lives in this
repo** — it reads `index.json`, `categories.json`, `models.json`, and the
per-entry folders (`skills/`, `mcp/`, `agents/`, `workflows/`, `models/`)
directly at build time. The registry repo stays the single source of truth; the
website is just a view on top of it.

## Stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- **Tailwind CSS v4** with light/dark themes
- `react-markdown` + `rehype-highlight` for rendering `SKILL.md` / `AGENT.md`
- `gray-matter` for skill frontmatter

## Develop

```bash
npm install
npm run dev      # http://localhost:3000
```

## Build

```bash
npm run build    # statically generates a page for every entry
npm run start    # serve the production build
```

## How it's wired

| Path | What it is |
| --- | --- |
| `src/lib/registry.ts` | Reads the registry JSON + per-entry files from the repo root |
| `src/lib/types.ts` | Types mirroring the registry schema |
| `src/lib/ui.ts` / `facets.ts` | Type metadata, hrefs, tag/category facets |
| `src/app/page.tsx` | Home — hero search, type cards, featured, categories |
| `src/app/{skills,mcp,agents,workflows}/` | List + detail pages per type |
| `src/app/search` | Full-text search across everything |
| `src/app/models/[provider]` | Model catalog per provider |
| `src/app/categories`, `tags` | Taxonomy browsing |
| `src/app/registry-icon/[...path]` | Serves entry icons that live next to the data |
| `src/components/detail/DetailView.tsx` | The shared, type-aware detail page |

Detail pages are pre-rendered with `generateStaticParams`, so each entry gets
its own static HTML page. Because the data is read at build time, regenerating
the catalog (`scripts/build_index.py`) and rebuilding the site keeps the two in
sync automatically.
