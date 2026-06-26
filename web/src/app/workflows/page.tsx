import { Workflow } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesByType } from "@/lib/registry";
import { tagFacets } from "@/lib/facets";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Workflows",
  description:
    "Browse multi-step recipes that chain skills, agents, and MCP servers.",
};

export default async function WorkflowsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const sp = await searchParams;
  const entries = getEntriesByType("workflow");
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
        <BrowseClient
          entries={entries}
          tags={tagFacets(entries)}
          initialQuery={sp.q ?? ""}
        />
      </div>
    </div>
  );
}
