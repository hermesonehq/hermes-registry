import { Workflow } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesPage, type SortKey } from "@/lib/registry";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Workflows",
  description:
    "Browse multi-step recipes that chain skills, agents, and MCP servers.",
};

type SP = Promise<{
  q?: string;
  tag?: string;
  sort?: string;
  page?: string;
}>;

export default async function WorkflowsPage({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  const query = {
    type: "workflow" as const,
    tag: sp.tag,
    q: sp.q,
    sort: sp.sort as SortKey | undefined,
    page: Number(sp.page) || 1,
  };
  const data = await getEntriesPage(query);

  return (
    <div>
      <PageHeader
        title="Workflows"
        description="Multi-step recipes that chain skills, agents, and MCP servers into a repeatable pipeline with defined inputs and steps."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-default">
            <Workflow className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BrowseClient data={data} query={query} basePath="/workflows" />
      </div>
    </div>
  );
}
