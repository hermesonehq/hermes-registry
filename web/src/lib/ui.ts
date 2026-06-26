import { Sparkles, Plug, Bot, Workflow, type LucideIcon } from "lucide-react";
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
  /** lucide icon representing the type */
  icon: LucideIcon;
}

// Monochrome by design: every type shares one neutral badge/dot treatment.
// Types are distinguished by their label and icon, not by color.
const MONO_BADGE = "bg-[var(--accent-soft)] text-muted ring-[var(--border)]";
const MONO_DOT = "bg-[var(--text-faint)]";

export const TYPE_META: Record<EntryType, TypeMeta> = {
  skill: {
    type: "skill",
    label: "Skill",
    plural: "Skills",
    slug: "skills",
    blurb: "Task procedures Hermes can follow.",
    badge: MONO_BADGE,
    dot: MONO_DOT,
    icon: Sparkles,
  },
  mcp: {
    type: "mcp",
    label: "MCP",
    plural: "MCP Servers",
    slug: "mcp",
    blurb: "Model Context Protocol servers exposing tools and resources.",
    badge: MONO_BADGE,
    dot: MONO_DOT,
    icon: Plug,
  },
  agent: {
    type: "agent",
    label: "Agent",
    plural: "Agents",
    slug: "agents",
    blurb: "Named subagent personas with their own prompt, tools, and model.",
    badge: MONO_BADGE,
    dot: MONO_DOT,
    icon: Bot,
  },
  workflow: {
    type: "workflow",
    label: "Workflow",
    plural: "Workflows",
    slug: "workflows",
    blurb: "Multi-step recipes chaining skills, agents, and MCPs.",
    badge: MONO_BADGE,
    dot: MONO_DOT,
    icon: Workflow,
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
