import Link from "next/link";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`group inline-flex items-center gap-2.5 ${className}`}
      aria-label="Hermes Registry home"
    >
      <span className="relative inline-flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 text-white shadow-sm ring-1 ring-black/5">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          className="h-5 w-5"
          aria-hidden="true"
        >
          {/* winged-messenger mark */}
          <path
            d="M12 3v18M12 6c-2.4-2-5-2.4-7.5-1.5C6 6 7.8 7.2 9.5 7.5M12 6c2.4-2 5-2.4 7.5-1.5C18 6 16.2 7.2 14.5 7.5"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="12" cy="13.5" r="2" fill="currentColor" />
        </svg>
      </span>
      <span className="text-[15px] font-semibold tracking-tight text-default">
        Hermes
        <span className="text-muted font-normal"> Registry</span>
      </span>
    </Link>
  );
}
