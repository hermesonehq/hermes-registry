import Link from "next/link";
import { entryHref } from "@/lib/ui";
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
  version?: string;
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

      {entry.tags?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {entry.tags.slice(0, 4).map((t) => (
            <Tag key={t} tag={t} />
          ))}
        </div>
      )}
    </Link>
  );
}
