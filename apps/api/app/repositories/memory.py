from datetime import datetime, timezone
from app.core.config import DATASET_VERSION, settings
from app.domain.models import OperationalEvent
from app.ml.baselines import build_baselines
from app.simulation.generator import generate_events
from app.simulation.scenarios import SCENARIOS
from app.simulation.world import ENTITIES, FACILITY, SENSORS, ZONES
from app.reasoning.incidents import build_incidents

class DemoRepository:
    def __init__(self, seed: int=settings.demo_seed): self.reset(seed)
    def reset(self, seed: int) -> None:
        self.seed=seed; self.events,self.ground_truth=generate_events(seed); self.baselines=build_baselines([e for e in self.events if not e.scenario_id]); self.incidents=build_incidents(self.events); self.feedback=[]; self.tick=0; self.running=False
    def rebuild_incidents(self): self.incidents=build_incidents(self.events); return list(self.incidents.values())
    def filtered_events(self, start: datetime|None=None,end:datetime|None=None,entity:str|None=None,zone:str|None=None,event_type:str|None=None,source:str|None=None) -> list[OperationalEvent]:
        return [e for e in self.events if (not start or e.timestamp>=start) and (not end or e.timestamp<=end) and (not entity or e.entity_id==entity) and (not zone or e.zone_id==zone) and (not event_type or e.event_type==event_type) and (not source or e.source_id==source)]
    def metrics(self) -> dict: return {"dataset_version":DATASET_VERSION,"event_count":len(self.events),"scenario_count":len(SCENARIOS),"injected_anomalies":sum(len(t.event_ids) for t in self.ground_truth),"seed":self.seed}
    def detected_anomalies(self) -> list[dict]:
        """Inference uses observations/ranges only; ground truth remains evaluation-only."""
        results=[]
        for event in self.events:
            components=[]
            if event.entity_id in {"forklift-a","forklift-b","tugger-t01"} and event.zone_id=="restricted-zone-c": components.append("restricted_zone_rule")
            if event.source_id=="temp-m17" and (event.value or 0)>82: components.append("temperature_deviation")
            if event.source_id=="vibration-m17" and (event.value or 0)>5: components.append("vibration_deviation")
            if event.source_id=="throughput-c03" and event.timestamp.hour in range(7,22) and (event.value or 999)<60: components.append("throughput_deviation")
            if components: results.append({"event_id":event.event_id,"timestamp":event.timestamp,"entity_id":event.entity_id,"zone_id":event.zone_id,"detectors":components,"score":min(100,55+len(components)*20)})
        return results
    def state(self) -> dict: return {"status":"running" if self.running else ("ready" if self.tick==0 else "paused"),"running":self.running,"tick":self.tick,"events_processed":self.tick,"simulated_at":self.events[min(self.tick,len(self.events)-1)].timestamp}
    def advance(self) -> dict:
        if self.running: self.tick=min(len(self.events)-1,self.tick+25)
        return self.state()
    def recent_events(self,limit:int=20): return self.events[max(0,self.tick-limit):self.tick]

repository=DemoRepository()
