import Link from "next/link";
import { ArrowRight, Cpu, ExternalLink } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { getModelsCatalog } from "@/lib/registry";
import { formatNumber } from "@/lib/ui";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Models",
  description:
    "Model providers and their catalogs — context windows, modalities, and capabilities.",
};

export default async function ModelsPage() {
  const catalog = await getModelsCatalog();
  const providers = [...catalog.providers].sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  return (
    <div>
      <PageHeader
        title="Models"
        description={`${formatNumber(
          catalog.modelCount ?? 0
        )} models across ${formatNumber(
          catalog.providerCount ?? providers.length
        )} providers. The model catalog clients use to resolve context windows, modalities, and capabilities.`}
        icon={
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-default">
            <Cpu className="h-5 w-5" />
          </span>
        }
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {providers.map((p) => (
            <div
              key={p.id}
              className="flex flex-col rounded-xl border border-default bg-elevated p-5 transition hover:border-strong hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <Link
                  href={`/models/${p.id}`}
                  className="text-lg font-semibold text-default hover:text-accent"
                >
                  {p.name}
                </Link>
                <span className="rounded-full bg-subtle px-2 py-0.5 text-xs font-medium text-muted">
                  {p.models.length} models
                </span>
              </div>
              {p.description && (
                <p className="mt-2 line-clamp-2 flex-1 text-sm text-muted">
                  {p.description}
                </p>
              )}
              <div className="mt-4 flex items-center justify-between">
                <Link
                  href={`/models/${p.id}`}
                  className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
                >
                  View models <ArrowRight className="h-4 w-4" />
                </Link>
                {p.homepage && (
                  <a
                    href={p.homepage}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-faint hover:text-default"
                    aria-label={`${p.name} homepage`}
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
