from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from .transport_data import TransportMode, Location


class DisruptionType(str, Enum):
    DELAY = "delay"
    CANCELLATION = "cancellation"
    ROUTE_CHANGE = "route_change"
    MECHANICAL_ISSUE = "mechanical_issue"
    WEATHER = "weather"
    STRIKE = "strike"
    ACCIDENT = "accident"
    TRAFFIC_JAM = "traffic_jam"
    ROAD_CLOSURE = "road_closure"
    EMERGENCY = "emergency"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DisruptionStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    MONITORING = "monitoring"
    PLANNED = "planned"


class AffectedArea(BaseModel):
    location: Location
    radius_km: float = Field(..., gt=0)
    affected_stops: Optional[List[str]] = None
    affected_routes: Optional[List[str]] = None


class DisruptionAlert(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    disruption_type: DisruptionType
    severity: SeverityLevel
    status: DisruptionStatus
    transport_modes: List[TransportMode]
    affected_areas: List[AffectedArea]
    start_time: datetime
    estimated_end_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    source: str  # Who reported this disruption
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ImpactAssessment(BaseModel):
    disruption_id: str
    estimated_delay_minutes: int
    affected_passenger_count: Optional[int] = None
    alternative_routes_available: bool = True
    additional_cost_impact: Optional[float] = None
    accessibility_impact: Optional[str] = None
    recommendations: List[str] = []


class ContingencyPlan(BaseModel):
    disruption_type: DisruptionType
    severity: SeverityLevel
    actions: List[str]
    alternative_routes: List[str] = []
    estimated_additional_time: Optional[int] = None
    estimated_additional_cost: Optional[float] = None
    emergency_contacts: List[Dict[str, str]] = []
    special_instructions: Optional[str] = None


class DisruptionMonitoringRequest(BaseModel):
    origin: Location
    destination: Location
    planned_departure: datetime
    transport_modes: Optional[List[TransportMode]] = None
    monitor_duration_hours: int = Field(default=24, ge=1, le=72)


class DisruptionResponse(BaseModel):
    disruptions: List[DisruptionAlert]
    impact_assessment: Optional[ImpactAssessment] = None
    contingency_plans: List[ContingencyPlan] = []
    monitoring_enabled: bool = False
    next_update_at: Optional[datetime] = None


class CreateDisruptionRequest(BaseModel):
    title: str
    description: str
    disruption_type: DisruptionType
    severity: SeverityLevel
    transport_modes: List[TransportMode]
    affected_areas: List[AffectedArea]
    estimated_duration_hours: Optional[int] = None
    source: str = "system"


class UpdateDisruptionRequest(BaseModel):
    disruption_id: str
    status: Optional[DisruptionStatus] = None
    severity: Optional[SeverityLevel] = None
    description: Optional[str] = None
    estimated_end_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None


class DisruptionQuery(BaseModel):
    location: Optional[Location] = None
    radius_km: Optional[float] = Field(default=10.0, gt=0)
    transport_modes: Optional[List[TransportMode]] = None
    severity_levels: Optional[List[SeverityLevel]] = None
    disruption_types: Optional[List[DisruptionType]] = None
    active_only: bool = True
    include_planned: bool = False