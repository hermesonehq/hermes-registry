import type { EntryType } from "./types";

export interface TypeMeta {
  type: EntryType;
  /** singular label */
  label: string;
  /** plural label */
  plural: string;
  /** route segment */
  slug: string;
  blurb: string;
  /** tailwind classes for the badge */
  badge: string;
  /** accent dot / icon color */
  dot: string;
}

export const TYPE_META: Record<EntryType, TypeMeta> = {
  skill: {
    type: "skill",
    label: "Skill",
    plural: "Skills",
    slug: "skills",
    blurb: "Task procedures Hermes can follow.",
    badge:
      "bg-emerald-50 text-emerald-700 ring-emerald-600/20 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-400/20",
    dot: "bg-emerald-500",
  },
  mcp: {
    type: "mcp",
    label: "MCP",
    plural: "MCP Servers",
    slug: "mcp",
    blurb: "Model Context Protocol servers exposing tools and resources.",
    badge:
      "bg-sky-50 text-sky-700 ring-sky-600/20 dark:bg-sky-500/10 dark:text-sky-300 dark:ring-sky-400/20",
    dot: "bg-sky-500",
  },
  agent: {
    type: "agent",
    label: "Agent",
    plural: "Agents",
    slug: "agents",
    blurb: "Named subagent personas with their own prompt, tools, and model.",
    badge:
      "bg-violet-50 text-violet-700 ring-violet-600/20 dark:bg-violet-500/10 dark:text-violet-300 dark:ring-violet-400/20",
    dot: "bg-violet-500",
  },
  workflow: {
    type: "workflow",
    label: "Workflow",
    plural: "Workflows",
    slug: "workflows",
    blurb: "Multi-step recipes chaining skills, agents, and MCPs.",
    badge:
      "bg-amber-50 text-amber-700 ring-amber-600/20 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-400/20",
    dot: "bg-amber-500",
  },
};

export const TYPE_ORDER: EntryType[] = ["skill", "mcp", "agent", "workflow"];

export function typeMeta(type: EntryType): TypeMeta {
  return TYPE_META[type];
}

/** Detail-page href for an entry. */
export function entryHref(type: EntryType, id: string): string {
  return `/${TYPE_META[type].slug}/${id}`;
}

/** Resolve an index `icon` path (root-relative) to the served URL. */
export function iconUrl(icon: string | null | undefined): string | null {
  if (!icon) return null;
  return `/registry-icon/${icon}`;
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-US").format(n);
}

/**
 * Parse a dependency / requires reference like "agent/debugger" or
 * "skill/systematic-debugging" into a linkable {type, id}. Returns null when
 * the prefix is not a known type.
 */
export function parseRef(
  ref: string
): { type: EntryType; id: string } | null {
  const idx = ref.indexOf("/");
  if (idx === -1) return null;
  const prefix = ref.slice(0, idx);
  const id = ref.slice(idx + 1);
  const match = TYPE_ORDER.find((t) => t === prefix);
  if (!match || !id) return null;
  return { type: match, id };
}
