import type { BrowseFacet } from "@/components/BrowseClient";

/** Build a tag → count facet list from a set of entries, most-used first. */
export function tagFacets(
  entries: { tags?: string[] }[],
  limit = 24
): BrowseFacet[] {
  const counts = new Map<string, number>();
  for (const e of entries) {
    for (const t of e.tags ?? []) counts.set(t, (counts.get(t) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .slice(0, limit);
}
