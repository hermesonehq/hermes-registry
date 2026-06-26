import { CodeBlock } from "@/components/CodeBlock";
import { Pill } from "@/components/Badges";
import type { Manifest } from "@/lib/types";

export function McpDetails({ manifest }: { manifest: Manifest }) {
  const argsStr = (manifest.args ?? []).join(" ");
  const launch = [manifest.command, argsStr].filter(Boolean).join(" ");
  const props = manifest.configSchema?.properties ?? {};
  const required = new Set(manifest.configSchema?.required ?? []);
  const configKeys = Object.keys(props);

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-3 text-lg font-semibold text-default">
          How it runs
        </h2>
        <p className="mb-4 text-sm text-muted">
          The client launches this pinned, published server on demand
          {manifest.transport ? (
            <>
              {" "}
              over{" "}
              <Pill className="mx-0.5">{manifest.transport}</Pill>
            </>
          ) : null}
          . Required configuration is injected by the user at install time.
        </p>
        {launch && (
          <CodeBlock code={launch} title="launch command" language="bash" />
        )}
      </section>

      {manifest.env && Object.keys(manifest.env).length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-semibold text-default">
            Environment
          </h3>
          <div className="overflow-hidden rounded-lg border border-default">
            <table className="w-full text-sm">
              <tbody className="divide-y divide-[var(--border)]">
                {Object.entries(manifest.env).map(([k, v]) => (
                  <tr key={k}>
                    <td className="bg-subtle px-3 py-2 font-mono text-xs text-default">
                      {k}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs text-muted">
                      {v}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {configKeys.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-default">
            Configuration
          </h2>
          <p className="mb-4 text-sm text-muted">
            Values you supply when installing this server.
          </p>
          <div className="space-y-3">
            {configKeys.map((key) => {
              const prop = props[key];
              return (
                <div
                  key={key}
                  className="rounded-lg border border-default bg-elevated p-3.5"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <code className="font-mono text-sm font-semibold text-default">
                      {key}
                    </code>
                    {prop?.type && (
                      <Pill className="text-[10px]">{prop.type}</Pill>
                    )}
                    {required.has(key) ? (
                      <span className="text-[11px] font-medium text-rose-500">
                        required
                      </span>
                    ) : (
                      <span className="text-[11px] text-faint">optional</span>
                    )}
                  </div>
                  {prop?.description && (
                    <p className="mt-1.5 text-sm text-muted">
                      {prop.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
