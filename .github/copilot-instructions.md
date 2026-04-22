# Project Guidelines

## Code Style
- Backend is Python 3.12 + Django/DRF (see backend/pyproject.toml). Follow existing patterns in backend/kernelCI_app/views and backend/kernelCI_app/queries.
- Frontend is React + TypeScript + Vite. Formatting/linting via Prettier + ESLint (scripts in dashboard/package.json).

## Architecture
- Monorepo:
  - Backend (Django): backend/kernelCI (settings/urls) + backend/kernelCI_app (API) + backend/kernelCI_cache (SQLite cache DB).
  - Frontend (React): dashboard/.
- Backend routing:
  - Root URLconf: backend/kernelCI/urls.py; API mounted via backend/kernelCI_app/urls.py.
  - Views are DRF APIView classes, commonly annotated with drf-spectacular `@extend_schema` (example: backend/kernelCI_app/views/proxyView.py).
  - backend/kernelCI_app/views/__init__.py re-exports view classes; URLconfs often import from the package.
- Backend data access/caching:
  - Query/aggregation logic lives in backend/kernelCI_app/queries (prefer adding/changing query logic there vs in views).
  - Redis caching helpers: backend/kernelCI_app/cache.py; cache backend configured in backend/kernelCI/settings.py.
  - Multi-DB behavior/migrations use router logic in backend/kernelCI_app/routers/databaseRouter.py.
- Frontend routing/state:
  - TanStack Router file-based routes live in dashboard/src/routes; generated route tree: dashboard/src/routeTree.gen.ts.
  - Prefer URL/search params for shareable state (see dashboard/README.md); additional local state may use Zustand (example: dashboard/src/hooks/store/useSearchStore.tsx).
  - React Query is the primary async cache; configured in dashboard/src/main.tsx.

## Build and Test
- Full stack (proxy + backend + dashboard):
  - `docker compose up --build -d`
  - Local access: frontend `http://localhost` and backend `http://localhost/api` (see README.md).
- Frontend (from dashboard/):
  - Install: `pnpm install`
  - Dev: `pnpm dev`
  - Unit tests: `pnpm test` (Vitest)
  - E2E: `pnpm run e2e` / `pnpm run e2e-ui` (Playwright; config in dashboard/playwright.config.ts)
  - Lint/format: `pnpm lint`, `pnpm prettify`
- Backend (from backend/):
  - Install: `poetry install`
  - Run: `poetry run python3 manage.py runserver`
  - Tests: `poetry run pytest` (markers: `-m unit|integration|performance`)
    - Integration tests are request-based and require the server running; otherwise they are skipped (details in backend/README.md).
  - Cache SQLite migrations: `./migrate-cache-db.sh`
  - OpenAPI schema generation: `./generate-schema.sh`

## Project Conventions
- Frontend env vars are Vite `import.meta.env.*` (e.g., `VITE_API_BASE_URL` in dashboard/src/api/api.ts). Keep feature flags as Vite env vars (documented in dashboard/README.md).
- Backend DB config uses `DB_DEFAULT` as a JSON string env var (documented in backend/README.md). There is also a secondary local dashboard DB controlled by `USE_DASHBOARD_DB`.
- Cron jobs use django-crontab (`CRONJOBS` in backend/kernelCI/settings.py). “Tasks” are plain functions in backend/kernelCI_app/tasks.py; longer workflows are management commands under backend/kernelCI_app/management/commands.

## Integration Points
- Cloud SQL proxy uses ADC mounted from application_default_credentials.json (docker-compose.yml). Local Postgres runs as `dashboard_db` on host port 5434.
- Redis runs as docker service `redis` (docker-compose.yml) and backs Django caching.
- Reverse proxy lives under proxy/ and routes `/api` to backend (nginx template: proxy/etc/nginx/templates/default.conf.template).
- Monitoring stack via docker-compose.monitoring.yml (Prometheus/Grafana) and load testing via docker-compose.k6.yml (k6 scripts in k6/tests).

## Security
- Never commit or paste secrets: application_default_credentials.json, backend/runtime/secrets/*, or any real `.env` values. Use the `*.example` files as references.
- Be careful with debug envs that may leak info: `DEBUG`, `DEBUG_SQL_QUERY`, `DEBUG_DB_VARS` (see backend/README.md and backend/kernelCI/settings.py).
- DISCORD_WEBHOOK_URL controls 5xx error reporting middleware (backend/kernelCI_app/middleware/logServerErrorMiddleware.py); treat as sensitive.
