# Deployment plan

> The current deterministic demo does not require Supabase. Simulation state is process-local and resets when the API restarts.

## Exact decisions

| Concern | Decision |
| --- | --- |
| Frontend | Next.js static/SSR app on Vercel. |
| Python backend | One FastAPI web service on Render, deployed from `apps/api`; bind Uvicorn to `0.0.0.0:$PORT`. |
| Database | Supabase Postgres, accessed only from FastAPI using a server-side connection string. |
| API connection | Browser uses `NEXT_PUBLIC_API_URL=https://<api-host>/api/v1`; FastAPI allows only production Vercel origin plus local dev origin via `CORS_ALLOWED_ORIGINS`. |
| Initialization | CI/release runs migrations, then idempotent `seed-demo --seed 20260828 --scenario-version v1`; API readiness requires fixtures/artifacts. |
| Reset | Auth-free demo endpoint uses a run-scoped reset token returned on initialization; it deletes/recreates only that run transactionally. Add rate limiting. |
| Live mode | Browser polling starts idempotent API ticks. No WebSocket, queue, or cron service. |
| ML loading | Versioned sklearn/statistical artifacts ship with the API image and load once at startup. |

## Environment variables

Frontend: `NEXT_PUBLIC_API_URL`.

API: `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `DEMO_SEED`, `MODEL_ARTIFACT_VERSION`, `RESET_RATE_LIMIT`, `ENABLE_LLM_ENHANCEMENT=false`, and optional `LLM_API_KEY`. Never expose database or LLM credentials to the browser. Use separate preview/production API URLs and CORS origins.

## Cost and operational assumptions

Use Vercel and Supabase free tiers while within their current limits, and Render Free only for disposable previews. Render documents that free web services spin down after 15 minutes of inactivity; for an outreach-ready demo, select its smallest paid web-service plan so cold starts do not undermine a demonstration. Supabase’s free tier currently includes a 500 MB database but pauses inactive projects; upgrading is a deliberate reliability choice, not a functional dependency. Monitor the provider pages before launch because limits/prices can change.

This is intentionally two deployables and one database. It avoids Kubernetes, serverless Python cold-start tuning, vector infrastructure, event brokers, persistent disks, and external streaming. Render supports public FastAPI web services and Vercel receives only the public API URL. Sources: [Render FastAPI deployment](https://render.com/docs/deploy-fastapi), [Render free limitations](https://render.com/docs/free), [Supabase pricing](https://supabase.com/pricing).

## Tests and release gate

Python: pytest unit tests for generators, features, scores, graph DTOs, API contracts, and seeded end-to-end scenarios. Web: Vitest/React Testing Library for states and Playwright for critical flows, keyboard operation, narrow view, and What-If behavior. CI runs format/lint/type checks, both test suites, fixture determinism, OpenAPI contract checks, and a deployment health check.
