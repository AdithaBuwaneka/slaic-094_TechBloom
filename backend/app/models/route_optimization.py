from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import math

from app.models.transport_data import Location, TransportMode, RouteData


class OptimizationCriteria(str, Enum):
    TIME = "time"
    COST = "cost"
    COMFORT = "comfort"
    RELIABILITY = "reliability"
    ENVIRONMENTAL = "environmental"


class TransferPoint(BaseModel):
    location: Location
    from_route_id: str
    to_route_id: str
    transfer_time_minutes: int
    transfer_distance_meters: int
    facilities: List[str] = []  # ["escalator", "elevator", "shelter", etc.]
    accessibility_score: float = Field(ge=0.0, le=1.0, default=0.8)


class RouteSegment(BaseModel):
    route_id: str
    transport_mode: TransportMode
    from_stop: str
    to_stop: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    distance_km: float
    fare: float
    operator: str
    reliability_score: float = Field(ge=0.0, le=1.0)
    comfort_score: float = Field(ge=0.0, le=1.0, default=0.7)
    occupancy_level: str = "unknown"  # low, medium, high, full


class OptimizedRoute(BaseModel):
    route_id: str
    total_duration_minutes: int
    total_cost: float
    total_distance_km: float
    segments: List[RouteSegment]
    transfers: List[TransferPoint] = []
    
    # Scoring metrics
    time_score: float = Field(ge=0.0, le=1.0)
    cost_score: float = Field(ge=0.0, le=1.0) 
    comfort_score: float = Field(ge=0.0, le=1.0)
    reliability_score: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    
    # Journey details
    departure_time: datetime
    arrival_time: datetime
    total_walking_distance_meters: int = 0
    number_of_transfers: int = 0
    
    # Environmental impact
    carbon_footprint_kg: Optional[float] = None
    
    # Accessibility
    wheelchair_accessible: bool = True
    accessibility_score: float = Field(ge=0.0, le=1.0, default=0.8)


class RouteOptimizationRequest(BaseModel):
    origin: Location
    destination: Location
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    preferred_modes: List[TransportMode] = []
    excluded_modes: List[TransportMode] = []
    optimization_criteria: List[OptimizationCriteria] = [OptimizationCriteria.TIME]
    criteria_weights: Dict[str, float] = {}
    max_walking_distance_meters: int = 1000
    max_transfers: int = 3
    wheelchair_accessible_only: bool = False
    budget_limit: Optional[float] = None
    max_journey_time_minutes: Optional[int] = None


class RouteAlternatives(BaseModel):
    request_id: str
    origin: Location
    destination: Location
    
    # Route options
    fastest_route: Optional[OptimizedRoute] = None
    cheapest_route: Optional[OptimizedRoute] = None
    most_comfortable_route: Optional[OptimizedRoute] = None
    most_reliable_route: Optional[OptimizedRoute] = None
    recommended_route: Optional[OptimizedRoute] = None
    
    all_routes: List[OptimizedRoute] = []
    
    # Analysis summary
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: float
    routes_analyzed: int
    data_sources_used: List[str] = []
    
    # Feasibility analysis
    is_journey_feasible: bool = True
    feasibility_issues: List[str] = []
    alternative_suggestions: List[str] = []


class OptimizationMetrics(BaseModel):
    """Metrics for evaluating route optimization performance"""
    
    # Time-based metrics
    avg_journey_time_minutes: float
    min_journey_time_minutes: float
    max_journey_time_minutes: float
    
    # Cost metrics  
    avg_cost: float
    min_cost: float
    max_cost: float
    
    # Reliability metrics
    avg_reliability_score: float
    on_time_probability: float
    
    # Transfer metrics
    avg_transfers: float
    max_walking_distance: int
    
    # Coverage metrics
    transport_modes_used: List[TransportMode]
    operators_covered: List[str]
    
    # Quality metrics
    route_diversity_score: float = Field(ge=0.0, le=1.0)
    optimization_confidence: float = Field(ge=0.0, le=1.0)