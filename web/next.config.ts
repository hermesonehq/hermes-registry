import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone build for a small Docker runtime image. Registry data is read
  // from Postgres at request time (pages are dynamic), so there are no repo
  // files to trace into the build anymore.
  output: "standalone",
};

export default nextConfig;
