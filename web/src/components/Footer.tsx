import Link from "next/link";
import { Logo } from "./Logo";
import { TYPE_ORDER, TYPE_META } from "@/lib/ui";

const REPO = "https://github.com/hermesonehq/hermes-registry";

export function Footer() {
  return (
    <footer className="mt-20 border-t border-default bg-subtle">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-10 md:flex-row md:justify-between">
          <div className="max-w-sm">
            <Logo />
            <p className="mt-4 text-sm text-muted">
              A free and open community package registry for the Hermes agent.
              Browse installable skills, MCP servers, agents, and workflows.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-10 sm:grid-cols-3">
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-faint">
                Browse
              </h3>
              <ul className="mt-3 space-y-2 text-sm">
                {TYPE_ORDER.map((t) => (
                  <li key={t}>
                    <Link
                      href={`/${TYPE_META[t].slug}`}
                      className="text-muted transition-colors hover:text-default"
                    >
                      {TYPE_META[t].plural}
                    </Link>
                  </li>
                ))}
                <li>
                  <Link
                    href="/models"
                    className="text-muted transition-colors hover:text-default"
                  >
                    Models
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-faint">
                Discover
              </h3>
              <ul className="mt-3 space-y-2 text-sm">
                <li>
                  <Link href="/search" className="text-muted hover:text-default">
                    Search
                  </Link>
                </li>
                <li>
                  <Link href="/categories" className="text-muted hover:text-default">
                    Categories
                  </Link>
                </li>
                <li>
                  <Link href="/tags" className="text-muted hover:text-default">
                    Tags
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-faint">
                Project
              </h3>
              <ul className="mt-3 space-y-2 text-sm">
                <li>
                  <a href={REPO} className="text-muted hover:text-default">
                    GitHub
                  </a>
                </li>
                <li>
                  <a
                    href={`${REPO}/blob/main/README.md`}
                    className="text-muted hover:text-default"
                  >
                    Documentation
                  </a>
                </li>
                <li>
                  <a
                    href={`${REPO}#contributing`}
                    className="text-muted hover:text-default"
                  >
                    Contribute
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-default pt-6 text-xs text-faint sm:flex-row">
          <p>
            Everything here is free and open. Built for the Hermes agent and its
            desktop companion.
          </p>
          <p>Catalog generated from the registry index.</p>
        </div>
      </div>
    </footer>
  );
}
