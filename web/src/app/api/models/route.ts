import { getModelsCatalog } from "@/lib/registry";
import { json, corsPreflight } from "@/lib/api";

export const dynamic = "force-dynamic";

export function OPTIONS() {
  return corsPreflight();
}

/** GET /api/models — the full provider + model catalog. */
export async function GET() {
  return json(await getModelsCatalog());
}
