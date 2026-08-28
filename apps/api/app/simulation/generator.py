from __future__ import annotations
from datetime import datetime, timedelta, timezone
import random
from app.domain.models import GroundTruth, OperationalEvent
from app.simulation.world import FACILITY

def _event(n: int, at: datetime, typ: str, entity: str, zone: str, value: float | None=None, unit: str | None=None, source: str | None=None, scenario: str | None=None, **metadata: object) -> OperationalEvent:
    return OperationalEvent(event_id=f"evt-{n:06d}", timestamp=at, facility_id=FACILITY.id, zone_id=zone, entity_id=entity, source_id=source or entity, event_type=typ, value=value, unit=unit, metadata=metadata, scenario_id=scenario)

def generate_events(seed: int, start: datetime | None=None, days: int=30) -> tuple[list[OperationalEvent], list[GroundTruth]]:
    """Generate realistic, noisy normal operations plus seeded scenario injections."""
    rng=random.Random(seed); start=start or datetime(2026,8,1,tzinfo=timezone.utc); events=[]; n=0
    for day in range(days):
        base=start+timedelta(days=day)
        for minute in range(6*60,22*60,15):
            for entity, route in (("forklift-a",["loading-dock","warehouse-a","packaging-line"]),("forklift-b",["receiving-bay","warehouse-b"]),("tugger-t01",["warehouse-a","packaging-line"])):
                zone=route[(minute//15)%len(route)]; n+=1; events.append(_event(n,base+timedelta(minutes=minute+rng.randint(-2,2)),"zone_transition",entity,zone,scenario_id=None,previous_zone=route[(minute//15-1)%len(route)]))
        for minute in range(6*60,22*60,10):
            at=base+timedelta(minutes=minute); active=1 if 7*60<=minute<=21*60 else 0
            n+=1; events.append(_event(n,at,"telemetry","machine-m17","packaging-line",70+rng.gauss(0,2),"celsius","temp-m17"))
            n+=1; events.append(_event(n,at,"telemetry","machine-m17","packaging-line",2.1+rng.gauss(0,.25),"mm/s","vibration-m17"))
            n+=1; events.append(_event(n,at,"telemetry","conveyor-c03","packaging-line",(115+rng.gauss(0,8))*active,"units/min","throughput-c03"))
            n+=1; events.append(_event(n,at,"machine_state","machine-m17","packaging-line",float(active),"state","state-m17",state="running" if active else "idle"))
        for worker, zone in (("worker-101","warehouse-a"),("worker-204","packaging-line"),("worker-317","maintenance-area"),("worker-411","loading-dock")):
            n+=1; events.append(_event(n,base+timedelta(hours=8+rng.randrange(8)),"worker_activity",worker,zone,source="cam-01",dwell_minutes=round(rng.uniform(3,12),1)))
    # Eight scenario injections across the period, explicitly kept outside inference inputs.
    specs=[("scenario-01",14,"forklift-a","restricted-zone-c","route_deviation",None),("scenario-02",17,"worker-317","maintenance-area","worker_activity",45),("scenario-03",20,"machine-m17","packaging-line","telemetry",96),("scenario-04",23,"tugger-t01","warehouse-a","zone_transition",None),("scenario-05",9,"forklift-b","restricted-zone-c","zone_transition",None),("scenario-06",15,"conveyor-c03","packaging-line","telemetry",38),("scenario-07",11,"machine-m17","packaging-line","telemetry",104),("scenario-08",13,"worker-204","restricted-zone-c","occupancy",1)]
    truth=[]
    for idx,(sid,hour,entity,zone,typ,value) in enumerate(specs,1):
        at=start+timedelta(days=idx*3,hours=hour,minutes=32); ids=[]
        def add(offset: int, etype: str, ent: str, z: str, val: float | None, unit: str | None, src: str, **meta: object):
            nonlocal n; n+=1; ev=_event(n,at+timedelta(minutes=offset),etype,ent,z,val,unit,src,sid,**meta);events.append(ev);ids.append(ev.event_id)
        add(0,typ,entity,zone,value,"celsius" if sid in {"scenario-03","scenario-07"} else None,entity,dwell_minutes=value if sid=="scenario-02" else None)
        if sid=="scenario-01":
            add(2,"dwell","forklift-a",zone,12,"minutes","cam-04");add(3,"telemetry","machine-m17","packaging-line",92,"celsius","temp-m17");add(5,"telemetry","machine-m17","packaging-line",8.4,"mm/s","vibration-m17");add(7,"telemetry","conveyor-c03","packaging-line",42,"units/min","throughput-c03");add(9,"machine_state","machine-m17","packaging-line",0,"state","state-m17",state="stopped");add(10,"worker_activity","worker-204","packaging-line",None,None,"cam-05",movement="unusual")
        elif sid=="scenario-03": add(2,"telemetry","machine-m17",zone,8.0,"mm/s","vibration-m17")
        elif sid=="scenario-06": add(-3,"occupancy","forklift-a","warehouse-a",9,"vehicles","occupancy-zone-c")
        elif sid=="scenario-08": add(1,"machine_state","machine-m17","packaging-line",1,"state","state-m17",state="running")
        truth.append(GroundTruth(scenario_id=sid,event_ids=ids,anomalous=True,category=sid.replace("scenario-","scenario_"),root_cause={"scenario-01":"vehicle/equipment interaction","scenario-03":"mechanical failure","scenario-07":"sensor malfunction","scenario-08":"safety procedure violation"}.get(sid,"operational deviation"),alternatives=["sensor malfunction"],severity="critical" if sid in {"scenario-01","scenario-03","scenario-08"} else "elevated",requires_operator_action=sid!="scenario-07"))
    return sorted(events,key=lambda e:e.timestamp),truth
