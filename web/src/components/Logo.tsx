import Link from "next/link";

/**
 * The mark is `public/images/icon.svg`, a single-color (black) glyph. Rather
 * than recolor the SVG per theme, we paint it with `background-color` through a
 * CSS mask, so it inherits the foreground (black in light mode, white in dark)
 * with no JS and no flash.
 */
const markStyle: React.CSSProperties = {
  WebkitMaskImage: "url(/images/icon.svg)",
  maskImage: "url(/images/icon.svg)",
  WebkitMaskRepeat: "no-repeat",
  maskRepeat: "no-repeat",
  WebkitMaskPosition: "center",
  maskPosition: "center",
  WebkitMaskSize: "contain",
  maskSize: "contain",
  backgroundColor: "var(--text)",
};

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`group inline-flex items-center gap-2.5 ${className}`}
      aria-label="Hermes Registry home"
    >
      <span
        aria-hidden="true"
        className="inline-block h-7 w-7 transition-opacity group-hover:opacity-70"
        style={markStyle}
      />
      <span className="text-[15px] font-semibold tracking-tight text-default">
        Hermes
        <span className="text-muted font-normal"> Registry</span>
      </span>
    </Link>
  );
}
