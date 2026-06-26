import "server-only";
import { cache } from "react";
import {
  and,
  asc,
  count,
  countDistinct,
  desc,
  eq,
  isNotNull,
  sql,
  type SQL,
} from "drizzle-orm";
import { db } from "@/db/client";
import { entries, entryContent, providers, downloadEvents } from "@/db/schema";
import type { EntryRow } from "@/db/schema";
import type {
  RegistryEntry,
  EntryType,
  TypeSummary,
  EntryDetail,
  Manifest,
  WorkflowDef,
  ModelsCatalog,
  ModelProvider,
  ModelEntry,
  Compatibility,
} from "./types";
import { TYPE_ORDER } from "./ui";

/** An entry plus its live download counter (what the UI renders). */
export interface EntryWithDownloads extends RegistryEntry {
  downloads: number;
}

function toEntry(r: EntryRow): EntryWithDownloads {
  return {
    id: r.id,
    type: r.type as EntryType,
    category: r.category,
    name: r.name,
    version: r.version,
    description: r.description,
    tags: r.tags ?? [],
    author: r.author,
    license: r.license,
    source: r.source,
    platforms: r.platforms ?? undefined,
    path: r.path,
    icon: r.icon,
    checksum: r.checksum ?? undefined,
    compatibility: (r.compatibility as Compatibility | null) ?? null,
    acceptsFunding: r.acceptsFunding,
    downloads: r.downloads,
  };
}

// ---- Collections -----------------------------------------------------------

export const getAllEntries = cache(async (): Promise<EntryWithDownloads[]> => {
  const rows = await db.select().from(entries).orderBy(asc(entries.name));
  return rows.map(toEntry);
});

export const getEntriesByType = cache(
  async (type: EntryType): Promise<EntryWithDownloads[]> => {
    const rows = await db
      .select()
      .from(entries)
      .where(eq(entries.type, type))
      .orderBy(asc(entries.name));
    return rows.map(toEntry);
  }
);

export const getEntry = cache(
  async (type: EntryType, id: string): Promise<EntryWithDownloads | undefined> => {
    const rows = await db
      .select()
      .from(entries)
      .where(and(eq(entries.type, type), eq(entries.id, id)))
      .limit(1);
    return rows[0] ? toEntry(rows[0]) : undefined;
  }
);

/** Resolve everything needed to render a detail page (joins entry_content). */
export const getEntryDetail = cache(
  async (entry: RegistryEntry): Promise<EntryDetail> => {
    const rows = await db
      .select()
      .from(entryContent)
      .where(
        and(
          eq(entryContent.type, entry.type),
          eq(entryContent.id, entry.id)
        )
      )
      .limit(1);
    const c = rows[0];
    return {
      entry,
      manifest: (c?.manifest as Manifest | null) ?? null,
      markdown: c?.markdown ?? null,
      frontmatter: (c?.frontmatter as Record<string, unknown> | null) ?? null,
      workflow: (c?.workflow as WorkflowDef | null) ?? null,
      readme: c?.readme ?? null,
    };
  }
);

// ---- Stats / facets --------------------------------------------------------

export interface RegistryStats {
  total: number;
  byType: Record<EntryType, number>;
  categoryCount: number;
  generated: string;
}

export const getStats = cache(async (): Promise<RegistryStats> => {
  const typeRows = await db
    .select({ type: entries.type, c: count() })
    .from(entries)
    .groupBy(entries.type);

  const byType = { skill: 0, mcp: 0, agent: 0, workflow: 0 } as Record<
    EntryType,
    number
  >;
  let total = 0;
  for (const r of typeRows) {
    byType[r.type as EntryType] = Number(r.c);
    total += Number(r.c);
  }

  const [{ cc }] = await db
    .select({ cc: countDistinct(entries.category) })
    .from(entries)
    .where(isNotNull(entries.category));

  return { total, byType, categoryCount: Number(cc), generated: new Date().toISOString() };
});

export interface CategoriesFile {
  schemaVersion: string;
  generated: string;
  types: TypeSummary[];
}

export const getCategories = cache(async (): Promise<CategoriesFile> => {
  const typeRows = await db
    .select({ type: entries.type, c: count() })
    .from(entries)
    .groupBy(entries.type);
  const catRows = await db
    .select({ type: entries.type, category: entries.category, c: count() })
    .from(entries)
    .where(isNotNull(entries.category))
    .groupBy(entries.type, entries.category);

  const countOf = new Map(typeRows.map((r) => [r.type, Number(r.c)]));
  const types: TypeSummary[] = TYPE_ORDER.map((type) => ({
    type,
    count: countOf.get(type) ?? 0,
    categories: catRows
      .filter((r) => r.type === type && r.category)
      .map((r) => ({ name: r.category as string, count: Number(r.c) }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name)),
  }));

  return { schemaVersion: "1", generated: new Date().toISOString(), types };
});

export const getTypeSummary = cache(
  async (type: EntryType): Promise<TypeSummary | undefined> => {
    const cats = await getCategories();
    return cats.types.find((t) => t.type === type);
  }
);

export const getAllTags = cache(
  async (): Promise<{ tag: string; count: number }[]> => {
    const rows = (await db.execute(sql`
      SELECT tag, COUNT(*)::int AS count
      FROM (SELECT unnest(tags) AS tag FROM entries) t
      GROUP BY tag
      ORDER BY count DESC, tag ASC
    `)) as unknown as { tag: string; count: number }[];
    return [...rows].map((r) => ({ tag: r.tag, count: Number(r.count) }));
  }
);

// ---- Paginated, filtered browse (server-side) ------------------------------

export type SortKey = "name" | "downloads" | "type" | "relevance";

export interface BrowseFacet {
  name: string;
  count: number;
}

export interface EntriesPage {
  rows: EntryWithDownloads[];
  total: number;
  page: number;
  limit: number;
  pageCount: number;
  typeFacets: { type: EntryType; count: number }[];
  categoryFacets: BrowseFacet[];
  tagFacets: BrowseFacet[];
}

export interface BrowseQuery {
  type?: EntryType | "";
  category?: string;
  tag?: string;
  q?: string;
  page?: number;
  limit?: number;
  sort?: SortKey;
}

const PAGE_SIZE = 24;
const ftsMatch = (q: string): SQL => sql`search_tsv @@ plainto_tsquery('english', ${q})`;

export const getEntriesPage = cache(
  async (opts: BrowseQuery): Promise<EntriesPage> => {
    const page = Math.max(1, opts.page ?? 1);
    const limit = Math.min(100, Math.max(1, opts.limit ?? PAGE_SIZE));
    const q = opts.q?.trim();

    // base = filters shared by every query (q + tag); type/category layered on.
    const base: SQL[] = [];
    if (q) base.push(ftsMatch(q));
    if (opts.tag) base.push(sql`${entries.tags} @> ARRAY[${opts.tag}]::text[]`);

    const withType = [...base];
    if (opts.type) withType.push(eq(entries.type, opts.type));
    const withTypeAndCat = [...withType];
    if (opts.category) withTypeAndCat.push(eq(entries.category, opts.category));

    const whereResults = withTypeAndCat.length ? and(...withTypeAndCat) : undefined;

    // ordering
    let orderBy: SQL[];
    if (opts.sort === "downloads") orderBy = [desc(entries.downloads), asc(entries.name)];
    else if (opts.sort === "type") orderBy = [asc(entries.type), asc(entries.name)];
    else if (opts.sort === "relevance" && q)
      orderBy = [desc(sql`ts_rank(search_tsv, plainto_tsquery('english', ${q}))`), asc(entries.name)];
    else orderBy = [asc(entries.name)];

    const rows = await db
      .select()
      .from(entries)
      .where(whereResults)
      .orderBy(...orderBy)
      .limit(limit)
      .offset((page - 1) * limit);

    const [{ total }] = await db
      .select({ total: count() })
      .from(entries)
      .where(whereResults);

    // facets: type counts ignore the type filter; category counts keep it.
    const typeFacetRows = await db
      .select({ type: entries.type, c: count() })
      .from(entries)
      .where(base.length ? and(...base) : undefined)
      .groupBy(entries.type);
    const categoryFacetRows = await db
      .select({ category: entries.category, c: count() })
      .from(entries)
      .where(and(isNotNull(entries.category), ...(withType.length ? withType : [])))
      .groupBy(entries.category);

    // top tags within the current type (+ q), for the sidebar tag cloud.
    const tagWhere = withType.length
      ? sql`WHERE ${and(...withType)!}`
      : sql``;
    const tagFacetRows = (await db.execute(sql`
      SELECT tag, COUNT(*)::int AS count
      FROM (SELECT unnest(tags) AS tag FROM entries ${tagWhere}) t
      GROUP BY tag ORDER BY count DESC, tag ASC LIMIT 30
    `)) as unknown as { tag: string; count: number }[];

    const total2 = Number(total);
    return {
      rows: rows.map(toEntry),
      total: total2,
      page,
      limit,
      pageCount: Math.max(1, Math.ceil(total2 / limit)),
      typeFacets: typeFacetRows.map((r) => ({
        type: r.type as EntryType,
        count: Number(r.c),
      })),
      categoryFacets: categoryFacetRows
        .filter((r) => r.category)
        .map((r) => ({ name: r.category as string, count: Number(r.c) }))
        .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name)),
      tagFacets: [...tagFacetRows].map((r) => ({
        name: r.tag,
        count: Number(r.count),
      })),
    };
  }
);

// ---- Models ----------------------------------------------------------------

export const getModelsCatalog = cache(async (): Promise<ModelsCatalog> => {
  const rows = await db.select().from(providers).orderBy(asc(providers.sortOrder));
  const list: ModelProvider[] = rows.map((p) => ({
    id: p.id,
    name: p.name,
    homepage: p.homepage ?? undefined,
    description: p.description ?? undefined,
    docs: p.docs ?? undefined,
    apiBase: p.apiBase ?? undefined,
    envKey: p.envKey ?? undefined,
    models: (p.models as ModelEntry[]) ?? [],
  }));
  return {
    schemaVersion: "1",
    generated: new Date().toISOString(),
    providerCount: list.length,
    modelCount: list.reduce((a, p) => a + p.models.length, 0),
    providers: list,
  };
});

export const getProvider = cache(
  async (id: string): Promise<ModelProvider | undefined> => {
    const catalog = await getModelsCatalog();
    return catalog.providers.find((p) => p.id === id);
  }
);

// ---- Icons (served by the registry-icon route) -----------------------------

export const getIcon = cache(
  async (iconPath: string): Promise<{ data: Buffer; mime: string } | null> => {
    const rows = await db
      .select({ b64: entryContent.iconB64, mime: entryContent.iconMime })
      .from(entries)
      .innerJoin(
        entryContent,
        and(eq(entries.type, entryContent.type), eq(entries.id, entryContent.id))
      )
      .where(eq(entries.icon, iconPath))
      .limit(1);
    const r = rows[0];
    if (!r?.b64) return null;
    return {
      data: Buffer.from(r.b64, "base64"),
      mime: r.mime ?? "application/octet-stream",
    };
  }
);

// ---- Writes ----------------------------------------------------------------

/** Increment an entry's install counter and log an event. Returns new count. */
export async function incrementDownload(
  type: EntryType,
  id: string,
  opts: { source?: string; version?: string | null; ipHash?: string | null } = {}
): Promise<number | null> {
  const updated = await db
    .update(entries)
    .set({ downloads: sql`${entries.downloads} + 1` })
    .where(and(eq(entries.type, type), eq(entries.id, id)))
    .returning({ downloads: entries.downloads });
  if (!updated.length) return null;
  await db.insert(downloadEvents).values({
    entryType: type,
    entryId: id,
    source: opts.source ?? "cli",
    version: opts.version ?? null,
    ipHash: opts.ipHash ?? null,
  });
  return updated[0].downloads;
}
