import Link from "next/link";
import { Boxes } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { getCategories } from "@/lib/registry";
import { TYPE_META, TYPE_ORDER } from "@/lib/ui";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Categories",
  description: "Browse the registry by category.",
};

export default function CategoriesPage() {
  const cats = getCategories();

  return (
    <div>
      <PageHeader
        title="Categories"
        description="Browse the skill library by category, plus a breakdown of every entry type."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-brand-500/10 text-brand-500">
            <Boxes className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl space-y-12 px-4 py-10 sm:px-6 lg:px-8">
        {cats.types.map((t) => {
          const meta = TYPE_META[t.type] ?? {
            plural: t.type,
            slug: t.type,
          };
          if (t.categories.length === 0) {
            return (
              <section key={t.type}>
                <SectionTitle title={meta.plural} count={t.count} />
                <Link
                  href={`/${meta.slug}`}
                  className="inline-flex rounded-lg border border-default bg-elevated px-4 py-2 text-sm text-muted transition hover:border-strong hover:text-default"
                >
                  Browse all {t.count} {meta.plural.toLowerCase()} →
                </Link>
              </section>
            );
          }
          const sorted = [...t.categories].sort((a, b) => b.count - a.count);
          return (
            <section key={t.type}>
              <SectionTitle title={meta.plural} count={t.count} />
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {sorted.map((c) => (
                  <Link
                    key={c.name}
                    href={`/${meta.slug}?category=${encodeURIComponent(
                      c.name
                    )}`}
                    className="flex items-center justify-between rounded-lg border border-default bg-elevated px-4 py-3 transition hover:border-strong hover:shadow-sm"
                  >
                    <span className="truncate font-medium text-default">
                      {c.name}
                    </span>
                    <span className="ml-2 shrink-0 rounded-full bg-subtle px-2 py-0.5 text-xs text-muted">
                      {c.count}
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          );
        })}

        <p className="text-sm text-muted">
          Looking for something specific? Try{" "}
          <Link href="/search" className="text-accent hover:underline">
            full-text search
          </Link>
          {" "}across all{" "}
          {TYPE_ORDER.map((t) => TYPE_META[t].plural.toLowerCase()).join(", ")}.
        </p>
      </div>
    </div>
  );
}

function SectionTitle({ title, count }: { title: string; count: number }) {
  return (
    <h2 className="mb-4 flex items-center gap-2 text-xl font-bold tracking-tight text-default">
      {title}
      <span className="rounded-full bg-subtle px-2 py-0.5 text-sm font-normal text-muted">
        {count}
      </span>
    </h2>
  );
}
