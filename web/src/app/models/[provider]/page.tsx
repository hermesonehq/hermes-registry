import Link from "next/link";
import { notFound } from "next/navigation";
import { ChevronRight, ExternalLink } from "lucide-react";
import { Pill } from "@/components/Badges";
import { CopyButton } from "@/components/CopyButton";
import { getProvider } from "@/lib/registry";
import { formatNumber } from "@/lib/ui";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ provider: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { provider } = await params;
  const p = await getProvider(provider);
  if (!p) return { title: "Not found" };
  return {
    title: `${p.name} — Models`,
    description: p.description ?? `${p.name} model catalog.`,
  };
}

function tokens(n?: number) {
  if (!n) return "—";
  if (n >= 1000) return `${formatNumber(Math.round(n / 1000))}K`;
  return formatNumber(n);
}

export default async function ProviderPage({ params }: Params) {
  const { provider } = await params;
  const p = await getProvider(provider);
  if (!p) notFound();

  const meta: { label: string; value: React.ReactNode }[] = [];
  if (p.apiBase)
    meta.push({
      label: "API base",
      value: <code className="font-mono text-xs">{p.apiBase}</code>,
    });
  if (p.envKey)
    meta.push({
      label: "Env key",
      value: <code className="font-mono text-xs">{p.envKey}</code>,
    });

  return (
    <div>
      <div className="border-b border-default bg-subtle">
        <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
          <nav className="flex items-center gap-1.5 text-sm text-muted">
            <Link href="/" className="hover:text-default">
              Home
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-faint" />
            <Link href="/models" className="hover:text-default">
              Models
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-faint" />
            <span className="text-default">{p.name}</span>
          </nav>
        </div>
      </div>

      <div className="border-b border-default bg-subtle">
        <div className="mx-auto max-w-7xl px-4 pb-8 pt-6 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-default">
              {p.name}
            </h1>
            <span className="rounded-full bg-elevated px-2.5 py-0.5 text-sm font-medium text-muted ring-1 ring-inset ring-default">
              {p.models.length} models
            </span>
          </div>
          {p.description && (
            <p className="mt-2 max-w-2xl text-muted">{p.description}</p>
          )}
          <div className="mt-4 flex flex-wrap gap-3">
            {p.homepage && (
              <a
                href={p.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-default bg-elevated px-3 py-1.5 text-sm font-medium text-default hover:bg-subtle"
              >
                Homepage <ExternalLink className="h-3 w-3 text-faint" />
              </a>
            )}
            {p.docs && (
              <a
                href={p.docs}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-default bg-elevated px-3 py-1.5 text-sm font-medium text-default hover:bg-subtle"
              >
                Docs <ExternalLink className="h-3 w-3 text-faint" />
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {meta.length > 0 && (
          <div className="mb-8 flex flex-wrap gap-x-10 gap-y-2 rounded-xl border border-default bg-subtle px-5 py-4 text-sm">
            {meta.map((m) => (
              <div key={m.label} className="flex items-center gap-2">
                <span className="text-faint">{m.label}</span>
                {m.value}
              </div>
            ))}
          </div>
        )}

        <div className="space-y-4">
          {p.models.map((m) => (
            <div
              key={m.name}
              className="rounded-xl border border-default bg-elevated p-5"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-default">
                      {m.label ?? m.name}
                    </h3>
                  </div>
                  <div className="mt-1 flex items-center gap-1.5">
                    <code className="font-mono text-xs text-muted">
                      {m.name}
                    </code>
                    <CopyButton text={m.name} />
                  </div>
                </div>
                <div className="flex shrink-0 gap-6 text-sm">
                  <div>
                    <div className="text-xs text-faint">Context</div>
                    <div className="font-semibold text-default">
                      {tokens(m.context)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-faint">Max output</div>
                    <div className="font-semibold text-default">
                      {tokens(m.maxOutput)}
                    </div>
                  </div>
                </div>
              </div>

              {m.description && (
                <p className="mt-3 text-sm text-muted">{m.description}</p>
              )}

              <div className="mt-3 flex flex-wrap items-center gap-1.5">
                {m.modalities?.input?.map((x) => (
                  <Pill key={`in-${x}`}>in: {x}</Pill>
                ))}
                {m.modalities?.output?.map((x) => (
                  <Pill key={`out-${x}`}>out: {x}</Pill>
                ))}
                {m.capabilities?.map((c) => (
                  <span
                    key={c}
                    className="rounded-md bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
