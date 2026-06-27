import "server-only";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { DOCS_NAV } from "./docs-nav";

/** Markdown docs live in `web/docs/`. `process.cwd()` is the app root at runtime
 *  (next.config traces this folder into the standalone build). */
const DOCS_DIR = join(process.cwd(), "docs");

const SLUG_RE = /^[a-z0-9-]+$/;

/** Map a route slug to its file ("" → README.md, "cli" → cli.md). */
function fileFor(slug: string): string | null {
  if (slug === "") return "README.md";
  return SLUG_RE.test(slug) ? `${slug}.md` : null;
}

/**
 * Rewrite intra-docs links so the markdown's relative `*.md` links resolve to
 * `/docs/*` routes: `README.md` → `/docs`, `getting-started.md` → `/docs/getting-started`,
 * preserving any `#anchor`. External/absolute links are left untouched.
 */
export function rewriteDocLinks(md: string): string {
  return md.replace(/\]\((?!https?:|\/|#)([A-Za-z0-9._/-]+?)\.md(#[^)]*)?\)/g, (_m, name, hash) => {
    const anchor = hash ?? "";
    return name === "README" ? `](/docs${anchor})` : `](/docs/${name}${anchor})`;
  });
}

export interface Doc {
  slug: string;
  title: string;
  /** Markdown body with the leading H1 stripped (rendered as the page heading). */
  body: string;
  /** First paragraph, for metadata descriptions. */
  description: string;
}

/** Read and prepare a doc, or null when the slug has no backing file. */
export async function getDoc(slug: string): Promise<Doc | null> {
  const file = fileFor(slug);
  if (!file) return null;
  let raw: string;
  try {
    raw = await readFile(join(DOCS_DIR, file), "utf-8");
  } catch {
    return null;
  }

  const md = rewriteDocLinks(raw);
  const h1 = md.match(/^#\s+(.+?)\s*$/m);
  // Strip inline markdown (backticks, emphasis) so the title is plain text.
  const rawTitle = h1?.[1] ?? DOCS_NAV.find((d) => d.slug === slug)?.title ?? slug;
  const title = rawTitle.replace(/[`*_]/g, "");
  // Drop the first H1 (shown via the page header) and read the first paragraph.
  const body = h1 ? md.replace(h1[0], "").replace(/^\s+/, "") : md;
  const firstPara = body.split(/\n\s*\n/).find((b) => b.trim() && !b.startsWith("#"));
  const description = (firstPara ?? "")
    .replace(/\s+/g, " ")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .trim()
    .slice(0, 160);

  return { slug, title, body, description };
}
