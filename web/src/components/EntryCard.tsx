import Link from "next/link";
import { Download } from "lucide-react";
import { entryHref, formatNumber } from "@/lib/ui";
import { EntryIcon } from "./EntryIcon";
import { TypeBadge, Tag } from "./Badges";
import type { EntryType } from "@/lib/types";

export interface EntryCardData {
  id: string;
  type: EntryType;
  name: string;
  description: string;
  tags: string[];
  author: string;
  category: string | null;
  icon: string | null;
  iconify?: string | null;
  version?: string;
  downloads?: number;
}

export function EntryCard({
  entry,
  showType = true,
}: {
  entry: EntryCardData;
  showType?: boolean;
}) {
  return (
    <Link
      href={entryHref(entry.type, entry.id)}
      className="group flex flex-col rounded-xl border border-default bg-elevated p-4 transition-all hover:border-strong hover:shadow-md focus:outline-none focus:ring-2 focus:ring-amber-500/40"
    >
      <div className="flex items-start gap-3">
        <EntryIcon
          icon={entry.icon}
          iconify={entry.iconify}
          name={entry.name}
          type={entry.type}
          size="sm"
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-semibold text-default group-hover:text-accent">
              {entry.name}
            </h3>
            {entry.version && (
              <span className="shrink-0 font-mono text-[11px] text-faint">
                {entry.version}
              </span>
            )}
          </div>
          <p className="truncate text-xs text-faint">
            {entry.author}
            {entry.category ? ` · ${entry.category}` : ""}
          </p>
        </div>
        {showType && <TypeBadge type={entry.type} />}
      </div>

      <p className="mt-3 line-clamp-2 flex-1 text-sm text-muted">
        {entry.description}
      </p>

      <div className="mt-3 flex items-center justify-between gap-2">
        {entry.tags?.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {entry.tags.slice(0, 3).map((t) => (
              <Tag key={t} tag={t} />
            ))}
          </div>
        ) : (
          <span />
        )}
        <span
          className="inline-flex shrink-0 items-center gap-1 text-xs text-faint"
          title={`${formatNumber(entry.downloads ?? 0)} installs`}
        >
          <Download className="h-3 w-3" />
          {formatNumber(entry.downloads ?? 0)}
        </span>
      </div>
    </Link>
  );
}
