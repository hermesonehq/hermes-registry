import Link from "next/link";
import { ArrowDown } from "lucide-react";
import { Pill } from "@/components/Badges";
import { parseRef, entryHref } from "@/lib/ui";
import type { WorkflowDef } from "@/lib/types";

function StepRef({ uses }: { uses: string }) {
  const ref = parseRef(uses);
  if (ref) {
    return (
      <Link
        href={entryHref(ref.type, ref.id)}
        className="font-mono text-xs text-accent hover:underline"
      >
        {uses}
      </Link>
    );
  }
  return <span className="font-mono text-xs text-muted">{uses}</span>;
}

export function WorkflowDetails({ workflow }: { workflow: WorkflowDef }) {
  const inputs = workflow.inputs ?? {};
  const inputKeys = Object.keys(inputs);

  return (
    <div className="space-y-8">
      {inputKeys.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-default">Inputs</h2>
          <div className="space-y-2.5">
            {inputKeys.map((key) => (
              <div
                key={key}
                className="rounded-lg border border-default bg-elevated p-3.5"
              >
                <div className="flex items-center gap-2">
                  <code className="font-mono text-sm font-semibold text-default">
                    {key}
                  </code>
                  {inputs[key]?.type && (
                    <Pill className="text-[10px]">{inputs[key]?.type}</Pill>
                  )}
                </div>
                {inputs[key]?.description && (
                  <p className="mt-1.5 text-sm text-muted">
                    {inputs[key]?.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {workflow.steps && workflow.steps.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-default">
            Steps
            <span className="ml-2 text-sm font-normal text-faint">
              {workflow.steps.length} stages
            </span>
          </h2>
          <ol className="space-y-1">
            {workflow.steps.map((step, i) => (
              <li key={step.id ?? i}>
                <div className="rounded-xl border border-default bg-elevated p-4">
                  <div className="flex items-center gap-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-soft text-xs font-bold text-accent">
                      {i + 1}
                    </span>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-default">
                          {step.id}
                        </span>
                        <span className="text-faint">·</span>
                        <StepRef uses={step.uses} />
                      </div>
                    </div>
                  </div>
                  {step.input && (
                    <p className="mt-2 pl-10 font-mono text-xs text-muted">
                      {step.input}
                    </p>
                  )}
                </div>
                {i < workflow.steps!.length - 1 && (
                  <div className="flex justify-center py-1 text-faint">
                    <ArrowDown className="h-4 w-4" />
                  </div>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
