import { getEntriesPage, type SortKey } from "@/lib/registry";
import { json, corsPreflight } from "@/lib/api";
import type { EntryType } from "@/lib/types";

export const dynamic = "force-dynamic";

export function OPTIONS() {
  return corsPreflight();
}

/** GET /api/entries?type=&category=&tag=&q=&sort=&page=&limit= */
export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const data = await getEntriesPage({
    type: (sp.get("type") as EntryType) || "",
    category: sp.get("category") ?? undefined,
    tag: sp.get("tag") ?? undefined,
    q: sp.get("q") ?? undefined,
    sort: (sp.get("sort") as SortKey) ?? undefined,
    page: Number(sp.get("page")) || 1,
    limit: Number(sp.get("limit")) || undefined,
  });

  return json({
    total: data.total,
    page: data.page,
    limit: data.limit,
    pageCount: data.pageCount,
    entries: data.rows,
    facets: {
      types: data.typeFacets,
      categories: data.categoryFacets,
      tags: data.tagFacets,
    },
  });
}
