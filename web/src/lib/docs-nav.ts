/** Ordered docs navigation. Pure data so both server (page) and client (nav)
 *  modules can import it. Slugs map to `web/docs/<slug>.md` (overview → README.md). */
export interface DocNavItem {
  slug: string;
  title: string;
}

export const DOCS_NAV: DocNavItem[] = [
  { slug: "", title: "Overview" },
  { slug: "getting-started", title: "Getting started" },
  { slug: "registry", title: "The registry" },
  { slug: "cli", title: "CLI reference" },
  { slug: "publishing", title: "Publishing" },
  { slug: "api", title: "API reference" },
];

/** Path for a doc slug ("" → /docs, "cli" → /docs/cli). */
export function docHref(slug: string): string {
  return slug ? `/docs/${slug}` : "/docs";
}
