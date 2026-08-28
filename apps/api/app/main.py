from contextlib import asynccontextmanager
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import DATASET_VERSION, FEATURE_VERSION, MODEL_VERSION, SCENARIO_VERSION, settings
from app.domain.models import WhatIfRequest, OperatorFeedback
from app.ml.scoring import score_what_if
from app.repositories.memory import repository
from app.simulation.scenarios import SCENARIOS
from app.simulation.world import ENTITIES, FACILITY, SENSORS, ZONES
from app.reasoning.correlation import correlation
from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s %(message)s")
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger("opsintel").info("dataset loaded events=%s seed=%s",len(repository.events),repository.seed); yield
app=FastAPI(title="OpsIntel API",version=settings.api_version,lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_allowed_origins),allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])

@app.get("/health")
def health(): return {"status":"ok","version":settings.api_version,"dataset_version":DATASET_VERSION,"scenario_version":SCENARIO_VERSION,"feature_version":FEATURE_VERSION,"model_version":MODEL_VERSION,"active_seed":repository.seed,"model_availability":{"robust_statistics":True,"isolation_forest":True}}
@app.get("/facilities")
def facilities(): return [FACILITY]
@app.get("/facilities/{facility_id}")
def facility(facility_id:str):
    if facility_id!=FACILITY.id: raise HTTPException(404,"Facility not found")
    return FACILITY
@app.get("/zones")
def zones(): return ZONES
@app.get("/entities")
def entities(entity_type:str|None=None): return [e for e in ENTITIES if not entity_type or e.type.value==entity_type]
@app.get("/entities/{entity_id}")
def entity(entity_id:str):
    return next((e for e in ENTITIES if e.id==entity_id), None) or (_ for _ in ()).throw(HTTPException(404,"Entity not found"))
@app.get("/events")
def events(start:datetime|None=None,end:datetime|None=None,entity:str|None=None,zone:str|None=None,event_type:str|None=None,source:str|None=None,limit:int=Query(200,ge=1,le=1000)):
    return repository.filtered_events(start,end,entity,zone,event_type,source)[:limit]
@app.get("/scenarios")
def scenarios(): return SCENARIOS
@app.get("/scenarios/{scenario_id}")
def scenario(scenario_id:str): return next((s for s in SCENARIOS if s.id==scenario_id),None) or (_ for _ in ()).throw(HTTPException(404,"Scenario not found"))
@app.get("/baselines/{entity_id}")
def baselines(entity_id:str): return repository.baselines.get(entity_id,[])
@app.get("/pattern-of-life/{entity_id}")
def pattern_of_life(entity_id:str):
    entity_data=next((item for item in ENTITIES if item.id==entity_id),None)
    if not entity_data: raise HTTPException(404,"Entity not found")
    rows=repository.filtered_events(entity=entity_id)
    related=[item["incident"] for item in repository.incidents.values() if entity_id in item["incident"].entity_ids]
    related_event_ids={event_id for incident in related for event_id in incident.event_ids}
    anomalies=[row for row in repository.detected_anomalies() if row["entity_id"]==entity_id]
    return {"entity":entity_data,"baselines":repository.baselines.get(entity_id,[]),"recent_events":rows[-50:],"related_incidents":related,"related_anomalies":anomalies,"related_event_ids":list(related_event_ids)}
@app.get("/anomalies")
def anomalies(): return repository.detected_anomalies()
@app.get("/incidents")
def incidents(severity:str|None=None,status:str|None=None,zone:str|None=None,entity:str|None=None,start:datetime|None=None,end:datetime|None=None):
    rows=[item["incident"] for item in repository.incidents.values()]
    return [row for row in rows if (not severity or row.severity.value==severity) and (not status or row.status==status) and (not zone or row.primary_zone_id==zone) and (not entity or entity in row.entity_ids) and (not start or row.start_time>=start) and (not end or row.end_time<=end)]
def _incident(incident_id:str):
    if incident_id not in repository.incidents: raise HTTPException(404,"Incident not found")
    return repository.incidents[incident_id]
@app.get("/incidents/{incident_id}")
def incident(incident_id:str): return _incident(incident_id)["incident"]
@app.get("/incidents/{incident_id}/timeline")
def timeline(incident_id:str): return _incident(incident_id)["events"]
@app.get("/incidents/{incident_id}/evidence")
def evidence(incident_id:str): return _incident(incident_id)["evidence"]
@app.get("/incidents/{incident_id}/graph")
def graph(incident_id:str): return _incident(incident_id)["graph"]
@app.get("/incidents/{incident_id}/hypotheses")
def hypotheses(incident_id:str): return _incident(incident_id)["hypotheses"]
@app.get("/incidents/{incident_id}/similar")
def similar(incident_id:str):
    target=_incident(incident_id)["incident"]; out=[]
    all_rows=list(repository.incidents.items()); corpus=[" ".join(v["incident"].entity_ids+[v["incident"].primary_zone_id or "",v["incident"].leading_hypothesis]) for _,v in all_rows]
    matrix=TfidfVectorizer().fit_transform(corpus); target_index=[i for i,(key,_) in enumerate(all_rows) if key==incident_id][0]
    for index,(other_id,item) in enumerate(all_rows):
        if other_id==incident_id: continue
        other=item["incident"]; shared=sorted(set(target.entity_ids)&set(other.entity_ids)); score=round((len(shared)+int(target.primary_zone_id==other.primary_zone_id))/max(1,len(set(target.entity_ids)|set(other.entity_ids))),2)
        tfidf_score=round(float((matrix[target_index] @ matrix[index].T).toarray()[0,0]),2)
        if tfidf_score: out.append({"incident_id":other_id,"similarity_score":tfidf_score,"shared_features":shared})
    return sorted(out,key=lambda x:x["similarity_score"],reverse=True)[:5]
@app.post("/incidents/{incident_id}/feedback")
def feedback(incident_id:str, item:OperatorFeedback):
    _incident(incident_id); repository.feedback.append(item.model_copy(update={"incident_id":incident_id})); return repository.feedback[-1]
@app.get("/incidents/{incident_id}/trace")
def trace(incident_id:str):
    item=_incident(incident_id); return [{"tool":"bounded_correlation","input_summary":f"{len(item['events'])} events", "result_summary":"Evidence grouped by time, space, dependency, semantics, and sequence."},{"tool":"hypothesis_ranking","input_summary":f"{len(item['evidence'])} evidence records", "result_summary":item["incident"].leading_hypothesis}]
@app.post("/incidents/rebuild")
def rebuild_incidents(): return {"count":len(repository.rebuild_incidents())}
@app.post("/simulation/reset")
def reset(seed:int|None=None): repository.reset(seed if seed is not None else settings.demo_seed); return repository.state()|{"seed":repository.seed}
@app.post("/simulation/start")
def start(): repository.running=True; return repository.state()
@app.post("/simulation/pause")
def pause(): repository.running=False; return repository.state()
@app.post("/simulation/resume")
def resume(): repository.running=True; return repository.state()
@app.post("/simulation/tick")
def tick(): return repository.advance()
@app.get("/simulation/state")
def state(): return repository.state()|{"seed":repository.seed}
@app.get("/simulation/live")
def live():
    current=repository.state()["simulated_at"]
    incidents=[item["incident"] for item in repository.incidents.values() if item["incident"].start_time<=current]
    anomalies=[row for row in repository.detected_anomalies() if row["timestamp"]<=current][-12:]
    return repository.state()|{"seed":repository.seed,"facility":FACILITY.name,"recent_events":repository.recent_events(),"anomalies":anomalies,"incidents":incidents[-8:]}
@app.get("/metrics/dataset")
def metrics(): return repository.metrics()
@app.get("/metrics/evaluation")
def evaluation():
    detected=repository.detected_anomalies(); truth={event_id for record in repository.ground_truth for event_id in record.event_ids}; ids={row["event_id"] for row in detected}; tp=len(ids & truth)
    return {"anomaly_precision":round(tp/len(ids),3) if ids else 0,"anomaly_recall":round(tp/len(truth),3) if truth else 0,"detected_anomalies":len(ids),"ground_truth_events":len(truth),"feedback_count":len(repository.feedback)}
@app.get("/overview")
def overview():
    snapshot=live(); incidents=snapshot["incidents"]; anomalies=snapshot["anomalies"]
    status="critical" if any(i.severity.value=="critical" for i in incidents) else "elevated" if incidents or anomalies else "normal"
    zones=[]
    for zone in ZONES:
        events=[e for e in snapshot["recent_events"] if e.zone_id==zone.id]
        zones.append({"id":zone.id,"name":zone.name,"recent_events":len(events),"entities":sorted({e.entity_id for e in events if e.entity_id}),"has_anomaly":any(a["zone_id"]==zone.id for a in anomalies),"has_incident":any(i.primary_zone_id==zone.id for i in incidents)})
    return {"facility":FACILITY.name,"status":status,"simulation":repository.state()|{"seed":repository.seed},"incidents":incidents[:3],"anomalies":anomalies[:6],"recent_events":snapshot["recent_events"][-6:],"zones":zones,"evaluation":evaluation()}
@app.post("/what-if/score")
def what_if(request:WhatIfRequest): return score_what_if(request)
