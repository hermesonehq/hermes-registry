import fs from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getAllEntries } from "@/lib/registry";

const ROOT = process.cwd();

const CONTENT_TYPES: Record<string, string> = {
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

/**
 * Serves entry icons that live next to the registry data at the repo root
 * (e.g. `mcp/ableton/icon.svg`). Only paths referenced by a real entry's
 * `icon` field are served, which keeps this from being an arbitrary file read.
 */
export async function GET(
  _req: Request,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await params;
  const rel = segments.join("/");

  const allowed = new Set(
    getAllEntries()
      .map((e) => e.icon)
      .filter((i): i is string => Boolean(i))
  );
  if (!allowed.has(rel)) {
    return new NextResponse("Not found", { status: 404 });
  }

  const abs = path.join(ROOT, rel);
  if (!abs.startsWith(ROOT)) {
    return new NextResponse("Forbidden", { status: 403 });
  }

  let data: Buffer;
  try {
    data = fs.readFileSync(abs);
  } catch {
    return new NextResponse("Not found", { status: 404 });
  }

  const ext = path.extname(abs).toLowerCase();
  return new NextResponse(new Uint8Array(data), {
    headers: {
      "Content-Type": CONTENT_TYPES[ext] ?? "application/octet-stream",
      "Cache-Control": "public, max-age=86400, immutable",
    },
  });
}

export function generateStaticParams() {
  return getAllEntries()
    .map((e) => e.icon)
    .filter((i): i is string => Boolean(i))
    .map((icon) => ({ path: icon.split("/") }));
}
