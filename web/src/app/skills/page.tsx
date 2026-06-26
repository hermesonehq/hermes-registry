import { Sparkles } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesPage, type SortKey } from "@/lib/registry";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Skills",
  description: "Browse task procedures the Hermes agent can follow.",
};

type SP = Promise<{
  q?: string;
  category?: string;
  tag?: string;
  sort?: string;
  page?: string;
}>;

export default async function SkillsPage({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  const query = {
    type: "skill" as const,
    category: sp.category,
    tag: sp.tag,
    q: sp.q,
    sort: sp.sort as SortKey | undefined,
    page: Number(sp.page) || 1,
  };
  const data = await getEntriesPage(query);

  return (
    <div>
      <PageHeader
        title="Skills"
        description="Self-contained task procedures the Hermes agent can follow — each a single SKILL.md following the agentskills.io open standard."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-default">
            <Sparkles className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BrowseClient data={data} query={query} basePath="/skills" />
      </div>
    </div>
  );
}
