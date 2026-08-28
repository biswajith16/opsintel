"""Preliminary event-level detection metrics; evaluation truth is imported only here, never by API inference."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "apps/api"))
from app.repositories.memory import DemoRepository

repo=DemoRepository(20260828)
detected={row["event_id"] for row in repo.detected_anomalies()}
truth={event_id for record in repo.ground_truth for event_id in record.event_ids}
tp=len(detected & truth); fp=len(detected-truth); fn=len(truth-detected)
print(json.dumps({"events":len(repo.events),"injected_anomaly_events":len(truth),"detected":len(detected),"true_positives":tp,"false_positives":fp,"false_negatives":fn,"precision":round(tp/(tp+fp),3) if tp+fp else 0,"recall":round(tp/(tp+fn),3) if tp+fn else 0},indent=2))
