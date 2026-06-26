import { Sparkles } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesByType, getTypeSummary } from "@/lib/registry";
import { tagFacets } from "@/lib/facets";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Skills",
  description: "Browse task procedures the Hermes agent can follow.",
};

export default async function SkillsPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string; q?: string }>;
}) {
  const sp = await searchParams;
  const entries = getEntriesByType("skill");
  const summary = getTypeSummary("skill");
  const categories = (summary?.categories ?? [])
    .slice()
    .sort((a, b) => b.count - a.count);

  return (
    <div>
      <PageHeader
        title="Skills"
        description="Self-contained task procedures the Hermes agent can follow — each a single SKILL.md following the agentskills.io open standard."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
            <Sparkles className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BrowseClient
          entries={entries}
          categories={categories}
          tags={tagFacets(entries)}
          initialCategory={sp.category ?? ""}
          initialQuery={sp.q ?? ""}
        />
      </div>
    </div>
  );
}
