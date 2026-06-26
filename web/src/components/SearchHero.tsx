"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Search } from "lucide-react";

export function SearchHero({ suggestions = [] }: { suggestions?: string[] }) {
  const router = useRouter();
  const [q, setQ] = useState("");

  function go(term?: string) {
    const value = (term ?? q).trim();
    router.push(value ? `/search?q=${encodeURIComponent(value)}` : "/search");
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          go();
        }}
        className="relative"
      >
        <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-faint" />
        <input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search 236+ skills, MCPs, agents & workflows…"
          className="w-full rounded-2xl border border-default bg-elevated py-4 pl-12 pr-28 text-base shadow-sm outline-none transition focus:border-strong focus:ring-4 focus:ring-amber-500/20"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[var(--bg)] transition hover:opacity-90"
        >
          Search
        </button>
      </form>

      {suggestions.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-sm">
          <span className="text-faint">Popular:</span>
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => go(s)}
              className="rounded-full border border-default bg-elevated px-3 py-1 text-muted transition hover:border-strong hover:text-default"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
