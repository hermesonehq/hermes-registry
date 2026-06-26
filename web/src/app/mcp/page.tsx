import { Plug } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesByType } from "@/lib/registry";
import { tagFacets } from "@/lib/facets";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MCP Servers",
  description:
    "Browse Model Context Protocol servers that expose tools and resources to the Hermes agent.",
};

export default async function McpPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const sp = await searchParams;
  const entries = getEntriesByType("mcp");
  return (
    <div>
      <PageHeader
        title="MCP Servers"
        description="Model Context Protocol servers exposing tools and resources. Each manifest points at a pinned, published server the client launches on demand."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/10 text-sky-500">
            <Plug className="h-5 w-5" />
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
