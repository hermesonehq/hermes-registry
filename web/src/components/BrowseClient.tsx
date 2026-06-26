"use client";

import { useMemo, useState } from "react";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { EntryCard, type EntryCardData } from "./EntryCard";
import { TypeBadge } from "./Badges";
import { TYPE_ORDER, TYPE_META } from "@/lib/ui";
import type { EntryType } from "@/lib/types";

type SortKey = "relevance" | "name" | "type";

export interface BrowseFacet {
  name: string;
  count: number;
}

export function BrowseClient({
  entries,
  categories,
  tags,
  enableTypeFilter = false,
  initialQuery = "",
  initialCategory = "",
  initialType = "",
}: {
  entries: EntryCardData[];
  categories?: BrowseFacet[];
  tags?: BrowseFacet[];
  enableTypeFilter?: boolean;
  initialQuery?: string;
  initialCategory?: string;
  initialType?: string;
}) {
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState(initialCategory);
  const [activeType, setActiveType] = useState<string>(initialType);
  const [activeTags, setActiveTags] = useState<string[]>([]);
  const [sort, setSort] = useState<SortKey>("name");
  const [showFilters, setShowFilters] = useState(false);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = entries.filter((e) => {
      if (activeType && e.type !== activeType) return false;
      if (category && e.category !== category) return false;
      if (activeTags.length && !activeTags.every((t) => e.tags?.includes(t)))
        return false;
      if (!q) return true;
      const hay = `${e.name} ${e.description} ${e.author} ${(
        e.tags ?? []
      ).join(" ")} ${e.category ?? ""}`.toLowerCase();
      return hay.includes(q);
    });

    if (sort === "name") {
      list = [...list].sort((a, b) => a.name.localeCompare(b.name));
    } else if (sort === "type") {
      list = [...list].sort(
        (a, b) =>
          TYPE_ORDER.indexOf(a.type) - TYPE_ORDER.indexOf(b.type) ||
          a.name.localeCompare(b.name)
      );
    } else if (q) {
      // relevance: name matches first
      list = [...list].sort((a, b) => {
        const an = a.name.toLowerCase().includes(q) ? 0 : 1;
        const bn = b.name.toLowerCase().includes(q) ? 0 : 1;
        return an - bn || a.name.localeCompare(b.name);
      });
    }
    return list;
  }, [entries, query, category, activeType, activeTags, sort]);

  function toggleTag(tag: string) {
    setActiveTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  }

  const hasFilters =
    Boolean(query || category || activeType || activeTags.length);

  function clearAll() {
    setQuery("");
    setCategory("");
    setActiveType("");
    setActiveTags([]);
  }

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      {/* Sidebar */}
      <aside
        className={`${
          showFilters ? "block" : "hidden"
        } shrink-0 lg:block lg:w-64`}
      >
        <div className="space-y-6 lg:sticky lg:top-24">
          {enableTypeFilter && (
            <FacetGroup title="Type">
              <button
                onClick={() => setActiveType("")}
                className={facetBtn(!activeType)}
              >
                All types
                <span className="text-faint">{entries.length}</span>
              </button>
              {TYPE_ORDER.map((t) => {
                const count = entries.filter((e) => e.type === t).length;
                if (!count) return null;
                return (
                  <button
                    key={t}
                    onClick={() => setActiveType(activeType === t ? "" : t)}
                    className={facetBtn(activeType === t)}
                  >
                    {TYPE_META[t].plural}
                    <span className="text-faint">{count}</span>
                  </button>
                );
              })}
            </FacetGroup>
          )}

          {categories && categories.length > 0 && (
            <FacetGroup title="Category">
              <button
                onClick={() => setCategory("")}
                className={facetBtn(!category)}
              >
                All categories
                <span className="text-faint">{entries.length}</span>
              </button>
              <div className="max-h-72 overflow-y-auto pr-1">
                {categories.map((c) => (
                  <button
                    key={c.name}
                    onClick={() =>
                      setCategory(category === c.name ? "" : c.name)
                    }
                    className={facetBtn(category === c.name)}
                  >
                    <span className="truncate">{c.name}</span>
                    <span className="text-faint">{c.count}</span>
                  </button>
                ))}
              </div>
            </FacetGroup>
          )}

          {tags && tags.length > 0 && (
            <FacetGroup title="Popular tags">
              <div className="flex flex-wrap gap-1.5">
                {tags.map((t) => (
                  <button
                    key={t.name}
                    onClick={() => toggleTag(t.name)}
                    className={`rounded-md px-2 py-0.5 text-xs ring-1 ring-inset transition ${
                      activeTags.includes(t.name)
                        ? "bg-[var(--text)] text-[var(--bg)] ring-[var(--text)]"
                        : "bg-subtle text-muted ring-default hover:text-default"
                    }`}
                  >
                    {t.name}
                  </button>
                ))}
              </div>
            </FacetGroup>
          )}
        </div>
      </aside>

      {/* Main */}
      <div className="min-w-0 flex-1">
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter results…"
              className="w-full rounded-lg border border-default bg-elevated py-2.5 pl-10 pr-3 text-sm outline-none focus:border-strong focus:ring-2 focus:ring-amber-500/20"
            />
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters((v) => !v)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-default px-3 py-2.5 text-sm text-muted lg:hidden"
            >
              <SlidersHorizontal className="h-4 w-4" />
              Filters
            </button>
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortKey)}
              className="rounded-lg border border-default bg-elevated px-3 py-2.5 text-sm text-muted outline-none focus:border-strong"
            >
              <option value="name">Sort: Name</option>
              <option value="type">Sort: Type</option>
              {query && <option value="relevance">Sort: Relevance</option>}
            </select>
          </div>
        </div>

        <div className="mb-4 flex items-center justify-between text-sm">
          <p className="text-muted">
            <span className="font-semibold text-default">
              {results.length}
            </span>{" "}
            result{results.length === 1 ? "" : "s"}
          </p>
          {hasFilters && (
            <button
              onClick={clearAll}
              className="inline-flex items-center gap-1 text-muted hover:text-default"
            >
              <X className="h-3.5 w-3.5" /> Clear filters
            </button>
          )}
        </div>

        {(activeType || category || activeTags.length > 0) && (
          <div className="mb-4 flex flex-wrap items-center gap-2">
            {activeType && (
              <Chip onClear={() => setActiveType("")}>
                <TypeBadge type={activeType as EntryType} />
              </Chip>
            )}
            {category && (
              <Chip onClear={() => setCategory("")}>{category}</Chip>
            )}
            {activeTags.map((t) => (
              <Chip key={t} onClear={() => toggleTag(t)}>
                #{t}
              </Chip>
            ))}
          </div>
        )}

        {results.length === 0 ? (
          <div className="rounded-xl border border-dashed border-default py-20 text-center">
            <p className="text-sm text-muted">
              No entries match your filters.
            </p>
            {hasFilters && (
              <button
                onClick={clearAll}
                className="mt-3 text-sm font-medium text-accent hover:underline"
              >
                Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {results.map((e) => (
              <EntryCard
                key={`${e.type}:${e.id}`}
                entry={e}
                showType={enableTypeFilter || !activeType}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function facetBtn(active: boolean) {
  return `flex w-full items-center justify-between gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition ${
    active
      ? "bg-accent-soft font-medium text-accent"
      : "text-muted hover:bg-subtle hover:text-default"
  }`;
}

function FacetGroup({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="mb-2 px-2.5 text-xs font-semibold uppercase tracking-wider text-faint">
        {title}
      </h3>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}

function Chip({
  children,
  onClear,
}: {
  children: React.ReactNode;
  onClear: () => void;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-default bg-subtle px-2.5 py-1 text-xs text-muted">
      {children}
      <button onClick={onClear} aria-label="Remove filter">
        <X className="h-3 w-3 hover:text-default" />
      </button>
    </span>
  );
}
