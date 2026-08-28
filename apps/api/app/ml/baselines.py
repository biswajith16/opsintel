from collections import Counter, defaultdict
from statistics import median
from app.domain.models import BehavioralBaseline, OperationalEvent

def _mad(values: list[float], med: float) -> float: return median([abs(v-med) for v in values]) or 0.1
def build_baselines(events: list[OperationalEvent]) -> dict[str,list[BehavioralBaseline]]:
    numeric=defaultdict(list); dwell=defaultdict(list); active=defaultdict(set); transitions=Counter()
    ordered=defaultdict(list)
    for e in events:
        if e.value is not None and e.event_type=="telemetry": numeric[e.source_id].append(e.value)
        if e.event_type=="dwell" or "dwell_minutes" in e.metadata: dwell[(e.entity_id,e.zone_id)].append(float(e.value or e.metadata.get("dwell_minutes",0)))
        if e.entity_id: active[e.entity_id].add(e.timestamp.hour); ordered[e.entity_id].append(e)
    for entity, rows in ordered.items():
        rows.sort(key=lambda x:x.timestamp)
        for a,b in zip(rows,rows[1:]):
            if a.event_type==b.event_type=="zone_transition" and a.zone_id and b.zone_id: transitions[(entity,a.zone_id,b.zone_id)]+=1
    out=defaultdict(list)
    for source,vals in numeric.items():
        med=median(vals);out[source].append(BehavioralBaseline(subject_id=source,baseline_type="numeric",feature="value",median=med,mad=_mad(vals,med),p05=sorted(vals)[max(0,int(.05*len(vals))-1)],p95=sorted(vals)[int(.95*len(vals))-1]))
    for key,vals in dwell.items():
        med=median(vals);out[key[0]].append(BehavioralBaseline(subject_id=key[0],baseline_type="dwell",feature=key[1] or "unknown",median=med,mad=_mad(vals,med)))
    for entity,hours in active.items(): out[entity].append(BehavioralBaseline(subject_id=entity,baseline_type="activity",feature="active_hours",values={str(h):1.0 for h in hours}))
    for (entity,frm,to),count in transitions.items(): out[entity].append(BehavioralBaseline(subject_id=entity,baseline_type="route",feature=f"{frm}->{to}",values={"count":float(count)}))
    return dict(out)
