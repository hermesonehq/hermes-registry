"use client";

import { Icon, addCollection } from "@iconify/react";
import type { IconifyJSON } from "@iconify/types";
import bundle from "@/generated/icons.json";

// Register the offline, build-time icon subset once. No runtime CDN calls:
// every glyph referenced by the registry ships in src/generated/icons.json
// (produced by scripts/gen-icons.mjs from index.json).
let registered = false;
if (!registered) {
  for (const collection of Object.values(bundle as Record<string, IconifyJSON>)) {
    addCollection(collection);
  }
  registered = true;
}

/** Render an Iconify glyph by id (e.g. "lucide:square-kanban"). */
export function IconifyGlyph({
  id,
  className,
}: {
  id: string;
  className?: string;
}) {
  return <Icon icon={id} className={className} aria-hidden="true" />;
}
