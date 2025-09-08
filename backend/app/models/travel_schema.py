from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class RouteInfo(BaseModel):
    route_id: str
    duration: int  # minutes
    distance: float  # km
    steps: List[Dict]
    polyline: str
    fare_estimate: Optional[float] = None
    mode_details: Dict[str, Any] = {}
    # Add missing fields:
    transit_modes: Optional[List[str]] = []
    transfers: Optional[int] = 0
    walking_distance: Optional[float] = 0.0
    category: Optional[str] = "unknown"

class DisruptionInfo(BaseModel):
    disruption_id: str
    location: str
    type: str  # traffic, construction, weather, etc.
    severity: str  # low, medium, high
    reported_by: str
    timestamp: datetime
    affected_routes: List[str]
    description: str

class UserPreferences(BaseModel):
    user_id: str
    preferred_transit_modes: List[str] = ["bus", "train"]
    max_walking_distance: float = 1.0  # km
    budget_preference: str = "medium"  # low, medium, high
    time_vs_cost_weight: float = 0.5  # 0=cost priority, 1=time priority
    comfort_preference: float = 0.7  # 0=basic, 1=premium
    accessibility_needs: List[str] = []
    avoid_preferences: List[str] = []  # tolls, highways, etc.
    last_updated: datetime = Field(default_factory=datetime.now)

class TravelState(BaseModel):
    # Input Parameters
    request_id: str = Field(default_factory=lambda: f"req_{datetime.now().timestamp()}")
    source: str
    destination: str
    mode: str  # driving, two_wheeler, transit, uber
    preferred_transit: Optional[str] = None
    user_id: str
    departure_time: Optional[datetime] = None
    
    # Route Data
    primary_routes: List[Dict[str, Any]] = []
    supplementary_routes: List[Dict[str, Any]] = []
    transit_routes: List[Dict[str, Any]] = []
    
    # Fare Information
    fare_data: Dict[str, Any] = {}
    last_mile_options: List[Dict] = []
    total_fare_estimate: Optional[float] = None
    
    # User Preferences
    current_user_preferences: Optional[UserPreferences] = None
    updated_user_preferences: Optional[UserPreferences] = None
    preference_weight_factors: Dict[str, Any] = {}
    
    # Local Knowledge
    route_context_data: List[Dict] = []
    poi_information: List[Dict] = []
    local_insights: Dict[str, Any] = {}
    weather_data: Dict[str, Any] = {}
    search_summary: Optional[Dict[str, Any]] = None
    
    # Disruption Data
    current_disruptions: List[DisruptionInfo] = []
    alternative_routes_due_disruptions: List[Dict[str, Any]] = []
    real_time_updates: List[Dict] = []
    ai_disruption_analysis: Optional[Dict[str, Any]] = None
    
    # Final Output
    recommended_routes: List[Dict] = []
    route_rankings: Dict[str, float] = {}
    final_response: Dict[str, Any] = {}
    
    # Process Tracking
    agents_completed: List[str] = []
    current_step: str = "input_processing"
    errors: List[Dict] = []
    processing_start_time: datetime = Field(default_factory=datetime.now)
    
    # Configuration
    config: Dict[str, Any] = {
        "max_routes": 5,
        "max_walking_distance": 2.0,
        "disruption_check_enabled": True,
        "local_knowledge_enabled": True
    }