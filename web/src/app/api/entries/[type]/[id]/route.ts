import { getEntry, getEntryDetail } from "@/lib/registry";
import { json, corsPreflight } from "@/lib/api";
import type { EntryType } from "@/lib/types";

export const dynamic = "force-dynamic";

export function OPTIONS() {
  return corsPreflight();
}

/** GET /api/entries/:type/:id — entry metadata + resolved detail. */
export async function GET(
  _req: Request,
  { params }: { params: Promise<{ type: string; id: string }> }
) {
  const { type, id } = await params;
  const entry = await getEntry(type as EntryType, id);
  if (!entry) return json({ error: "not_found" }, { status: 404 });

  const detail = await getEntryDetail(entry);
  return json({
    entry,
    manifest: detail.manifest,
    markdown: detail.markdown,
    frontmatter: detail.frontmatter,
    workflow: detail.workflow,
    readme: detail.readme,
  });
}
