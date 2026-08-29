# Deployment plan

## Public deployment

| Component | Production location | Configuration |
| --- | --- | --- |
| Web application | [opsintel-web.vercel.app](https://opsintel-web.vercel.app) | Vercel project `opsintel-web`, root directory `apps/web`, build command `npm run build`. |
| API | [opsintel-api.onrender.com](https://opsintel-api.onrender.com/health) | Render service `opsintel-api`, root directory `apps/api`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. |

The demo uses deterministic synthetic data and process-local state. It does not use Supabase, a database, queues, workers, Redis, or other infrastructure. API restart resets the simulation and operator feedback.

## Production environment

| Service | Variable | Value |
| --- | --- | --- |
| Vercel | `NEXT_PUBLIC_API_URL` | `https://opsintel-api.onrender.com` |
| Render | `DEMO_SEED` | `20260828` |
| Render | `CORS_ALLOWED_ORIGINS` | `https://opsintel-web.vercel.app` |

The API owns the shared simulation clock, so opening multiple browser tabs does not multiply event progression. The Render free instance may sleep after inactivity and needs time to wake on the first request.

## Release checks

Run `npm run test:api`, `npm run lint:web`, `npm run typecheck:web`, and `npm run build:web`. Then verify `/health`, `/overview`, `/simulation/live`, `/incidents`, `/entities`, `/metrics/evaluation`, and `POST /what-if/score` through the public API.
