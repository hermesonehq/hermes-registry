import { iconUrl, typeMeta } from "@/lib/ui";
import type { EntryType } from "@/lib/types";
import { IconifyGlyph } from "./IconifyGlyph";

const SIZES = {
  sm: "h-9 w-9 text-sm rounded-lg",
  md: "h-12 w-12 text-lg rounded-xl",
  lg: "h-16 w-16 text-2xl rounded-2xl",
} as const;

export function EntryIcon({
  icon,
  iconify,
  type,
  size = "md",
}: {
  icon: string | null;
  iconify?: string | null;
  name: string;
  type: EntryType;
  size?: keyof typeof SIZES;
}) {
  const url = iconUrl(icon);
  const cls = SIZES[size];
  const meta = typeMeta(type);
  const TypeIcon = meta.icon;

  // Named Iconify glyph (skills declaring metadata.hermes.icon). Rendered on the
  // same white tile as brand logos for grid consistency; a dark color keeps the
  // single-color glyph legible in both themes, matching the black logos.
  if (!url && iconify) {
    return (
      <span
        className={`${cls} flex shrink-0 items-center justify-center overflow-hidden border border-default bg-white p-2 text-neutral-800`}
      >
        <IconifyGlyph id={iconify} className="h-full w-full" />
      </span>
    );
  }

  if (url) {
    return (
      // Most registry logos are single-color (black) SVGs; a few are colored.
      // A white tile in BOTH themes keeps every logo legible (black logos
      // disappear on a dark tile).
      <span
        className={`${cls} flex shrink-0 items-center justify-center overflow-hidden border border-default bg-white p-1.5`}
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

  // No logo: fall back to the type's lucide icon, on the same white tile so the
  // whole grid of icons stays visually consistent regardless of type. The icon
  // uses a fixed gray (the tile is white in both themes) to read as a
  // placeholder distinct from the bolder real logos.
  return (
    <span
      className={`${cls} flex shrink-0 items-center justify-center border border-default bg-white text-neutral-400`}
      aria-hidden="true"
    >
      <TypeIcon className="h-1/2 w-1/2" />
    </span>
  );
}
