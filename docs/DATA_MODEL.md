# Data model

All operational records use UUID primary keys, UTC timestamps, `scenario_id`, `seed_version`, and a JSONB `metadata` escape hatch. Synthetic names are display labels; stable IDs remain immutable.

| Entity | Key fields | Relationships |
| --- | --- | --- |
| Facility | id, name, timezone | has zones, entities, sensors |
| Zone | id, facility_id, name, type, geometry_hint | hosts events and sensors |
| Entity | id, facility_id, type, label, status | vehicle, worker, machine, camera, or asset |
| Sensor | id, entity_id/zone_id, kind, unit, cadence | produces events |
| Event | id, occurred_at, source, event_type, entity_id, zone_id, payload, scenario_id | evidence input |
| BehavioralBaseline | id, subject_type/id, feature, window, expected distribution, version | compared with event/features |
| Anomaly | id, event_id, detector, score_0_100, feature_deltas, threshold, status | grouped into incidents |
| Incident | id, run_id, severity, confidence, state, summary, started_at, ended_at | has anomalies, evidence, causes |
| Evidence | id, incident_id, event_id nullable, relation, weight, explanation | graph node/edge support |
| InvestigationTrace | id, incident_id, step, tool, input_summary, result_summary, occurred_at | auditable summary, not chain-of-thought |
| OperatorFeedback | id, incident_id, action, selected_cause, severity_override, note, actor_label, created_at | evaluation label |

## Ground truth and graphs

`scenario_manifest` records scenario ID, deterministic seed, injected event IDs, expected anomaly labels, primary and alternative causes, and expected evidence IDs. This makes evaluation joins explicit. NetworkX graphs stay runtime objects; API graph DTOs are `{nodes:[{id,type,label,attributes}],edges:[{source,target,type,weight,attributes}]}` and reference canonical IDs.

## Retention and reset

The demo keeps 30 simulated days and derived records. A reset transaction deletes only rows with the selected `demo_run_id`, reapplies the versioned seed fixture, and returns the new run ID. Baseline/model versions are recorded with each run so results are reproducible.
