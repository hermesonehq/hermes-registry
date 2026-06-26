import "server-only";
import fs from "node:fs";
import path from "node:path";
import { cache } from "react";
import matter from "gray-matter";
import type {
  RegistryEntry,
  EntryType,
  TypeSummary,
  EntryDetail,
  Manifest,
  WorkflowDef,
  ModelsCatalog,
  ModelProvider,
} from "./types";

/**
 * The registry data (index.json, categories.json, models.json and the per-entry
 * folders) lives at the repository root. The Next.js project lives in the `web/`
 * subfolder, so the data root is one level up from process.cwd(). It can be
 * overridden with REGISTRY_ROOT when the site is run from elsewhere.
 */
const ROOT = process.env.REGISTRY_ROOT
  ? path.resolve(process.env.REGISTRY_ROOT)
  : path.resolve(process.cwd(), "..");

function readJSON<T>(rel: string): T {
  const file = path.join(ROOT, rel);
  return JSON.parse(fs.readFileSync(file, "utf8")) as T;
}

interface IndexFile {
  schemaVersion: string;
  generated: string;
  count: number;
  entries: RegistryEntry[];
}

interface CategoriesFile {
  schemaVersion: string;
  generated: string;
  types: TypeSummary[];
}

export const getIndex = cache((): IndexFile => readJSON<IndexFile>("index.json"));

export const getAllEntries = cache((): RegistryEntry[] => {
  const entries = getIndex().entries;
  return [...entries].sort((a, b) => a.name.localeCompare(b.name));
});

export const getCategories = cache(
  (): CategoriesFile => readJSON<CategoriesFile>("categories.json")
);

export const getModelsCatalog = cache((): ModelsCatalog =>
  readJSON<ModelsCatalog>("models.json")
);

export function getEntriesByType(type: EntryType): RegistryEntry[] {
  return getAllEntries().filter((e) => e.type === type);
}

export function getEntry(
  type: EntryType,
  id: string
): RegistryEntry | undefined {
  return getAllEntries().find((e) => e.type === type && e.id === id);
}

export function getTypeSummary(type: EntryType): TypeSummary | undefined {
  return getCategories().types.find((t) => t.type === type);
}

export interface RegistryStats {
  total: number;
  byType: Record<EntryType, number>;
  categoryCount: number;
  generated: string;
}

export const getStats = cache((): RegistryStats => {
  const cats = getCategories();
  const byType = {} as Record<EntryType, number>;
  let categoryCount = 0;
  for (const t of cats.types) {
    byType[t.type] = t.count;
    categoryCount += t.categories.length;
  }
  return {
    total: getIndex().count,
    byType,
    categoryCount,
    generated: cats.generated,
  };
});

function safeRead(rel: string): string | null {
  try {
    return fs.readFileSync(path.join(ROOT, rel), "utf8");
  } catch {
    return null;
  }
}

function readManifest(entryPath: string): Manifest | null {
  const raw = safeRead(path.join(entryPath, "manifest.json"));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Manifest;
  } catch {
    return null;
  }
}

/** Resolve everything required to render a detail page for an entry. */
export function getEntryDetail(entry: RegistryEntry): EntryDetail {
  const detail: EntryDetail = {
    entry,
    manifest: null,
    markdown: null,
    frontmatter: null,
    workflow: null,
    readme: safeRead(path.join(entry.path, "README.md")),
  };

  if (entry.type === "skill") {
    const raw = safeRead(path.join(entry.path, "SKILL.md"));
    if (raw) {
      const parsed = matter(raw);
      detail.markdown = parsed.content.trim();
      detail.frontmatter = parsed.data as Record<string, unknown>;
    }
    return detail;
  }

  detail.manifest = readManifest(entry.path);

  if (entry.type === "agent") {
    const raw = safeRead(path.join(entry.path, detail.manifest?.entry ?? "AGENT.md"));
    if (raw) detail.markdown = matter(raw).content.trim();
  }

  if (entry.type === "workflow") {
    const raw = safeRead(
      path.join(entry.path, detail.manifest?.entry ?? "workflow.json")
    );
    if (raw) {
      try {
        detail.workflow = JSON.parse(raw) as WorkflowDef;
      } catch {
        /* ignore malformed workflow.json */
      }
    }
  }

  return detail;
}

export function getProvider(id: string): ModelProvider | undefined {
  return getModelsCatalog().providers.find((p) => p.id === id);
}

/** A trimmed entry shape passed to client-side search. */
export interface SearchDoc {
  id: string;
  type: EntryType;
  name: string;
  description: string;
  tags: string[];
  category: string | null;
  author: string;
  icon: string | null;
}

export const getSearchDocs = cache((): SearchDoc[] =>
  getAllEntries().map((e) => ({
    id: e.id,
    type: e.type,
    name: e.name,
    description: e.description,
    tags: e.tags,
    category: e.category,
    author: e.author,
    icon: e.icon,
  }))
);

/** Aggregate every distinct tag with a usage count, most-used first. */
export const getAllTags = cache((): { tag: string; count: number }[] => {
  const counts = new Map<string, number>();
  for (const e of getAllEntries()) {
    for (const t of e.tags ?? []) {
      counts.set(t, (counts.get(t) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));
});
