import "server-only";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

/**
 * Singleton postgres.js connection + Drizzle instance. The client connects
 * lazily on first query, so importing this at build time (when DATABASE_URL may
 * be unset and pages are `force-dynamic`) is safe — nothing connects until a
 * request actually runs a query.
 */
const url = process.env.DATABASE_URL;
if (!url && process.env.NODE_ENV === "production") {
  // Don't throw at import (build-time); surface clearly if a query is attempted.
  console.warn("[db] DATABASE_URL is not set — database queries will fail.");
}

const globalForDb = globalThis as unknown as {
  _pgClient?: ReturnType<typeof postgres>;
};

const client =
  globalForDb._pgClient ??
  postgres(url ?? "postgres://localhost:5432/postgres", { max: 10 });

if (process.env.NODE_ENV !== "production") globalForDb._pgClient = client;

export const db = drizzle(client, { schema });
