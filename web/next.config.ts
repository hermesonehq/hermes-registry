import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone build for a small Docker runtime image. Registry data is read
  // from Postgres at request time (pages are dynamic), so there are no repo
  // files to trace into the build anymore.
  output: "standalone",
  // The /docs pages read markdown from `web/docs/` at build/runtime; trace that
  // folder into the standalone output so it ships with the server.
  outputFileTracingIncludes: {
    "/docs": ["./docs/**/*"],
    "/docs/[slug]": ["./docs/**/*"],
  },
};

export default nextConfig;
