# ML and evaluation design

## Interpretable hybrid detection

The baseline is per entity/zone/time segment, calculated from normal seeded history. Features include route-transition probability, dwell percentile, time-of-day frequency, occupancy, temperature slope/deviation, vibration deviation, machine state duration, throughput delta, and event-sequence order.

Use robust z-scores and explicit operational constraints first; Isolation Forest is a complementary detector for multivariate telemetry. Route anomalies use transition likelihood; dwell anomalies use robust percentile bounds. No detector alone creates a root-cause claim.

`anomaly_score = clamp(100 * weighted_detector_score)`. Weights are versioned and published in the run metadata. Default bands: 0–39 normal, 40–59 watch, 60–79 elevated, 80–100 critical candidate. Incident severity combines anomaly score, operational impact, corroborating-source count, and uncertainty; confidence represents evidence coverage/consistency, not causality.

## Correlation and root-cause ranking

Temporal links are constrained by source-pair windows; spatial links require same/adjacent zone; sequence links encode expected ordering. NetworkX ranks candidate explanations from weighted evidence-path support, counter-evidence penalties, and scenario/rule priors. Output always includes multiple candidates: vehicle/equipment interaction, mechanical failure, and sensor malfunction for the flagship sequence when supported.

## Models in production

Models are trained offline during fixture/artifact generation, serialized with compatible package versions, and loaded once at FastAPI startup. Small fixtures and artifacts are committed/versioned for the demo; production later can move them to object storage without API contract change. The fallback remains robust statistics and rules if a model artifact is unavailable.

## Ground truth and evaluation

Eight seeded scenarios include expected anomalies, causes, evidence links, and injected timestamps. Offline tests measure anomaly precision/recall/FPR, detection latency, top-1/top-3 cause accuracy, evidence precision/recall, and model latency. Feedback supplies a separate operator-agreement and review-time measure; it does not silently retrain a demo model.
