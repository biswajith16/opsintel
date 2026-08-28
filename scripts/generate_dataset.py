"""Emit a reproducible dataset summary without persisting hidden ground truth into inference inputs."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "apps/api"))
from app.simulation.generator import generate_events
events, truth = generate_events(20260828)
print(json.dumps({"events":len(events),"ground_truth_records":len(truth),"first_event":events[0].event_id}, indent=2, default=str))
