# OpsIntel

Behavioral intelligence for physical operations—connecting operational events, equipment telemetry, and behavioral patterns to investigate anomalies instead of simply generating more alerts.

> Independent proof-of-work prototype demonstrating Operational AI concepts using synthetic data.

## Public demo

- [Live application](https://opsintel-web.vercel.app)
- [Backend health](https://opsintel-api.onrender.com/health)
- [Source repository](https://github.com/biswajith16/opsintel)

## What OpsIntel does

OpsIntel models expected routes, dwell patterns, activity windows, and machine operating ranges. It scores deviations, correlates related events into incidents, builds evidence graphs, ranks competing root-cause hypotheses, and records operator feedback for evaluation.

## Why it is different

- Entity-specific behavioral baselines
- Multi-source correlation that does not treat time proximity as proof
- Traceable evidence graphs and counter-evidence
- Ranked hypotheses with explicit uncertainty
- Separate anomaly severity and root-cause confidence
- Complete operation without a paid LLM API

## Demo workflow

Live Operations → Incident Investigation → Asset Behavior → What-If Analysis → AI Evaluation.

The flagship scenario follows Forklift A entering Restricted Zone C before Machine M17 develops temperature and vibration anomalies, throughput falls, and the machine stops. Correlation does not prove causation.

## Architecture

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, Pydantic
- Detection: robust statistics and Isolation Forest
- Correlation: bounded scoring and NetworkX
- Similarity: TF-IDF
- Simulation: deterministic seeded event generation
- Deployment: Vercel frontend and Render backend

Operational events → baselines → anomaly detection → correlation → evidence graph → hypotheses → operator review → evaluation.

## Running locally

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

From the repository root in another terminal:

```bash
npm install
cp .env.example apps/web/.env.local
npm run dev:web
```

Open `http://localhost:3000`; API docs are at `http://localhost:8000/docs`.

## Environment variables

| Service | Variable | Purpose |
| --- | --- | --- |
| Web | `NEXT_PUBLIC_API_URL` | Public FastAPI origin |
| API | `DEMO_SEED` | Deterministic seed; default `20260828` |
| API | `CORS_ALLOWED_ORIGINS` | Comma-separated allowed frontend origins |

## Testing

```bash
npm run test:api
npm run lint:web
npm run typecheck:web
npm run build:web
apps/api/.venv/bin/python scripts/evaluate_anomalies.py
apps/api/.venv/bin/python scripts/evaluate_incidents.py
```

## Limitations

- All facility data is synthetic.
- The demo uses one shared process-local session.
- Backend restarts reset simulation and feedback state.
- Correlation is evidence, not causal proof.
- No real camera, sensor, or production-system integration is claimed.
- Supabase persistence is deferred and not required for this demo.

## Responsible AI

OpsIntel ranks multiple hypotheses, exposes contradicting evidence, keeps operator review explicit, and evaluates against seeded ground truth. Recommendations are review prompts rather than autonomous physical-control instructions.
