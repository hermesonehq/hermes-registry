"use client";

import { useEffect, useState, useTransition } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  ChevronLeft,
  ChevronRight,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { EntryCard } from "./EntryCard";
import { TypeBadge } from "./Badges";
import { TYPE_ORDER, TYPE_META } from "@/lib/ui";
import type { EntriesPage, BrowseQuery, BrowseFacet } from "@/lib/registry";
import type { EntryType } from "@/lib/types";

/**
 * URL-driven browse: all filtering/sorting/pagination lives in the query string,
 * so the server fetches just one page of results (no whole-catalog payload).
 * Controls update the URL; the server page re-queries and passes fresh `data`.
 */
export function BrowseClient({
  data,
  query,
  basePath,
  enableTypeFilter = false,
}: {
  data: EntriesPage;
  query: BrowseQuery;
  basePath: string;
  enableTypeFilter?: boolean;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const [pending, startTransition] = useTransition();
  const [showFilters, setShowFilters] = useState(false);
  const [term, setTerm] = useState(query.q ?? "");

  // keep the input in sync when navigation changes the q param
  useEffect(() => setTerm(query.q ?? ""), [query.q]);

  function navigate(updates: Record<string, string | null>) {
    const next = new URLSearchParams(params.toString());
    for (const [k, v] of Object.entries(updates)) {
      if (v === null || v === "") next.delete(k);
      else next.set(k, v);
    }
    // any filter change resets to page 1 unless page itself is being set
    if (!("page" in updates)) next.delete("page");
    startTransition(() => router.push(`${basePath}?${next.toString()}`));
  }

  // debounce the search box → ?q
  useEffect(() => {
    const current = query.q ?? "";
    if (term === current) return;
    const id = setTimeout(() => navigate({ q: term || null }), 300);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [term]);

  const toggle = (key: string, value: string) =>
    navigate({ [key]: query[key as keyof BrowseQuery] === value ? null : value });

  const hasFilters = Boolean(
    query.q || query.category || query.tag || query.type
  );
  const clearAll = () =>
    startTransition(() => router.push(basePath));

  const showType = enableTypeFilter;

  return (
    <div className={`flex flex-col gap-6 lg:flex-row ${pending ? "opacity-70" : ""}`}>
      {/* Sidebar */}
      <aside className={`${showFilters ? "block" : "hidden"} shrink-0 lg:block lg:w-64`}>
        <div className="space-y-6 lg:sticky lg:top-24">
          {enableTypeFilter && (
            <FacetGroup title="Type">
              <FacetRow
                active={!query.type}
                label="All types"
                count={data.typeFacets.reduce((a, f) => a + f.count, 0)}
                onClick={() => navigate({ type: null })}
              />
              {TYPE_ORDER.map((t) => {
                const f = data.typeFacets.find((x) => x.type === t);
                if (!f?.count) return null;
                return (
                  <FacetRow
                    key={t}
                    active={query.type === t}
                    label={TYPE_META[t].plural}
                    count={f.count}
                    onClick={() => toggle("type", t)}
                  />
                );
              })}
            </FacetGroup>
          )}

          {data.categoryFacets.length > 0 && (
            <FacetGroup title="Category">
              <div className="max-h-72 overflow-y-auto pr-1">
                {data.categoryFacets.map((c) => (
                  <FacetRow
                    key={c.name}
                    active={query.category === c.name}
                    label={c.name}
                    count={c.count}
                    onClick={() => toggle("category", c.name)}
                  />
                ))}
              </div>
            </FacetGroup>
          )}

          {data.tagFacets.length > 0 && (
            <FacetGroup title="Popular tags">
              <div className="flex flex-wrap gap-1.5">
                {data.tagFacets.map((t) => (
                  <button
                    key={t.name}
                    onClick={() => toggle("tag", t.name)}
                    className={`rounded-md px-2 py-0.5 text-xs transition ${
                      query.tag === t.name
                        ? "bg-[var(--text)] text-[var(--bg)]"
                        : "bg-[var(--chip)] text-muted hover:bg-[var(--chip-hover)] hover:text-default"
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
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              placeholder="Filter results…"
              className="w-full rounded-lg border border-default bg-elevated py-2.5 pl-10 pr-3 text-sm outline-none focus:border-strong focus:ring-2 focus:ring-amber-500/30"
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
              value={query.sort ?? "name"}
              onChange={(e) => navigate({ sort: e.target.value })}
              className="rounded-lg border border-default bg-elevated px-3 py-2.5 text-sm text-muted outline-none focus:border-strong"
            >
              <option value="name">Sort: Name</option>
              <option value="downloads">Sort: Installs</option>
              <option value="type">Sort: Type</option>
              {query.q && <option value="relevance">Sort: Relevance</option>}
            </select>
          </div>
        </div>

        <div className="mb-4 flex items-center justify-between text-sm">
          <p className="text-muted">
            <span className="font-semibold text-default">{data.total}</span>{" "}
            result{data.total === 1 ? "" : "s"}
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

        {(query.type || query.category || query.tag) && (
          <div className="mb-4 flex flex-wrap items-center gap-2">
            {query.type && (
              <Chip onClear={() => navigate({ type: null })}>
                <TypeBadge type={query.type as EntryType} />
              </Chip>
            )}
            {query.category && (
              <Chip onClear={() => navigate({ category: null })}>
                {query.category}
              </Chip>
            )}
            {query.tag && (
              <Chip onClear={() => navigate({ tag: null })}>#{query.tag}</Chip>
            )}
          </div>
        )}

        {data.rows.length === 0 ? (
          <div className="rounded-xl border border-dashed border-default py-20 text-center">
            <p className="text-sm text-muted">No entries match your filters.</p>
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
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {data.rows.map((e) => (
                <EntryCard key={`${e.type}:${e.id}`} entry={e} showType={showType} />
              ))}
            </div>
            {data.pageCount > 1 && (
              <Pagination
                page={data.page}
                pageCount={data.pageCount}
                onPage={(p) => navigate({ page: String(p) })}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

function Pagination({
  page,
  pageCount,
  onPage,
}: {
  page: number;
  pageCount: number;
  onPage: (p: number) => void;
}) {
  return (
    <div className="mt-8 flex items-center justify-center gap-3 text-sm">
      <button
        disabled={page <= 1}
        onClick={() => onPage(page - 1)}
        className="inline-flex items-center gap-1 rounded-lg border border-default px-3 py-1.5 text-muted transition hover:text-default disabled:cursor-not-allowed disabled:opacity-40"
      >
        <ChevronLeft className="h-4 w-4" /> Prev
      </button>
      <span className="text-muted">
        Page <span className="font-semibold text-default">{page}</span> of{" "}
        {pageCount}
      </span>
      <button
        disabled={page >= pageCount}
        onClick={() => onPage(page + 1)}
        className="inline-flex items-center gap-1 rounded-lg border border-default px-3 py-1.5 text-muted transition hover:text-default disabled:cursor-not-allowed disabled:opacity-40"
      >
        Next <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
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

function FacetRow({
  active,
  label,
  count,
  onClick,
}: {
  active: boolean;
  label: string;
  count: number;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center justify-between gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition ${
        active
          ? "bg-accent-soft font-medium text-default"
          : "text-muted hover:bg-subtle hover:text-default"
      }`}
    >
      <span className="truncate">{label}</span>
      <span className="text-faint">{count}</span>
    </button>
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

export type { BrowseFacet };
