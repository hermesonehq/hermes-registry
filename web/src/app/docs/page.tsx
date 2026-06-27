import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { Markdown } from "@/components/Markdown";
import { getDoc } from "@/lib/docs";

export const dynamic = "force-static";

export const metadata: Metadata = {
  title: "Documentation",
  description:
    "Guides for the Hermes registry — getting started, the CLI, publishing entries, and the API.",
};

export default async function DocsIndexPage() {
  const doc = await getDoc("");
  if (!doc) notFound();
  return (
    <article>
      <h1 className="mb-6 text-3xl font-bold tracking-tight text-default">{doc.title}</h1>
      <Markdown>{doc.body}</Markdown>
    </article>
  );
}
