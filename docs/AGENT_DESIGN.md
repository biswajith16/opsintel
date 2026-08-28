# Investigation agent design

## Deterministic orchestration

An investigation is a bounded state machine, not an unconstrained autonomous agent:

`validate incident → collect history → compare baseline → correlate time/space → retrieve similar scenarios → build graph → calculate risk → rank causes → recommend action → persist summary`.

Each transition records an `InvestigationTrace` with tool name, concise validated input, concise result, timestamp, artifact version, and duration. It never stores or exposes private reasoning.

## Tool contracts

`search_events`, `inspect_entity_history`, `inspect_sensor_history`, `compare_against_baseline`, `find_temporally_related_events`, `find_spatially_related_events`, `retrieve_similar_incidents`, `build_evidence_graph`, `calculate_risk`, `rank_root_causes`, and `generate_recommendations` accept typed IDs/windows and return structured DTOs with evidence IDs.

## Safeguards

- Read-only tool access except explicit operator feedback and reset endpoints.
- Maximum time window, result count, graph size, and tool-step count.
- Candidate causes are ranked hypotheses; UI labels uncertainty and shows alternatives.
- Recommendations are review actions, never autonomous physical-control instructions.
- All narrative statements link to returned evidence IDs.

## No-LLM default and optional boundary

Standard mode uses templates, intent patterns, TF-IDF similarity, rules, ML scores, and graph algorithms. Search maps supported query patterns to parameterized database/API queries and returns an unsupported-query explanation when needed. An optional server-only `NarrativeEnhancer` adapter may summarize an already-grounded result when `LLM_API_KEY` and `ENABLE_LLM_ENHANCEMENT=true`; it cannot call tools, alter scores, or add uncited claims. Its absence changes wording only, never functionality.
