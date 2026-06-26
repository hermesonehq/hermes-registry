import { Bot } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { BrowseClient } from "@/components/BrowseClient";
import { getEntriesByType } from "@/lib/registry";
import { tagFacets } from "@/lib/facets";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Agents",
  description:
    "Browse named subagent personas with their own prompt, tools, and model.",
};

export default async function AgentsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const sp = await searchParams;
  const entries = getEntriesByType("agent");
  return (
    <div>
      <PageHeader
        title="Agents"
        description="Named subagent personas — each a system prompt (AGENT.md) plus a declared model and tool set the Hermes agent can delegate to."
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/10 text-violet-500">
            <Bot className="h-5 w-5" />
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
