import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

/**
 * Renders trusted registry markdown (SKILL.md / AGENT.md bodies). Content comes
 * from the repo itself, so raw HTML is intentionally not enabled.
 */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="prose prose-slate max-w-none dark:prose-invert prose-headings:scroll-mt-24 prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h2:mt-10 prose-h2:border-b prose-h2:border-default prose-h2:pb-2 prose-h3:text-lg prose-a:text-accent prose-a:no-underline hover:prose-a:underline prose-code:rounded prose-code:bg-subtle prose-code:px-1.5 prose-code:py-0.5 prose-code:text-[0.85em] prose-code:font-normal prose-code:before:content-none prose-code:after:content-none prose-pre:rounded-lg prose-pre:border prose-pre:border-default prose-pre:bg-subtle prose-img:rounded-lg">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeHighlight, { detect: true, ignoreMissing: true }]]}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
