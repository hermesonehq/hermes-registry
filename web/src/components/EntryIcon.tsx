import { iconUrl, typeMeta } from "@/lib/ui";
import type { EntryType } from "@/lib/types";

const SIZES = {
  sm: "h-9 w-9 text-sm rounded-lg",
  md: "h-12 w-12 text-lg rounded-xl",
  lg: "h-16 w-16 text-2xl rounded-2xl",
} as const;

export function EntryIcon({
  icon,
  name,
  type,
  size = "md",
}: {
  icon: string | null;
  name: string;
  type: EntryType;
  size?: keyof typeof SIZES;
}) {
  const url = iconUrl(icon);
  const cls = SIZES[size];
  const meta = typeMeta(type);

  if (url) {
    return (
      <span
        className={`${cls} flex shrink-0 items-center justify-center overflow-hidden border border-default bg-app p-1.5`}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={url}
          alt=""
          className="h-full w-full object-contain"
          loading="lazy"
        />
      </span>
    );
  }

  const letter = (name?.[0] ?? "?").toUpperCase();
  return (
    <span
      className={`${cls} relative flex shrink-0 items-center justify-center border border-default bg-subtle font-semibold text-muted`}
      aria-hidden="true"
    >
      {letter}
      <span
        className={`absolute bottom-1 right-1 h-1.5 w-1.5 rounded-full ${meta.dot}`}
      />
    </span>
  );
}
