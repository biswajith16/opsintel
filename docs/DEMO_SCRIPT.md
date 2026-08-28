# OpsIntel demo script

## 2–3 minute walkthrough

- **0:00–0:20 — Landing:** Explain that OpsIntel connects operational signals into evidence-backed investigations.
- **0:20–0:45 — Overview:** Show facility state, incidents, zone context, and honest evaluation metrics.
- **0:45–1:15 — Live Operations:** Start the deterministic simulation and watch deviations emerge.
- **1:15–1:50 — Incident Detail:** Pause and review the timeline, evidence, competing hypotheses, counter-evidence, confidence, and recommendation.
- **1:50–2:10 — Asset Detail:** Show the behavioral baseline, recent activity, anomalies, and linked incidents.
- **2:10–2:30 — What-If:** Run two materially different inputs and compare dynamic scoring.
- **2:30–2:45 — AI Performance:** Explain seeded evaluation and the separation of anomaly severity from root-cause confidence.

## Technical talk track

I built OpsIntel to explore a problem I find interesting in physical operations: detecting an anomaly is often easier than understanding whether several signals belong to the same incident. The system learns deterministic behavioral baselines from synthetic operational history, scores deviations, correlates related events into incidents, builds an evidence graph, ranks competing root-cause hypotheses, and exposes supporting and contradicting evidence for operator review. I deliberately separated anomaly severity from root-cause confidence so the system does not overstate causality.
