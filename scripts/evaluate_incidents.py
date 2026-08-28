"""Evaluation-only comparison. Ground truth never enters incident inference."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"apps/api"))
from app.repositories.memory import DemoRepository

repo=DemoRepository(20260828); incidents=list(repo.incidents.values()); truth=repo.ground_truth
matched=[]
for record in truth:
    candidates=[item for item in incidents if set(record.event_ids)&set(item["incident"].event_ids)]
    if candidates: matched.append((record,max(candidates,key=lambda item:len(set(record.event_ids)&set(item["incident"].event_ids)))))
top1=sum(item["incident"].candidate_hypotheses[0].title.lower()==record.root_cause for record,item in matched)
top3=sum(any(record.root_cause in h.title.lower() for h in item["incident"].candidate_hypotheses) for record,item in matched)
grounded=sum(len(set(record.event_ids)&set(item["incident"].event_ids)) for record,item in matched); included=sum(len(item["incident"].event_ids) for _,item in matched); expected=sum(len(r.event_ids) for r,_ in matched)
print(json.dumps({"ground_truth_scenarios":len(truth),"grouped_scenarios":len(matched),"incident_grouping_accuracy":round(len(matched)/len(truth),3),"root_cause_top_1":round(top1/len(matched),3) if matched else 0,"root_cause_top_3":round(top3/len(matched),3) if matched else 0,"evidence_grounding_accuracy":round(grounded/included,3) if included else 0,"average_relevant_events_missed":round((expected-grounded)/len(matched),2) if matched else 0,"average_distractors_included":round((included-grounded)/len(matched),2) if matched else 0},indent=2))
