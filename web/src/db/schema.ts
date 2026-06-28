/**
 * Drizzle table definitions for typed queries. The actual DDL (including the
 * generated `search_tsv` column and GIN/btree indexes) lives in the hand-written
 * SQL migrations under `web/drizzle/` — these definitions must stay in sync with
 * them. No `server-only` import here so the seed/migrate scripts can use it too.
 */
import {
  pgTable,
  text,
  integer,
  boolean,
  jsonb,
  timestamp,
  bigserial,
  primaryKey,
  index,
} from "drizzle-orm/pg-core";

export const entries = pgTable(
  "entries",
  {
    type: text("type").notNull(),
    id: text("id").notNull(),
    name: text("name").notNull(),
    version: text("version").notNull(),
    description: text("description").notNull().default(""),
    category: text("category"),
    tags: text("tags").array().notNull().default([]),
    author: text("author").notNull().default(""),
    license: text("license"),
    source: text("source"),
    platforms: text("platforms").array(),
    path: text("path").notNull(),
    icon: text("icon"),
    iconify: text("iconify"),
    checksum: text("checksum"),
    compatibility: jsonb("compatibility"),
    acceptsFunding: boolean("accepts_funding").notNull().default(false),
    downloads: integer("downloads").notNull().default(0),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    primaryKey({ columns: [t.type, t.id] }),
    index("entries_type_idx").on(t.type),
    index("entries_name_idx").on(t.name),
  ]
);

/** 1:1 with entries; heavy fields loaded only on detail pages / icon route. */
export const entryContent = pgTable(
  "entry_content",
  {
    type: text("type").notNull(),
    id: text("id").notNull(),
    manifest: jsonb("manifest"),
    markdown: text("markdown"),
    frontmatter: jsonb("frontmatter"),
    workflow: jsonb("workflow"),
    readme: text("readme"),
    iconB64: text("icon_b64"),
    iconMime: text("icon_mime"),
  },
  (t) => [primaryKey({ columns: [t.type, t.id] })]
);

export const providers = pgTable("providers", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  homepage: text("homepage"),
  description: text("description"),
  docs: text("docs"),
  apiBase: text("api_base"),
  envKey: text("env_key"),
  icon: text("icon"),
  iconB64: text("icon_b64"),
  iconMime: text("icon_mime"),
  models: jsonb("models").notNull().default([]),
  sortOrder: integer("sort_order").notNull().default(0),
});

/** Append-only install log; the entries.downloads counter is the fast read. */
export const downloadEvents = pgTable(
  "download_events",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    entryType: text("entry_type").notNull(),
    entryId: text("entry_id").notNull(),
    source: text("source").notNull().default("cli"),
    version: text("version"),
    ipHash: text("ip_hash"),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index("download_events_entry_idx").on(t.entryType, t.entryId, t.createdAt)]
);

export type EntryRow = typeof entries.$inferSelect;
export type EntryContentRow = typeof entryContent.$inferSelect;
export type ProviderRow = typeof providers.$inferSelect;
