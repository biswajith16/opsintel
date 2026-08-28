from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field

class EntityType(str, Enum): worker="worker"; vehicle="vehicle"; machine="machine"; camera="camera"; sensor="sensor"
class Severity(str, Enum): normal="normal"; watch="watch"; elevated="elevated"; critical="critical"

class Facility(BaseModel): id: str; name: str; timezone: str
class Zone(BaseModel): id: str; facility_id: str; name: str; zone_type: str; adjacent_zone_ids: list[str] = []
class Entity(BaseModel): id: str; facility_id: str; type: EntityType; label: str; home_zone_id: str | None = None; status: str = "active"
class Sensor(BaseModel): id: str; entity_id: str | None = None; zone_id: str | None = None; kind: str; unit: str; cadence_seconds: int
class OperationalEvent(BaseModel):
    event_id: str; timestamp: datetime; facility_id: str; zone_id: str | None = None; entity_id: str | None = None; source_id: str | None = None
    event_type: str; event_subtype: str | None = None; value: float | None = None; unit: str | None = None; metadata: dict[str, Any] = Field(default_factory=dict); scenario_id: str | None = None
class BehavioralBaseline(BaseModel): subject_id: str; baseline_type: str; feature: str; median: float | None = None; mad: float | None = None; p05: float | None = None; p95: float | None = None; values: dict[str, float] = Field(default_factory=dict)
class ScoreComponent(BaseModel): type: str; score: float; reason: str
class AnomalyScore(BaseModel): score: float; severity: Severity; components: list[ScoreComponent]; violated_baselines: list[str]
class Anomaly(BaseModel): id: str; event_id: str; score: AnomalyScore; detector: str
class Evidence(BaseModel): id: str; incident_id: str; event_id: str | None = None; relation: str; weight: float; explanation: str
class EvidenceStrength(str, Enum): weak="weak"; moderate="moderate"; strong="strong"
class Hypothesis(BaseModel): hypothesis_id: str; title: str; confidence: float; supporting_evidence_ids: list[str] = []; contradicting_evidence_ids: list[str] = []; reason_summary: str
class Incident(BaseModel):
    incident_id: str; title: str; summary: str; facility_id: str; primary_zone_id: str | None; start_time: datetime; end_time: datetime; severity: Severity; risk_score: float; status: Literal["open","investigating","confirmed","false_positive","resolved"]="open"; anomaly_ids: list[str]=[]; event_ids: list[str]=[]; entity_ids: list[str]=[]; sensor_ids: list[str]=[]; evidence_ids: list[str]=[]; leading_hypothesis: str; root_cause_confidence: float; candidate_hypotheses: list[Hypothesis]=[]; recommendation: str; created_at: datetime
class Evidence(BaseModel):
    evidence_id: str; type: str; source_id: str | None=None; event_id: str | None=None; entity_id: str | None=None; zone_id: str | None=None; timestamp: datetime | None=None; claim_supported: str; relationship_type: str; strength: EvidenceStrength; summary: str
class GraphNode(BaseModel): id: str; type: str; label: str; attributes: dict[str, Any] = Field(default_factory=dict)
class GraphEdge(BaseModel): source: str; target: str; relationship_type: str; score: float; reason: str
class GraphDTO(BaseModel): nodes: list[GraphNode]; edges: list[GraphEdge]
class CorrelationScore(BaseModel): score: float; temporal_score: float; spatial_score: float; shared_entity_score: float; dependency_score: float; semantic_score: float; sequence_score: float; reason: str
class InvestigationTrace(BaseModel): id: str; incident_id: str; tool: str; input_summary: str; result_summary: str; occurred_at: datetime
class OperatorFeedback(BaseModel): id: str; incident_id: str; action: str; note: str | None = None
class ScenarioDefinition(BaseModel): id: str; name: str; description: str; affected_entity_ids: list[str]; affected_zone_ids: list[str]; sensor_kinds: list[str]; expected_severity: str; root_cause: str; alternative_hypotheses: list[str]
class GroundTruth(BaseModel): scenario_id: str; event_ids: list[str]; anomalous: bool; category: str; root_cause: str; alternatives: list[str]; severity: str; requires_operator_action: bool
class WhatIfRequest(BaseModel): entity_id: str; zone_id: str; dwell_minutes: float = Field(ge=0, le=240); temperature_c: float | None = None; vibration: float | None = None; production_slowdown: bool = False; hour: int = Field(ge=0, le=23)
