import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { DetailView } from "@/components/detail/DetailView";
import {
  getEntriesByType,
  getEntry,
  getEntryDetail,
} from "@/lib/registry";

type Params = { params: Promise<{ id: string }> };

export function generateStaticParams() {
  return getEntriesByType("skill").map((e) => ({ id: e.id }));
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const entry = getEntry("skill", id);
  if (!entry) return { title: "Not found" };
  return {
    title: `${entry.name} — Skill`,
    description: entry.description,
  };
}

export default async function SkillDetailPage({ params }: Params) {
  const { id } = await params;
  const entry = getEntry("skill", id);
  if (!entry) notFound();
  return <DetailView detail={getEntryDetail(entry)} />;
}
