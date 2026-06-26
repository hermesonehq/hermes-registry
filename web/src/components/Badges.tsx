import Link from "next/link";
import { typeMeta } from "@/lib/ui";
import type { EntryType } from "@/lib/types";

export function TypeBadge({
  type,
  className = "",
}: {
  type: EntryType;
  className?: string;
}) {
  const meta = typeMeta(type);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${meta.badge} ${className}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
      {meta.label}
    </span>
  );
}

export function Tag({ tag, href }: { tag: string; href?: string }) {
  const cls =
    "inline-flex items-center rounded-md bg-subtle px-2 py-0.5 text-xs text-muted ring-1 ring-inset ring-default transition-colors hover:text-default hover:bg-accent-soft";
  if (href) {
    return (
      <Link href={href} className={cls}>
        {tag}
      </Link>
    );
  }
  return <span className={cls}>{tag}</span>;
}

export function Pill({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border border-default bg-subtle px-2 py-0.5 text-xs font-medium text-muted ${className}`}
    >
      {children}
    </span>
  );
}
