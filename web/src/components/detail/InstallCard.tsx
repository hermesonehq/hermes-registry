import { Download } from "lucide-react";
import { CopyButton } from "@/components/CopyButton";
import type { EntryType } from "@/lib/types";

/** The install reference clients use: `{type}/{id}` (skills use bare id). */
function installRef(type: EntryType, id: string) {
  return type === "skill" ? id : `${type}/${id}`;
}

export function InstallCard({
  type,
  id,
}: {
  type: EntryType;
  id: string;
}) {
  const ref = installRef(type, id);
  const cmd = `hermes add ${ref}`;
  return (
    <div className="rounded-xl border border-default bg-elevated p-4">
      <div className="flex items-center gap-2 text-sm font-semibold text-default">
        <Download className="h-4 w-4 text-accent" />
        Install with Hermes
      </div>
      <div className="mt-3 flex items-center justify-between gap-2 rounded-lg border border-default bg-subtle px-3 py-2 font-mono text-[13px]">
        <span className="truncate text-default">
          <span className="select-none text-faint">$ </span>
          {cmd}
        </span>
        <CopyButton text={cmd} />
      </div>
      <p className="mt-2.5 text-xs text-faint">
        Or browse it in the Hermes desktop gallery and click install.
      </p>
    </div>
  );
}
