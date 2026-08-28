from __future__ import annotations
from datetime import datetime, timezone
import networkx as nx
from app.domain.models import Evidence, EvidenceStrength, GraphDTO, GraphEdge, GraphNode, Hypothesis, Incident, OperationalEvent, Severity
from app.reasoning.correlation import correlation

def _signal(event:OperationalEvent)->bool:
    return (event.entity_id in {"forklift-a","forklift-b","tugger-t01"} and event.zone_id=="restricted-zone-c") or (event.event_type=="dwell" and (event.value or 0)>25) or (event.event_type=="worker_activity" and float(event.metadata.get("dwell_minutes",0))>25) or (event.event_type=="zone_transition" and event.timestamp.hour<6) or (event.event_type=="occupancy" and event.zone_id=="restricted-zone-c" and event.entity_id and event.entity_id.startswith("worker")) or (event.source_id=="temp-m17" and (event.value or 0)>82) or (event.source_id=="vibration-m17" and (event.value or 0)>5) or (event.source_id=="throughput-c03" and event.timestamp.hour in range(7,22) and (event.value or 999)<60) or (event.event_type=="machine_state" and event.metadata.get("state")=="stopped")
def build_incidents(events:list[OperationalEvent])->dict[str,dict]:
    seeds=[e for e in events if _signal(e)]; consumed=set(); results={}
    for seed in seeds:
        if seed.event_id in consumed: continue
        neighborhood=[seed]
        # bounded one-hop expansion, 15 minutes, minimum 45. A nearby unrelated badge event remains out.
        for candidate in events:
            if candidate.event_id==seed.event_id or abs((candidate.timestamp-seed.timestamp).total_seconds())>15*60: continue
            score=correlation(seed,candidate)
            if score.score>=45 and len(neighborhood)<12: neighborhood.append(candidate)
        if len(neighborhood)<2 and seed.source_id=="temp-m17": continue # isolated noisy signal is not a major incident
        for item in neighborhood: consumed.add(item.event_id)
        ordered=sorted({e.event_id:e for e in neighborhood}.values(),key=lambda e:e.timestamp)
        incident_id=f"inc-{seed.event_id}"
        evidence=[]
        for idx,event in enumerate(ordered,1):
            kind="machine stop" if event.event_type=="machine_state" else "restricted-zone entry" if event.zone_id=="restricted-zone-c" and event.entity_id and "forklift" in event.entity_id else "temperature deviation" if event.source_id=="temp-m17" else "vibration deviation" if event.source_id=="vibration-m17" else "throughput change" if event.source_id=="throughput-c03" else "temporal relationship"
            evidence.append(Evidence(evidence_id=f"{incident_id}-ev-{idx}",type=kind,source_id=event.source_id,event_id=event.event_id,entity_id=event.entity_id,zone_id=event.zone_id,timestamp=event.timestamp,claim_supported="operational interruption",relationship_type="observed",strength=EvidenceStrength.strong if kind in {"machine stop","temperature deviation","vibration deviation"} else EvidenceStrength.moderate,summary=f"{kind.capitalize()} observed at {event.timestamp.isoformat()}"))
        types={e.type for e in evidence}; vehicle=any(e.entity_id=="forklift-a" for e in evidence); thermal={"temperature deviation","vibration deviation"}<=types
        veh_conf=min(85,35+(25 if vehicle else 0)+(20 if thermal else 0)); mech_conf=min(85,35+(35 if thermal else 0)+(15 if "machine stop" in types else 0)); sensor_conf=45+(20 if len(types)==1 else 0)
        hypotheses=[Hypothesis(hypothesis_id="vehicle-interaction",title="Vehicle/equipment interaction",confidence=veh_conf,supporting_evidence_ids=[e.evidence_id for e in evidence if e.entity_id=="forklift-a" or e.type=="restricted-zone entry"],contradicting_evidence_ids=[] if vehicle else [evidence[0].evidence_id],reason_summary="Vehicle proximity is considered only alongside equipment evidence."),Hypothesis(hypothesis_id="mechanical-failure",title="Mechanical failure",confidence=mech_conf,supporting_evidence_ids=[e.evidence_id for e in evidence if e.type in {"temperature deviation","vibration deviation","machine stop"}],contradicting_evidence_ids=[] if thermal else [evidence[0].evidence_id],reason_summary="Telemetry sequence and shutdown support a mechanical explanation."),Hypothesis(hypothesis_id="sensor-malfunction",title="Sensor malfunction",confidence=sensor_conf,supporting_evidence_ids=[e.evidence_id for e in evidence if e.type in {"temperature deviation","vibration deviation"}],contradicting_evidence_ids=[e.evidence_id for e in evidence if e.type=="machine stop"],reason_summary="Multi-source corroboration lowers the single-sensor explanation.")]
        hypotheses.sort(key=lambda x:x.confidence,reverse=True); risk=min(100,45+len(evidence)*7+max(h.confidence for h in hypotheses)/4); severity=Severity.critical if risk>75 else Severity.elevated
        inc=Incident(incident_id=incident_id,title="Correlated operational anomaly",summary=f"{len(evidence)} related observations indicate an operational deviation requiring review.",facility_id=seed.facility_id,primary_zone_id=seed.zone_id,start_time=ordered[0].timestamp,end_time=ordered[-1].timestamp,severity=severity,risk_score=round(risk,1),anomaly_ids=[e.event_id for e in ordered if _signal(e)],event_ids=[e.event_id for e in ordered],entity_ids=sorted({e.entity_id for e in ordered if e.entity_id}),sensor_ids=sorted({e.source_id for e in ordered if e.source_id}),evidence_ids=[e.evidence_id for e in evidence],leading_hypothesis=hypotheses[0].title,root_cause_confidence=hypotheses[0].confidence,candidate_hypotheses=hypotheses,recommendation="Review correlated telemetry and available camera evidence before restart or escalation.",created_at=datetime.now(timezone.utc))
        graph=graph_for(inc,ordered,evidence,hypotheses)
        results[incident_id]={"incident":inc,"events":ordered,"evidence":evidence,"graph":graph,"hypotheses":hypotheses}
    return results
def graph_for(incident,events,evidence,hypotheses)->GraphDTO:
    g=nx.DiGraph();g.add_node(incident.incident_id,type="incident",label=incident.title)
    for event in events:g.add_node(event.event_id,type="event",label=event.event_type);g.add_edge(event.event_id,incident.incident_id,relationship_type="affected",score=75,reason="Included by bounded correlation")
    for h in hypotheses:g.add_node(h.hypothesis_id,type="hypothesis",label=h.title);g.add_edge(h.hypothesis_id,incident.incident_id,relationship_type="possible_cause",score=h.confidence,reason=h.reason_summary)
    return GraphDTO(nodes=[GraphNode(id=n,type=d["type"],label=d["label"]) for n,d in g.nodes(data=True)],edges=[GraphEdge(source=a,target=b,relationship_type=d["relationship_type"],score=d["score"],reason=d["reason"]) for a,b,d in g.edges(data=True)])
