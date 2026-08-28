from fastapi.testclient import TestClient
from app.main import app
from app.ml.baselines import build_baselines
from app.ml.scoring import score_what_if
from app.ml.scoring import isolation_forest_scores
from app.domain.models import WhatIfRequest
from app.simulation.generator import generate_events
from app.reasoning.correlation import correlation
from app.reasoning.incidents import build_incidents

client=TestClient(app)
def test_deterministic_generation():
    a,_=generate_events(12);b,_=generate_events(12);c,_=generate_events(13)
    assert [x.model_dump_json() for x in a]==[x.model_dump_json() for x in b]
    assert a[0].timestamp!=c[0].timestamp or a[0].value!=c[0].value
    assert len(a)>5000
def test_baselines_and_ground_truth_are_separate():
    events,truth=generate_events(2); baselines=build_baselines([e for e in events if not e.scenario_id])
    assert baselines and truth and not hasattr(baselines,"root_cause")
def test_dynamic_score_and_rule():
    critical=score_what_if(WhatIfRequest(entity_id="forklift-a",zone_id="restricted-zone-c",dwell_minutes=12,temperature_c=92,vibration=8.4,production_slowdown=True,hour=14))
    normal=score_what_if(WhatIfRequest(entity_id="forklift-a",zone_id="warehouse-a",dwell_minutes=2,hour=14))
    assert critical.score>normal.score and critical.severity.value=="critical"
def test_isolation_forest_reproducibility():
    rows=[(70,2.1,110),(71,2.0,115),(69,2.2,112),(92,8.4,42),(70,2.1,111)]
    assert isolation_forest_scores(rows)==isolation_forest_scores(rows)
def test_health_and_filters():
    assert client.get("/health").json()["status"]=="ok"
    assert client.get("/events",params={"entity":"forklift-a","limit":3}).status_code==200
    assert all(x["entity_id"]=="forklift-a" for x in client.get("/events",params={"entity":"forklift-a","limit":3}).json())
def test_what_if_endpoint():
    payload={"entity_id":"forklift-a","zone_id":"restricted-zone-c","dwell_minutes":12,"temperature_c":92,"vibration":8.4,"production_slowdown":True,"hour":14}
    assert client.post("/what-if/score",json=payload).json()["score"]>75
def test_correlation_and_distractor_rejection():
    events,_=generate_events(20260828)
    flagship=[e for e in events if e.scenario_id=="scenario-01"]
    related=correlation(flagship[0],flagship[2]); distant=correlation(flagship[2], next(e for e in events if e.entity_id=="forklift-b" and e.zone_id=="warehouse-b"))
    assert related.score>distant.score and distant.shared_entity_score==0
def test_incidents_are_deterministic_and_graph_safe():
    events,_=generate_events(20260828); first=build_incidents(events); second=build_incidents(events)
    assert list(first)==list(second)
    flagship=next(item for item in first.values() if "forklift-a" in item["incident"].entity_ids and "machine-m17" in item["incident"].entity_ids)
    assert len(flagship["graph"].nodes)>1 and flagship["incident"].candidate_hypotheses
def test_incident_endpoints_and_noisy_sensor_behavior():
    rows=client.get("/incidents").json(); assert rows
    incident_id=rows[0]["incident_id"]
    assert client.get(f"/incidents/{incident_id}/graph").status_code==200
    assert client.get(f"/incidents/{incident_id}/hypotheses").status_code==200
    # An isolated noisy spike must not expand into an unbounded evidence bundle.
    assert all(len(client.get(f"/incidents/{row['incident_id']}/timeline").json())<=12 for row in rows)
def test_trace_feedback_and_evaluation():
    incident_id=client.get("/incidents").json()[0]["incident_id"]
    assert client.get(f"/incidents/{incident_id}/trace").status_code==200
    response=client.post(f"/incidents/{incident_id}/feedback",json={"id":"feedback-1","incident_id":"ignored","action":"confirm","note":"Reviewed"})
    assert response.status_code==200 and client.get("/metrics/evaluation").json()["feedback_count"]>=1
def test_pattern_of_life_api():
    body=client.get("/pattern-of-life/forklift-a").json()
    assert body["entity"]["id"]=="forklift-a" and body["recent_events"]
def test_simulation_controls_and_reset_are_deterministic():
    client.post("/simulation/reset"); initial=client.get("/simulation/state").json(); client.post("/simulation/start"); client.post("/simulation/tick"); advanced=client.get("/simulation/live").json(); assert advanced["events_processed"]>initial["events_processed"]
    client.post("/simulation/pause"); paused=client.post("/simulation/tick").json(); assert paused["events_processed"]==advanced["events_processed"]
    client.post("/simulation/reset"); assert client.get("/simulation/state").json()["events_processed"]==0
def test_overview_aggregation():
    body=client.get("/overview").json(); assert body["facility"] and len(body["zones"])==7 and body["status"] in {"normal","elevated","critical"}
