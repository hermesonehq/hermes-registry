import Link from "next/link";
import { ChevronRight, Download, ExternalLink, Github, Heart } from "lucide-react";
import { EntryIcon } from "@/components/EntryIcon";
import { TypeBadge, Tag, Pill } from "@/components/Badges";
import { Markdown } from "@/components/Markdown";
import { CopyButton } from "@/components/CopyButton";
import { MetaList } from "./MetaList";
import { InstallCard } from "./InstallCard";
import { McpDetails } from "./McpDetails";
import { WorkflowDetails } from "./WorkflowDetails";
import { typeMeta, entryHref, parseRef, formatNumber } from "@/lib/ui";
import type { EntryDetail } from "@/lib/types";

function get(obj: unknown, ...keys: string[]): unknown {
  let cur = obj;
  for (const k of keys) {
    if (cur && typeof cur === "object" && k in cur) {
      cur = (cur as Record<string, unknown>)[k];
    } else {
      return undefined;
    }
  }
  return cur;
}

export function DetailView({ detail }: { detail: EntryDetail }) {
  const { entry, manifest, markdown, frontmatter, workflow } = detail;
  const meta = typeMeta(entry.type);

  const source = entry.source ?? manifest?.source ?? null;
  const license = entry.license ?? manifest?.license ?? null;
  const compat = entry.compatibility ?? manifest?.compatibility ?? null;
  const permissions = manifest?.permissions ?? [];
  const dependencies = manifest?.dependencies ?? [];
  const requires = manifest?.requires ?? [];
  const funding =
    manifest?.funding ??
    (get(frontmatter, "metadata", "hermes", "funding") as
      | { address?: string }
      | undefined);
  const relatedSkills =
    (get(frontmatter, "metadata", "hermes", "related_skills") as
      | string[]
      | undefined) ?? [];
  const platforms =
    entry.platforms ??
    (get(frontmatter, "platforms") as string[] | undefined) ??
    [];

  const detailItems: { label: string; value: React.ReactNode }[] = [
    { label: "Version", value: <span className="font-mono">{entry.version}</span> },
    { label: "Type", value: <TypeBadge type={entry.type} /> },
    {
      label: "Installs",
      value: (
        <span className="inline-flex items-center gap-1">
          <Download className="h-3.5 w-3.5 text-faint" />
          {formatNumber(entry.downloads ?? 0)}
        </span>
      ),
    },
  ];
  if (entry.category)
    detailItems.push({
      label: "Category",
      value: (
        <Link
          href={`/skills?category=${encodeURIComponent(entry.category)}`}
          className="text-accent hover:underline"
        >
          {entry.category}
        </Link>
      ),
    });
  if (license) detailItems.push({ label: "License", value: license });
  detailItems.push({ label: "Author", value: entry.author });
  if (entry.type === "agent" && manifest?.model)
    detailItems.push({
      label: "Model",
      value: <span className="font-mono text-xs">{manifest.model}</span>,
    });
  if (entry.type === "mcp" && manifest?.transport)
    detailItems.push({ label: "Transport", value: manifest.transport });
  if (compat?.hermes)
    detailItems.push({
      label: "Hermes",
      value: <span className="font-mono text-xs">{compat.hermes}</span>,
    });
  if (compat?.desktop)
    detailItems.push({
      label: "Desktop",
      value: <span className="font-mono text-xs">{compat.desktop}</span>,
    });
  if (platforms.length)
    detailItems.push({ label: "Platforms", value: platforms.join(", ") });

  return (
    <div>
      {/* Breadcrumb */}
      <div className="border-b border-default bg-subtle">
        <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
          <nav className="flex items-center gap-1.5 text-sm text-muted">
            <Link href="/" className="hover:text-default">
              Home
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-faint" />
            <Link href={`/${meta.slug}`} className="hover:text-default">
              {meta.plural}
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-faint" />
            <span className="truncate text-default">{entry.name}</span>
          </nav>
        </div>
      </div>

      {/* Header */}
      <div className="border-b border-default bg-subtle">
        <div className="mx-auto max-w-7xl px-4 pb-8 pt-6 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-start">
            <EntryIcon
              icon={entry.icon}
              name={entry.name}
              type={entry.type}
              size="lg"
            />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-bold tracking-tight text-default sm:text-3xl">
                  {entry.name}
                </h1>
                <span className="font-mono text-sm text-faint">
                  v{entry.version}
                </span>
                <TypeBadge type={entry.type} />
              </div>
              <p className="mt-2 max-w-3xl text-muted">{entry.description}</p>
              <div className="mt-4 flex flex-wrap items-center gap-3">
                {source && (
                  <a
                    href={source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-lg border border-default bg-elevated px-3 py-1.5 text-sm font-medium text-default transition hover:bg-subtle"
                  >
                    <Github className="h-4 w-4" />
                    Source
                    <ExternalLink className="h-3 w-3 text-faint" />
                  </a>
                )}
                <span className="inline-flex items-center gap-2 text-sm text-muted">
                  <span className="text-faint">ID</span>
                  <code className="rounded bg-elevated px-1.5 py-0.5 font-mono text-xs text-default ring-1 ring-inset ring-default">
                    {entry.id}
                  </code>
                  <CopyButton text={entry.id} />
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_320px]">
          <div className="min-w-0">
            {entry.type === "mcp" && manifest && (
              <McpDetails manifest={manifest} />
            )}
            {entry.type === "workflow" && workflow && (
              <WorkflowDetails workflow={workflow} />
            )}

            {markdown && (
              <div className={entry.type === "skill" ? "" : "mt-10"}>
                {entry.type === "agent" && (
                  <h2 className="mb-4 text-lg font-semibold text-default">
                    System prompt
                  </h2>
                )}
                <Markdown>{markdown}</Markdown>
              </div>
            )}

            {!markdown && entry.type === "mcp" && !manifest && (
              <p className="text-muted">No manifest details available.</p>
            )}
          </div>

          {/* Sidebar */}
          <aside className="space-y-6 lg:sticky lg:top-24 lg:self-start">
            <InstallCard type={entry.type} id={entry.id} />

            <div className="rounded-xl border border-default bg-elevated p-4">
              <h3 className="mb-1 text-sm font-semibold text-default">
                Details
              </h3>
              <MetaList items={detailItems} />
            </div>

            {entry.type === "agent" && manifest?.tools?.length ? (
              <SidebarSection title="Tools">
                <div className="flex flex-wrap gap-1.5">
                  {manifest.tools.map((t) => (
                    <Pill key={t}>{t}</Pill>
                  ))}
                </div>
              </SidebarSection>
            ) : null}

            {permissions.length > 0 && (
              <SidebarSection title="Permissions">
                <div className="flex flex-wrap gap-1.5">
                  {permissions.map((p) => (
                    <Pill key={p}>{p}</Pill>
                  ))}
                </div>
              </SidebarSection>
            )}

            {entry.tags?.length > 0 && (
              <SidebarSection title="Tags">
                <div className="flex flex-wrap gap-1.5">
                  {entry.tags.map((t) => (
                    <Tag
                      key={t}
                      tag={t}
                      href={`/${meta.slug}?q=${encodeURIComponent(t)}`}
                    />
                  ))}
                </div>
              </SidebarSection>
            )}

            {(dependencies.length > 0 || requires.length > 0) && (
              <SidebarSection title="Requires">
                <ul className="space-y-1.5 text-sm">
                  {dependencies.map((d) => (
                    <RefRow key={d.id} refStr={d.id} suffix={d.version} />
                  ))}
                  {requires.map((r) => (
                    <RefRow key={r} refStr={r} />
                  ))}
                </ul>
              </SidebarSection>
            )}

            {relatedSkills.length > 0 && (
              <SidebarSection title="Related skills">
                <ul className="space-y-1.5 text-sm">
                  {relatedSkills.map((r) => (
                    <li key={r}>
                      <Link
                        href={entryHref("skill", r)}
                        className="font-mono text-xs text-accent hover:underline"
                      >
                        {r}
                      </Link>
                    </li>
                  ))}
                </ul>
              </SidebarSection>
            )}

            {funding?.address && (
              <div className="rounded-xl border border-default bg-elevated p-4">
                <h3 className="flex items-center gap-1.5 text-sm font-semibold text-default">
                  <Heart className="h-4 w-4 text-rose-500" />
                  Support the author
                </h3>
                <p className="mt-1 text-xs text-muted">
                  This author accepts optional tips in H1 on Base.
                </p>
                <div className="mt-2 flex items-center justify-between gap-2 rounded-lg border border-default bg-subtle px-2.5 py-1.5">
                  <code className="truncate font-mono text-xs text-default">
                    {funding.address}
                  </code>
                  <CopyButton text={funding.address} />
                </div>
              </div>
            )}

            {entry.checksum && (
              <p className="break-all px-1 font-mono text-[10px] leading-relaxed text-faint">
                {entry.checksum}
              </p>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}

function SidebarSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-default bg-elevated p-4">
      <h3 className="mb-3 text-sm font-semibold text-default">{title}</h3>
      {children}
    </div>
  );
}

function RefRow({ refStr, suffix }: { refStr: string; suffix?: string }) {
  const parsed = parseRef(refStr);
  return (
    <li className="flex items-center justify-between gap-2">
      {parsed ? (
        <Link
          href={entryHref(parsed.type, parsed.id)}
          className="truncate font-mono text-xs text-accent hover:underline"
        >
          {refStr}
        </Link>
      ) : (
        <span className="truncate font-mono text-xs text-muted">{refStr}</span>
      )}
      {suffix && <span className="shrink-0 text-xs text-faint">{suffix}</span>}
    </li>
  );
}
