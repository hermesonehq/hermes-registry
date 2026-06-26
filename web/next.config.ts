import path from "node:path";
import type { NextConfig } from "next";

// The registry data lives at the repo root, one level up from this Next.js
// project in `web/`.
const repoRoot = path.resolve(process.cwd(), "..");

const nextConfig: NextConfig = {
  // The registry data (skills/, mcp/, agents/, workflows/, models/, *.json) is
  // read at build time via the Node fs API in src/lib. Set the file-tracing root
  // to the repo root and include those reads so they trace into a standalone
  // build output.
  outputFileTracingRoot: repoRoot,
  outputFileTracingIncludes: {
    "/**": [
      "../index.json",
      "../categories.json",
      "../models.json",
      "../skills/**/*",
      "../mcp/**/*",
      "../agents/**/*",
      "../workflows/**/*",
      "../models/**/*",
    ],
  },
};

export default nextConfig;
