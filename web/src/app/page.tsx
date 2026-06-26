import Link from "next/link";
import { ArrowRight, Boxes } from "lucide-react";
import { SearchHero } from "@/components/SearchHero";
import { EntryCard } from "@/components/EntryCard";
import {
  getStats,
  getAllEntries,
  getCategories,
  getAllTags,
} from "@/lib/registry";
import { TYPE_ORDER, TYPE_META, formatNumber } from "@/lib/ui";
import type { EntryWithDownloads } from "@/lib/registry";

export const dynamic = "force-dynamic";

function pickFeatured(all: EntryWithDownloads[]) {
  // A stable, mixed selection: prefer entries that have icons & tags.
  const featured: EntryWithDownloads[] = [];
  for (const type of TYPE_ORDER) {
    const ofType = all.filter((e) => e.type === type);
    const withIcon = ofType.filter((e) => e.icon);
    const pool = withIcon.length >= 2 ? withIcon : ofType;
    featured.push(...pool.slice(0, type === "skill" ? 3 : 2));
  }
  return featured.slice(0, 9);
}

export default async function HomePage() {
  const [stats, allEntries, cats, allTags] = await Promise.all([
    getStats(),
    getAllEntries(),
    getCategories(),
    getAllTags(),
  ]);
  const topTags = allTags.slice(0, 8);
  const featured = pickFeatured(allEntries);

  const skillCats = (cats.types.find((t) => t.type === "skill")?.categories ?? [])
    .slice()
    .sort((a, b) => b.count - a.count)
    .slice(0, 12);

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-default bg-subtle">
        <div className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6 lg:px-8 lg:py-28">
          <Link
            href="https://github.com/hermesonehq/hermes-registry"
            className="inline-flex items-center gap-2 rounded-full border border-default bg-elevated px-3 py-1 text-xs font-medium text-muted shadow-sm transition hover:text-default"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
            Free & open · community registry
          </Link>
          <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-bold tracking-tight text-default sm:text-5xl lg:text-6xl">
            The package registry for the{" "}
            <span className="text-amber-500">Hermes</span> ecosystem
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-muted">
            Discover and inspect installable skills, MCP servers, agents, and
            workflows. One clean place to browse everything the Hermes agent and
            its desktop companion can run.
          </p>

          <div className="mt-9">
            <SearchHero suggestions={topTags.slice(0, 5).map((t) => t.tag)} />
          </div>

          <dl className="mx-auto mt-12 grid max-w-2xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-default bg-[var(--border)] sm:grid-cols-4">
            {[
              { label: "Total entries", value: stats.total },
              { label: "Skills", value: stats.byType.skill },
              { label: "MCP servers", value: stats.byType.mcp },
              { label: "Agents + workflows", value: stats.byType.agent + stats.byType.workflow },
            ].map((s) => (
              <div key={s.label} className="bg-elevated px-4 py-5">
                <dt className="text-xs text-faint">{s.label}</dt>
                <dd className="mt-1 text-2xl font-bold text-default">
                  {formatNumber(s.value)}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Type cards */}
        <section className="py-16">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {TYPE_ORDER.map((type) => {
              const meta = TYPE_META[type];
              const Icon = meta.icon;
              return (
                <Link
                  key={type}
                  href={`/${meta.slug}`}
                  className="group relative flex flex-col overflow-hidden rounded-2xl border border-default bg-elevated p-6 transition-all hover:border-strong hover:shadow-md"
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`inline-flex h-11 w-11 items-center justify-center rounded-xl ${meta.badge} ring-1 ring-inset`}
                    >
                      <Icon className="h-5 w-5" />
                    </span>
                    <span className="text-2xl font-bold text-default">
                      {formatNumber(stats.byType[type])}
                    </span>
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-default">
                    {meta.plural}
                  </h3>
                  <p className="mt-1 flex-1 text-sm text-muted">{meta.blurb}</p>
                  <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-accent">
                    Browse
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </Link>
              );
            })}
          </div>
        </section>

        {/* Featured */}
        <section className="pb-16">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-default">
                Explore the collection
              </h2>
              <p className="mt-1 text-sm text-muted">
                A taste of what&apos;s available across every type.
              </p>
            </div>
            <Link
              href="/search"
              className="hidden items-center gap-1 text-sm font-medium text-accent hover:underline sm:inline-flex"
            >
              View all <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {featured.map((e) => (
              <EntryCard key={`${e.type}:${e.id}`} entry={e} />
            ))}
          </div>
        </section>

        {/* Categories */}
        <section className="pb-20">
          <div className="rounded-2xl border border-default bg-subtle p-8">
            <div className="flex items-center gap-2">
              <Boxes className="h-5 w-5 text-accent" />
              <h2 className="text-xl font-bold tracking-tight text-default">
                Browse skills by category
              </h2>
            </div>
            <p className="mt-1 text-sm text-muted">
              {stats.categoryCount} categories spanning the skill library.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {skillCats.map((c) => (
                <Link
                  key={c.name}
                  href={`/skills?category=${encodeURIComponent(c.name)}`}
                  className="inline-flex items-center gap-2 rounded-full border border-default bg-elevated px-3.5 py-1.5 text-sm text-muted transition hover:border-strong hover:text-default"
                >
                  {c.name}
                  <span className="rounded-full bg-subtle px-1.5 text-xs text-faint">
                    {c.count}
                  </span>
                </Link>
              ))}
              <Link
                href="/categories"
                className="inline-flex items-center gap-1 rounded-full px-3.5 py-1.5 text-sm font-medium text-accent hover:underline"
              >
                All categories <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
