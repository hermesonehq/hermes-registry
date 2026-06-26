#!/bin/sh
# On container start: apply migrations + seed the registry (both idempotent;
# the seed never resets download counters), then exec the given command (the
# Next.js server). Set RUN_MIGRATIONS=false to skip — e.g. for extra app
# replicas that shouldn't each re-seed.
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "[entrypoint] applying migrations + seed…"
  npm run db:migrate
  npm run db:seed
else
  echo "[entrypoint] RUN_MIGRATIONS=false — skipping migrate/seed"
fi

echo "[entrypoint] starting app…"
exec "$@"
