# Multi-stage build for the Hermes Registry web app.
# Build context is the REPO ROOT (see docker-compose.yml) so the migrator stage
# can copy the registry data (index.json, models.json, per-entry folders) for
# seeding. node:22-slim (glibc) avoids musl/esbuild issues with tsx.
# syntax=docker/dockerfile:1

FROM node:22-slim AS base
WORKDIR /app/web

# --- deps: full install (incl. dev deps; tsx is needed by the seeder) ---
FROM base AS deps
COPY web/package.json web/package-lock.json* ./
RUN npm ci

# --- build: compile the standalone Next.js server ---
FROM base AS build
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/web/node_modules ./node_modules
COPY web/ ./
RUN npm run build

# --- migrator: runs migrations + seed from the registry data, then exits ---
FROM base AS migrator
ENV NODE_ENV=production
ENV REGISTRY_ROOT=/registry
COPY --from=deps /app/web/node_modules ./node_modules
COPY web/ ./
# Registry source of truth, copied in for the one-shot seed.
COPY index.json models.json categories.json /registry/
COPY skills /registry/skills
COPY mcp /registry/mcp
COPY agents /registry/agents
COPY workflows /registry/workflows
CMD ["sh", "-c", "npm run db:migrate && npm run db:seed"]

# --- runner: minimal standalone image ---
FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
COPY --from=build /app/web/.next/standalone ./
COPY --from=build /app/web/.next/static ./.next/static
COPY --from=build /app/web/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
