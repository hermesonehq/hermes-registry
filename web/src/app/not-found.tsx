import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[60vh] max-w-lg flex-col items-center justify-center px-4 text-center">
      <p className="text-6xl font-bold text-accent">404</p>
      <h1 className="mt-4 text-2xl font-bold tracking-tight text-default">
        Not found
      </h1>
      <p className="mt-2 text-muted">
        We couldn&apos;t find that registry entry. It may have been renamed or
        removed.
      </p>
      <div className="mt-6 flex gap-3">
        <Link
          href="/"
          className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-[var(--bg)] transition hover:opacity-90"
        >
          Go home
        </Link>
        <Link
          href="/search"
          className="rounded-lg border border-default px-4 py-2 text-sm font-semibold text-default transition hover:bg-subtle"
        >
          Search the registry
        </Link>
      </div>
    </div>
  );
}
