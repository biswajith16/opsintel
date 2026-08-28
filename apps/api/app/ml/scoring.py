from app.domain.models import AnomalyScore, ScoreComponent, Severity, WhatIfRequest
from sklearn.ensemble import IsolationForest
import numpy as np

def severity(score: float) -> Severity: return Severity.critical if score>75 else Severity.elevated if score>55 else Severity.watch if score>30 else Severity.normal
def score_what_if(request: WhatIfRequest) -> AnomalyScore:
    components=[]; violations=[]
    if request.entity_id.startswith(("forklift","tugger")) and request.zone_id=="restricted-zone-c": components.append(ScoreComponent(type="restricted_zone_rule",score=100,reason="Vehicle entered Restricted Zone C"));violations.append("restricted zone access")
    if request.dwell_minutes>10: components.append(ScoreComponent(type="dwell_deviation",score=min(100,40+request.dwell_minutes*5),reason="Dwell exceeds the typical operating window"));violations.append("dwell baseline")
    if request.temperature_c is not None and request.temperature_c>80: components.append(ScoreComponent(type="temperature_deviation",score=min(100,(request.temperature_c-70)*4),reason="Temperature exceeds M17 operating range"));violations.append("temperature baseline")
    if request.vibration is not None and request.vibration>4: components.append(ScoreComponent(type="vibration_deviation",score=min(100,(request.vibration-2)*17),reason="Vibration exceeds normal variation"));violations.append("vibration baseline")
    if request.production_slowdown: components.append(ScoreComponent(type="throughput_deviation",score=72,reason="Production throughput is below the expected operating range"));violations.append("throughput baseline")
    if request.hour<6 or request.hour>21: components.append(ScoreComponent(type="time_of_day_deviation",score=75,reason="Activity is outside normal operating hours"));violations.append("activity-hours baseline")
    score=round(min(100,sum(c.score for c in components)/max(1,len(components)) + max(0,len(components)-1)*5),1)
    return AnomalyScore(score=score,severity=severity(score),components=components,violated_baselines=violations)

def isolation_forest_scores(rows: list[tuple[float,float,float]]) -> list[float]:
    """Deterministic multivariate telemetry novelty scores for numerical rows only."""
    if len(rows) < 5: return [0.0 for _ in rows]
    matrix=np.asarray(rows,dtype=float)
    model=IsolationForest(contamination=0.08,random_state=20260828,n_estimators=64)
    model.fit(matrix)
    raw=-model.score_samples(matrix)
    span=max(float(raw.max()-raw.min()),1e-9)
    return [round(float((v-raw.min())/span*100),2) for v in raw]
