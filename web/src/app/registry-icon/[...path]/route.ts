import { NextResponse } from "next/server";
import { getIcon } from "@/lib/registry";

export const dynamic = "force-dynamic";

/**
 * Serves entry icons from Postgres (entry_content.icon_b64). `getIcon` only
 * matches a path that is some entry's `icon` field, so this can't be used to
 * read arbitrary data.
 */
export async function GET(
  _req: Request,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await params;
  const rel = segments.join("/");

  const icon = await getIcon(rel);
  if (!icon) return new NextResponse("Not found", { status: 404 });

  return new NextResponse(new Uint8Array(icon.data), {
    headers: {
      "Content-Type": icon.mime,
      "Cache-Control": "public, max-age=86400, immutable",
    },
  });
}
