import { Plug } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesPage, type SortKey } from "@/lib/registry";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "MCP Servers",
  description:
    "Browse Model Context Protocol servers that expose tools and resources to the Hermes agent.",
};

type SP = Promise<{
  q?: string;
  tag?: string;
  sort?: string;
  page?: string;
}>;

export default async function McpPage({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  const query = {
    type: "mcp" as const,
    tag: sp.tag,
    q: sp.q,
    sort: sp.sort as SortKey | undefined,
    page: Number(sp.page) || 1,
  };
  const data = await getEntriesPage(query);

  return (
    <div>
      <PageHeader
        title="MCP Servers"
        description="Model Context Protocol servers exposing tools and resources. Each manifest points at a pinned, published server the client launches on demand."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-default">
            <Plug className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BrowseClient data={data} query={query} basePath="/mcp" />
      </div>
    </div>
  );
}
