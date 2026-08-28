-- Local SQLite / production Postgres migration foundation. Full repository persistence follows the same identifiers.
CREATE TABLE IF NOT EXISTS demo_runs (id TEXT PRIMARY KEY, seed INTEGER NOT NULL, dataset_version TEXT NOT NULL, created_at TIMESTAMP NOT NULL);
CREATE TABLE IF NOT EXISTS operational_events (event_id TEXT PRIMARY KEY, run_id TEXT, occurred_at TIMESTAMP NOT NULL, facility_id TEXT NOT NULL, zone_id TEXT, entity_id TEXT, source_id TEXT, event_type TEXT NOT NULL, value REAL, unit TEXT, scenario_id TEXT, metadata_json TEXT);
