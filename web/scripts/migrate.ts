/**
 * Minimal SQL migration runner. Applies every `web/drizzle/*.sql` file once, in
 * filename order, tracking applied files in `schema_migrations`. Hand-rolled
 * (rather than drizzle-kit's journal) so the DDL — including the generated
 * tsvector column — stays plain SQL we control, and runs deterministically in
 * the Docker one-shot. Requires DATABASE_URL.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import postgres from "postgres";

const here = path.dirname(fileURLToPath(import.meta.url));
const MIGRATIONS_DIR = path.resolve(here, "../drizzle");

async function main() {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error("DATABASE_URL is required");

  const sql = postgres(url, { max: 1 });
  try {
    await sql.unsafe(
      `CREATE TABLE IF NOT EXISTS schema_migrations (
         name text PRIMARY KEY,
         applied_at timestamptz NOT NULL DEFAULT now()
       );`
    );

    const files = fs
      .readdirSync(MIGRATIONS_DIR)
      .filter((f) => f.endsWith(".sql"))
      .sort();
    const applied = new Set(
      (await sql<{ name: string }[]>`SELECT name FROM schema_migrations`).map(
        (r) => r.name
      )
    );

    let ran = 0;
    for (const file of files) {
      if (applied.has(file)) {
        console.log(`· skip   ${file}`);
        continue;
      }
      const content = fs.readFileSync(path.join(MIGRATIONS_DIR, file), "utf8");
      await sql.begin(async (tx) => {
        await tx.unsafe(content);
        await tx`INSERT INTO schema_migrations (name) VALUES (${file})`;
      });
      console.log(`✓ apply  ${file}`);
      ran++;
    }
    console.log(`migrations up to date (${ran} applied, ${files.length} total)`);
  } finally {
    await sql.end();
  }
}

main().catch((err) => {
  console.error("migration failed:", err);
  process.exit(1);
});
