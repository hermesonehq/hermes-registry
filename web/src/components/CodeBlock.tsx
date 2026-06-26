import { CopyButton } from "./CopyButton";

export function CodeBlock({
  code,
  language,
  title,
}: {
  code: string;
  language?: string;
  title?: string;
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-default bg-subtle">
      <div className="flex items-center justify-between border-b border-default px-3 py-1.5">
        <span className="font-mono text-[11px] uppercase tracking-wide text-faint">
          {title ?? language ?? "code"}
        </span>
        <CopyButton text={code} label="Copy" />
      </div>
      <pre className="overflow-x-auto p-3.5 text-[13px] leading-relaxed">
        <code className="font-mono text-default">{code}</code>
      </pre>
    </div>
  );
}
