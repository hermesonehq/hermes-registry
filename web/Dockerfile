# Single self-contained image for the Hermes Registry web app.
# Build context is the REPO ROOT (CI sets this) so the registry data can be
# baked in for seeding. The image both serves the app AND can run migrate/seed
# on startup (see docker-entrypoint.sh), so docker-compose only needs db + app.
# syntax=docker/dockerfile:1

FROM node:22-slim AS base
WORKDIR /app/web

# --- deps: full install (dev deps included; tsx runs the seeder) ---
FROM base AS deps
COPY web/package.json web/package-lock.json* ./
RUN npm ci

# --- build: compile .next ---
FROM base AS build
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/web/node_modules ./node_modules
COPY web/ ./
RUN npm run build

# --- release: serve + migrate/seed in one image ---
FROM base AS release
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    REGISTRY_ROOT=/registry

COPY --from=deps /app/web/node_modules ./node_modules
COPY --from=build /app/web/.next ./.next
COPY web/package.json web/next.config.ts web/tsconfig.json ./
COPY web/public ./public
COPY web/src ./src
COPY web/scripts ./scripts
COPY web/drizzle ./drizzle

# Registry source of truth, baked in for the (idempotent) seed step.
COPY index.json models.json categories.json /registry/
COPY skills /registry/skills
COPY mcp /registry/mcp
COPY agents /registry/agents
COPY workflows /registry/workflows

COPY web/docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 3000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["npm", "run", "start"]
