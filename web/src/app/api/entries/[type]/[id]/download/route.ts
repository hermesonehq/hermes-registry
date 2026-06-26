import { createHash } from "node:crypto";
import { incrementDownload } from "@/lib/registry";
import { json, corsPreflight } from "@/lib/api";
import type { EntryType } from "@/lib/types";

export const dynamic = "force-dynamic";

export function OPTIONS() {
  return corsPreflight();
}

function ipHash(req: Request): string | null {
  const ip =
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    req.headers.get("x-real-ip") ||
    "";
  return ip ? createHash("sha256").update(ip).digest("hex").slice(0, 16) : null;
}

/**
 * POST /api/entries/:type/:id/download — called by the `hermesone` CLI on
 * install. Increments the counter and logs an event. Body (optional):
 * { version?: string, source?: string }.
 */
export async function POST(
  req: Request,
  { params }: { params: Promise<{ type: string; id: string }> }
) {
  const { type, id } = await params;

  let body: { version?: unknown; source?: unknown } = {};
  try {
    body = await req.json();
  } catch {
    /* empty body is fine */
  }

  const downloads = await incrementDownload(type as EntryType, id, {
    source: typeof body.source === "string" ? body.source : "cli",
    version: typeof body.version === "string" ? body.version : null,
    ipHash: ipHash(req),
  });

  if (downloads === null) return json({ error: "not_found" }, { status: 404 });
  return json({ ok: true, type, id, downloads });
}
