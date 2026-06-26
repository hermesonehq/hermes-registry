import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { DetailView } from "@/components/detail/DetailView";
import { getEntry, getEntryDetail } from "@/lib/registry";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const entry = await getEntry("agent", id);
  if (!entry) return { title: "Not found" };
  return { title: `${entry.name} — Agent`, description: entry.description };
}

export default async function AgentDetailPage({ params }: Params) {
  const { id } = await params;
  const entry = await getEntry("agent", id);
  if (!entry) notFound();
  return <DetailView detail={await getEntryDetail(entry)} />;
}
