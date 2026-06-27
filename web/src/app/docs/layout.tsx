import Link from "next/link";
import { BookOpen } from "lucide-react";
import { DocsNav } from "@/components/DocsNav";

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="lg:grid lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-10">
        <aside className="mb-8 lg:mb-0">
          <div className="lg:sticky lg:top-24">
            <Link
              href="/docs"
              className="mb-3 flex items-center gap-2 text-sm font-semibold text-default"
            >
              <BookOpen className="h-4 w-4 text-accent" />
              Documentation
            </Link>
            <DocsNav />
          </div>
        </aside>
        <main className="min-w-0">{children}</main>
      </div>
    </div>
  );
}
