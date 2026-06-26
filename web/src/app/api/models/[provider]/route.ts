import { getProvider } from "@/lib/registry";
import { json, corsPreflight } from "@/lib/api";

export const dynamic = "force-dynamic";

export function OPTIONS() {
  return corsPreflight();
}

/** GET /api/models/:provider — one provider and its models. */
export async function GET(
  _req: Request,
  { params }: { params: Promise<{ provider: string }> }
) {
  const { provider } = await params;
  const p = await getProvider(provider);
  if (!p) return json({ error: "not_found" }, { status: 404 });
  return json(p);
}
