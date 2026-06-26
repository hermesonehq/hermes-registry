import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The registry data (skills/, mcp/, agents/, workflows/, models/, *.json) lives
  // at the repo root and is read at build time via the Node fs API in src/lib.
  // Allow those reads to be traced into the standalone build output.
  outputFileTracingIncludes: {
    "/**": [
      "./index.json",
      "./categories.json",
      "./models.json",
      "./skills/**/*",
      "./mcp/**/*",
      "./agents/**/*",
      "./workflows/**/*",
      "./models/**/*",
    ],
  },
};

export default nextConfig;
