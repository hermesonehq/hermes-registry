import Link from "next/link";
import { Tags } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { getAllTags } from "@/lib/registry";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tags",
  description: "Browse every tag used across the registry.",
};

export default async function TagsPage() {
  const tags = await getAllTags();
  const max = tags[0]?.count ?? 1;

  // scale font size with usage for a simple tag cloud
  function size(count: number) {
    const ratio = count / max;
    if (ratio > 0.6) return "text-2xl";
    if (ratio > 0.35) return "text-xl";
    if (ratio > 0.18) return "text-lg";
    if (ratio > 0.08) return "text-base";
    return "text-sm";
  }

  return (
    <div>
      <PageHeader
        title="Tags"
        description={`${tags.length} tags used across the registry. Bigger means more entries.`}
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-default">
            <Tags className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-3">
          {tags.map((t) => (
            <Link
              key={t.tag}
              href={`/search?q=${encodeURIComponent(t.tag)}`}
              className={`${size(
                t.count
              )} font-medium text-muted transition-colors hover:text-accent`}
            >
              {t.tag}
              <span className="ml-1 align-super text-xs text-faint">
                {t.count}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
