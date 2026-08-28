# OpsIntel product specification

## Purpose

OpsIntel is a company-neutral operational-intelligence prototype for physical facilities. It learns expected operating behavior, detects material deviations, assembles supporting evidence, and gives an operator calibrated next actions. It is not a camera viewer, a generic analytics dashboard, or a chatbot.

**Disclosure:** Independent proof-of-work prototype demonstrating Operational AI concepts using synthetic data.

## Target users and problems

| User | Need | Outcome |
| --- | --- | --- |
| Operations lead | Triage many weak signals | One evidence-backed incident queue |
| Shift supervisor | Understand disruption fast | Timeline, affected assets, and next action |
| Reliability engineer | Separate mechanical issues from bad telemetry | Competing causes with evidence and confidence |
| Demo reviewer | Verify claims without credentials | Repeatable, interactive synthetic investigation |

## Product hypothesis

When operational signals are compared with entity-specific baselines and connected through time, proximity, and sequence, operators can investigate interruptions more quickly and with fewer false escalations than by inspecting isolated alerts.

## Primary workflows

1. **Triage:** open Operations Overview, filter active incidents, and open the highest-risk one.
2. **Investigate:** read the evidence timeline, inspect baseline changes and graph, compare candidate causes, then confirm, correct, or resolve.
3. **What-if:** adjust entity, zone, dwell, telemetry, slowdown, and time; run the same deterministic scoring pipeline used by the demo.
4. **Live demo:** start, pause, resume, or reset browser-driven simulation ticks; inspect newly formed anomalies and investigations.
5. **Search:** submit a plain-language operations question; deterministic intent parsing maps it to data queries and returns cited records.

## Success criteria

- A seeded 30-day dataset has 5,000+ events, eight or more scenarios, and scenario-level ground truth.
- The flagship Forklift A/M17 sequence produces a high-risk incident with at least three ranked causes and evidence for each.
- Every incident exposes why it was flagged, baseline deltas, supporting and competing evidence, confidence, and a concrete action.
- The entire public demo operates with no external LLM key.
- Evaluation reports precision, recall, false-positive rate, detection time, top-k cause accuracy, evidence-grounding accuracy, operator agreement, investigation time, latency, and human-review rate.

## Non-goals

- Real surveillance ingestion, identity recognition, autonomous control, safety certification, or claims of causal proof.
- A general-purpose conversational agent or an enterprise multi-tenant platform.
- Replacing operator judgment; all classifications are reviewable and correctable.
