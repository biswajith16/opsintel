import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "apps/api"))
from app.ml.baselines import build_baselines
from app.simulation.generator import generate_events
events,_=generate_events(20260828)
baselines=build_baselines([event for event in events if not event.scenario_id])
print(json.dumps({"entities":len(baselines),"baseline_count":sum(len(rows) for rows in baselines.values())}))
