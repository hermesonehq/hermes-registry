/**
 * Ingest the on-disk registry (index.json + per-entry folders + models.json)
 * into Postgres. Idempotent: re-running upserts everything and NEVER resets the
 * `downloads` counter or `created_at`. Removes entries no longer in index.json.
 *
 * Reads from REGISTRY_ROOT (default `..`, i.e. the repo root relative to web/).
 * Run with: DATABASE_URL=… REGISTRY_ROOT=… tsx scripts/seed.ts
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js";
import { sql } from "drizzle-orm";
import matter from "gray-matter";
import { entries, entryContent, providers } from "../src/db/schema";
import type {
  RegistryEntry,
  Manifest,
  ModelsCatalog,
} from "../src/lib/types";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(
  process.env.REGISTRY_ROOT ?? path.resolve(here, "../..")
);

const MIME: Record<string, string> = {
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

function readText(rel: string): string | null {
  try {
    return fs.readFileSync(path.join(ROOT, rel), "utf8");
  } catch {
    return null;
  }
}

function readJson<T>(rel: string): T {
  return JSON.parse(fs.readFileSync(path.join(ROOT, rel), "utf8")) as T;
}

function readManifest(entryPath: string): Manifest | null {
  const raw = readText(path.join(entryPath, "manifest.json"));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Manifest;
  } catch {
    return null;
  }
}

type ContentRow = {
  type: string;
  id: string;
  manifest: unknown;
  markdown: string | null;
  frontmatter: unknown;
  workflow: unknown;
  readme: string | null;
  iconB64: string | null;
  iconMime: string | null;
};

/** Resolve the per-entry content (mirrors the old fs-based getEntryDetail). */
function buildContent(e: RegistryEntry): ContentRow {
  const row: ContentRow = {
    type: e.type,
    id: e.id,
    manifest: null,
    markdown: null,
    frontmatter: null,
    workflow: null,
    readme: readText(path.join(e.path, "README.md")),
    iconB64: null,
    iconMime: null,
  };

  if (e.icon) {
    try {
      const buf = fs.readFileSync(path.join(ROOT, e.icon));
      row.iconB64 = buf.toString("base64");
      row.iconMime = MIME[path.extname(e.icon).toLowerCase()] ?? "application/octet-stream";
    } catch {
      /* missing icon file — leave null */
    }
  }

  if (e.type === "skill") {
    const raw = readText(path.join(e.path, "SKILL.md"));
    if (raw) {
      const parsed = matter(raw);
      row.markdown = parsed.content.trim();
      row.frontmatter = parsed.data;
    }
    return row;
  }

  const manifest = readManifest(e.path);
  row.manifest = manifest;

  if (e.type === "agent") {
    const raw = readText(path.join(e.path, manifest?.entry ?? "AGENT.md"));
    if (raw) row.markdown = matter(raw).content.trim();
  }

  if (e.type === "workflow") {
    const raw = readText(path.join(e.path, manifest?.entry ?? "workflow.json"));
    if (raw) {
      try {
        row.workflow = JSON.parse(raw);
      } catch {
        /* ignore malformed workflow.json */
      }
    }
  }

  return row;
}

async function main() {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error("DATABASE_URL is required");
  console.log(`[seed] reading registry from ${ROOT}`);

  const index = readJson<{ entries: RegistryEntry[] }>("index.json");
  const models = readJson<ModelsCatalog>("models.json");
  const all = index.entries;

  const client = postgres(url, { max: 1 });
  const db = drizzle(client, { schema: { entries, entryContent, providers } });

  try {
    // --- entries (preserve downloads + created_at on conflict) ---
    const entryRows = all.map((e) => ({
      type: e.type,
      id: e.id,
      name: e.name,
      version: e.version || "0.0.0",
      description: e.description ?? "",
      category: e.category ?? null,
      tags: e.tags ?? [],
      author: e.author ?? "",
      license: e.license ?? null,
      source: e.source ?? null,
      platforms: e.platforms ?? null,
      path: e.path,
      icon: e.icon ?? null,
      checksum: e.checksum ?? null,
      compatibility: e.compatibility ?? null,
      acceptsFunding: Boolean(e.acceptsFunding),
    }));

    await db
      .insert(entries)
      .values(entryRows)
      .onConflictDoUpdate({
        target: [entries.type, entries.id],
        set: {
          name: sql`excluded.name`,
          version: sql`excluded.version`,
          description: sql`excluded.description`,
          category: sql`excluded.category`,
          tags: sql`excluded.tags`,
          author: sql`excluded.author`,
          license: sql`excluded.license`,
          source: sql`excluded.source`,
          platforms: sql`excluded.platforms`,
          path: sql`excluded.path`,
          icon: sql`excluded.icon`,
          checksum: sql`excluded.checksum`,
          compatibility: sql`excluded.compatibility`,
          acceptsFunding: sql`excluded.accepts_funding`,
          updatedAt: sql`now()`,
        },
      });

    // --- entry_content ---
    const contentRows = all.map(buildContent);
    await db
      .insert(entryContent)
      .values(contentRows)
      .onConflictDoUpdate({
        target: [entryContent.type, entryContent.id],
        set: {
          manifest: sql`excluded.manifest`,
          markdown: sql`excluded.markdown`,
          frontmatter: sql`excluded.frontmatter`,
          workflow: sql`excluded.workflow`,
          readme: sql`excluded.readme`,
          iconB64: sql`excluded.icon_b64`,
          iconMime: sql`excluded.icon_mime`,
        },
      });

    // --- providers (models catalog) ---
    const providerRows = (models.providers ?? []).map((p, i) => ({
      id: p.id,
      name: p.name,
      homepage: p.homepage ?? null,
      description: p.description ?? null,
      docs: p.docs ?? null,
      apiBase: p.apiBase ?? null,
      envKey: p.envKey ?? null,
      models: p.models ?? [],
      sortOrder: i,
    }));
    if (providerRows.length) {
      await db
        .insert(providers)
        .values(providerRows)
        .onConflictDoUpdate({
          target: providers.id,
          set: {
            name: sql`excluded.name`,
            homepage: sql`excluded.homepage`,
            description: sql`excluded.description`,
            docs: sql`excluded.docs`,
            apiBase: sql`excluded.api_base`,
            envKey: sql`excluded.env_key`,
            models: sql`excluded.models`,
            sortOrder: sql`excluded.sort_order`,
          },
        });
    }

    // --- prune entries no longer in index.json (cascades to entry_content) ---
    const keys = all.map((e) => `${e.type}/${e.id}`);
    const deletedEntries = await client`
      DELETE FROM entries
      WHERE (type || '/' || id) <> ALL(${keys})
      RETURNING type, id
    `;
    const providerIds = providerRows.map((p) => p.id);
    const deletedProviders = await client`
      DELETE FROM providers
      WHERE id <> ALL(${providerIds})
      RETURNING id
    `;

    console.log(
      `[seed] done — ${entryRows.length} entries, ${providerRows.length} providers` +
        (deletedEntries.length ? `, pruned ${deletedEntries.length} stale entries` : "") +
        (deletedProviders.length ? `, pruned ${deletedProviders.length} stale providers` : "")
    );
  } finally {
    await client.end();
  }
}

main().catch((err) => {
  console.error("[seed] failed:", err);
  process.exit(1);
});
