export function MetaList({
  items,
}: {
  items: { label: string; value: React.ReactNode }[];
}) {
  return (
    <dl className="divide-y divide-[var(--border)] text-sm">
      {items.map((it) => (
        <div
          key={it.label}
          className="flex items-start justify-between gap-4 py-2.5"
        >
          <dt className="shrink-0 text-muted">{it.label}</dt>
          <dd className="text-right font-medium text-default">{it.value}</dd>
        </div>
      ))}
    </dl>
  );
}
