import { Search } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getAllEntries } from "@/lib/registry";
import { tagFacets } from "@/lib/facets";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Search",
  description: "Search across every skill, MCP server, agent, and workflow.",
};

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; type?: string }>;
}) {
  const sp = await searchParams;
  const entries = getAllEntries();
  return (
    <div>
      <PageHeader
        title="Search the registry"
        description="One search across every skill, MCP server, agent, and workflow."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-brand-500/10 text-brand-500">
            <Search className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BrowseClient
          entries={entries}
          tags={tagFacets(entries, 30)}
          enableTypeFilter
          initialQuery={sp.q ?? ""}
          initialType={sp.type ?? ""}
        />
      </div>
    </div>
  );
}
