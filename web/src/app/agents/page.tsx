import { Bot } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesPage, type SortKey } from "@/lib/registry";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Agents",
  description:
    "Browse named subagent personas with their own prompt, tools, and model.",
};

type SP = Promise<{
  q?: string;
  tag?: string;
  sort?: string;
  page?: string;
}>;

export default async function AgentsPage({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  const query = {
    type: "agent" as const,
    tag: sp.tag,
    q: sp.q,
    sort: sp.sort as SortKey | undefined,
    page: Number(sp.page) || 1,
  };
  const data = await getEntriesPage(query);

  return (
    <div>
      <PageHeader
        title="Agents"
        description="Named subagent personas — each a system prompt (AGENT.md) plus a declared model and tool set the Hermes agent can delegate to."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-default">
            <Bot className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BrowseClient data={data} query={query} basePath="/agents" />
      </div>
    </div>
  );
}
