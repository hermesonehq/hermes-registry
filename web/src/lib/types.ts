export type EntryType = "skill" | "mcp" | "agent" | "workflow";

export interface Compatibility {
  hermes?: string;
  desktop?: string;
}

/** An entry as it appears in the generated index.json catalog. */
export interface RegistryEntry {
  id: string;
  type: EntryType;
  category: string | null;
  name: string;
  version: string;
  description: string;
  tags: string[];
  author: string;
  license?: string | null;
  source?: string | null;
  platforms?: string[];
  path: string;
  icon: string | null;
  checksum?: string;
  compatibility: Compatibility | null;
  acceptsFunding?: boolean;
  /** Live install counter (from Postgres). */
  downloads?: number;
}

export interface CategoryCount {
  name: string;
  count: number;
}

export interface TypeSummary {
  type: EntryType;
  count: number;
  categories: CategoryCount[];
}

/** A resolved author object (manifests use an object; index flattens to a name). */
export interface Author {
  name: string;
  url?: string;
}

export interface Funding {
  address: string;
  token?: string;
  chain?: string;
}

/** The raw manifest.json for mcp / agent / workflow entries. */
export interface Manifest {
  schemaVersion?: string;
  type?: EntryType;
  id?: string;
  name?: string;
  version?: string;
  description?: string;
  author?: Author | string;
  license?: string;
  source?: string;
  tags?: string[];
  icon?: string;
  compatibility?: Compatibility;
  dependencies?: { id: string; version: string }[];
  permissions?: string[];
  funding?: Funding;
  // skill
  entry?: string;
  // agent
  model?: string;
  tools?: string[];
  // mcp
  transport?: "stdio" | "http";
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  configSchema?: ConfigSchema;
  // workflow
  requires?: string[];
}

export interface ConfigSchema {
  type?: string;
  properties?: Record<
    string,
    { type?: string; description?: string; default?: unknown; enum?: unknown[] }
  >;
  required?: string[];
}

export interface WorkflowStep {
  id: string;
  uses: string;
  input?: string;
  with?: Record<string, unknown>;
}

export interface WorkflowDef {
  name?: string;
  description?: string;
  inputs?: Record<string, { type?: string; description?: string }>;
  steps?: WorkflowStep[];
}

/** Everything needed to render a detail page, resolved from disk. */
export interface EntryDetail {
  entry: RegistryEntry;
  manifest: Manifest | null;
  /** Markdown body (SKILL.md / AGENT.md content, frontmatter stripped). */
  markdown: string | null;
  /** Parsed SKILL.md frontmatter, when present. */
  frontmatter: Record<string, unknown> | null;
  workflow: WorkflowDef | null;
  /** Optional README.md from the entry folder. */
  readme: string | null;
}

// ---- Models catalog ----

export interface ModelModalities {
  input?: string[];
  output?: string[];
}

export interface ModelEntry {
  name: string;
  label?: string;
  description?: string;
  context?: number;
  maxOutput?: number;
  modalities?: ModelModalities;
  capabilities?: string[];
}

export interface ModelProvider {
  id: string;
  name: string;
  homepage?: string;
  description?: string;
  docs?: string;
  apiBase?: string;
  envKey?: string;
  models: ModelEntry[];
}

export interface ModelsCatalog {
  schemaVersion?: string;
  generated?: string;
  providerCount?: number;
  modelCount?: number;
  providers: ModelProvider[];
}
