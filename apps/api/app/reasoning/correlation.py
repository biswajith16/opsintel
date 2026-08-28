from __future__ import annotations
from datetime import timedelta
from app.domain.models import CorrelationScore, OperationalEvent

RELATED_ZONES={frozenset({"restricted-zone-c","packaging-line"}),frozenset({"warehouse-a","packaging-line"}),frozenset({"loading-dock","warehouse-a"})}
def correlation(a:OperationalEvent,b:OperationalEvent)->CorrelationScore:
    minutes=abs((b.timestamp-a.timestamp).total_seconds())/60
    temporal=100 if minutes<=2 else 70 if minutes<=5 else 35 if minutes<=15 else 0
    spatial=100 if a.zone_id==b.zone_id else 65 if frozenset({a.zone_id,b.zone_id}) in RELATED_ZONES else 10 if a.facility_id==b.facility_id else 0
    shared=100 if a.entity_id and a.entity_id==b.entity_id else 0
    dependency=85 if {a.entity_id,b.entity_id}=={"forklift-a","machine-m17"} else 75 if {a.entity_id,b.entity_id}=={"machine-m17","conveyor-c03"} else 0
    telemetry={"telemetry","machine_state"}; semantic=85 if a.event_type in telemetry and b.event_type in telemetry else 55 if "zone_transition" in {a.event_type,b.event_type} and "telemetry" in {a.event_type,b.event_type} else 10
    sequence=80 if a.timestamp<=b.timestamp and ((a.source_id=="temp-m17" and b.source_id=="vibration-m17") or (a.source_id=="vibration-m17" and b.event_type=="machine_state")) else 30 if a.timestamp<=b.timestamp else 0
    score=round(.25*temporal+.15*spatial+.15*shared+.2*dependency+.15*semantic+.1*sequence,1)
    return CorrelationScore(score=score,temporal_score=temporal,spatial_score=spatial,shared_entity_score=shared,dependency_score=dependency,semantic_score=semantic,sequence_score=sequence,reason=f"{minutes:.1f} minutes apart; spatial and operational relationship evaluated")
