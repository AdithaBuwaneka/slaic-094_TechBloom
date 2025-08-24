from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, time
from enum import Enum

from app.models.transport_data import Location, TransportMode


class TravelPurpose(str, Enum):
    COMMUTE = "commute"
    BUSINESS = "business"
    LEISURE = "leisure"
    SHOPPING = "shopping"
    MEDICAL = "medical"
    EDUCATION = "education"
    SOCIAL = "social"
    OTHER = "other"


class TimeFlexibility(str, Enum):
    RIGID = "rigid"          # Must arrive at exact time
    MODERATE = "moderate"    # 15-30 min flexibility
    FLEXIBLE = "flexible"    # 1+ hour flexibility
    VERY_FLEXIBLE = "very_flexible"  # Anytime today


class BudgetSensitivity(str, Enum):
    VERY_HIGH = "very_high"  # Every rupee matters
    HIGH = "high"            # Price conscious
    MODERATE = "moderate"    # Balanced approach
    LOW = "low"              # Convenience over cost
    VERY_LOW = "very_low"    # Cost not a factor


class ComfortPreference(str, Enum):
    BASIC = "basic"          # Just get there
    STANDARD = "standard"    # Normal comfort expected
    PREMIUM = "premium"      # High comfort priority
    LUXURY = "luxury"        # Best available


class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    age_group: Optional[str] = None  # "18-25", "26-35", etc.
    occupation: Optional[str] = None
    home_location: Optional[Location] = None
    work_location: Optional[Location] = None
    
    # Core preferences
    preferred_modes: List[TransportMode] = []
    avoided_modes: List[TransportMode] = []
    budget_sensitivity: BudgetSensitivity = BudgetSensitivity.MODERATE
    comfort_preference: ComfortPreference = ComfortPreference.STANDARD
    time_flexibility: TimeFlexibility = TimeFlexibility.MODERATE
    
    # Accessibility needs
    wheelchair_required: bool = False
    visual_assistance_needed: bool = False
    hearing_assistance_needed: bool = False
    mobility_assistance_needed: bool = False
    
    # Travel patterns
    typical_commute_times: Dict[str, List[str]] = {}  # {"monday": ["08:00", "17:30"]}
    frequent_destinations: List[Location] = []
    max_walking_distance_meters: int = 800
    max_acceptable_transfers: int = 2
    
    # Dynamic preferences
    weather_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    crowd_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    punctuality_importance: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Learning metadata
    profile_created: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    trips_taken: int = 0
    preferences_learned: bool = False


class TravelHistory(BaseModel):
    trip_id: str
    user_id: str
    origin: Location
    destination: Location
    departure_time: datetime
    arrival_time: datetime
    actual_duration_minutes: int
    chosen_route_id: str
    transport_modes_used: List[TransportMode]
    total_cost: float
    purpose: TravelPurpose
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    weather_condition: Optional[str] = None
    rush_hour: bool = False
    with_luggage: bool = False
    group_size: int = 1
    trip_date: datetime = Field(default_factory=datetime.utcnow)


class TravelPreferences(BaseModel):
    """Context-aware travel preferences for a specific journey"""
    
    user_id: str
    context: Dict[str, Any] = {}  # Current context (weather, time, purpose, etc.)
    
    # Weighted importance scores (0.0 to 1.0)
    time_importance: float = 0.4
    cost_importance: float = 0.3
    comfort_importance: float = 0.15
    reliability_importance: float = 0.15
    
    # Mode preferences (dynamic based on context)
    mode_preferences: Dict[TransportMode, float] = {}  # -1.0 to 1.0
    
    # Journey constraints
    max_budget: Optional[float] = None
    max_duration_minutes: Optional[int] = None
    arrival_deadline: Optional[datetime] = None
    departure_flexibility_minutes: int = 15
    
    # Contextual factors
    weather_impact_factor: float = 0.0  # -0.5 to 0.5
    rush_hour_factor: float = 0.0       # -0.3 to 0.3
    luggage_factor: float = 0.0         # -0.2 to 0.2
    group_factor: float = 0.0           # -0.1 to 0.3
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizationInsights(BaseModel):
    """Insights generated from user behavior analysis"""
    
    user_id: str
    
    # Travel patterns
    most_common_routes: List[Dict[str, Any]] = []
    peak_travel_times: List[str] = []  # ["08:00-09:00", "17:30-18:30"]
    preferred_days: List[str] = []     # ["monday", "wednesday"]
    
    # Mode usage patterns
    mode_usage_frequency: Dict[TransportMode, float] = {}
    mode_satisfaction_scores: Dict[TransportMode, float] = {}
    
    # Cost patterns
    average_trip_cost: float = 0.0
    budget_adherence_rate: float = 0.0  # How often stays within budget
    cost_sensitivity_score: float = 0.5
    
    # Time patterns  
    average_trip_duration: float = 0.0
    on_time_performance: float = 0.0  # How often arrives on time
    time_flexibility_score: float = 0.5
    
    # Comfort patterns
    comfort_vs_cost_ratio: float = 0.5  # Willingness to pay for comfort
    transfer_tolerance: float = 0.5     # Comfort with transfers
    walking_tolerance: float = 0.5      # Comfort with walking
    
    # Reliability patterns
    reliability_importance_score: float = 0.7
    disruption_adaptation_score: float = 0.5  # How well adapts to disruptions
    
    # Seasonal/contextual patterns
    weather_impact_patterns: Dict[str, float] = {}  # {"rainy": -0.3, "sunny": 0.1}
    time_of_day_patterns: Dict[str, float] = {}     # {"morning": 0.2, "evening": -0.1}
    
    # Learning confidence
    prediction_confidence: float = Field(default=0.1, ge=0.0, le=1.0)
    data_points_analyzed: int = 0
    
    insights_generated: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PersonalizationRecommendation(BaseModel):
    """Personalized recommendation for a specific journey request"""
    
    recommendation_id: str
    user_id: str
    request_context: Dict[str, Any]
    
    # Personalization factors applied
    personalization_factors: Dict[str, Any] = {}
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Customized route rankings
    personalized_route_scores: Dict[str, float] = {}
    reasoning: List[str] = []  # Human-readable explanations
    
    # Adaptive suggestions
    alternative_suggestions: List[str] = []
    learning_opportunities: List[str] = []  # What system can learn from this trip
    
    # Contextual adaptations
    weather_adaptations: List[str] = []
    time_adaptations: List[str] = []
    cost_adaptations: List[str] = []
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class LearningEvent(BaseModel):
    """Event that can be used for learning user preferences"""
    
    event_id: str
    user_id: str
    event_type: str  # "route_chosen", "rating_given", "preference_changed", etc.
    event_data: Dict[str, Any]
    confidence_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    learning_value: float = Field(default=0.0, ge=-1.0, le=1.0)  # Positive/negative learning
    
    context_at_event: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PersonalizationMetrics(BaseModel):
    """Metrics for evaluating personalization effectiveness"""
    
    user_id: str
    evaluation_period_days: int
    
    # Recommendation accuracy
    recommendation_acceptance_rate: float = Field(ge=0.0, le=1.0)
    user_satisfaction_trend: float = Field(ge=-1.0, le=1.0)  # Improving or declining
    prediction_accuracy_score: float = Field(ge=0.0, le=1.0)
    
    # Learning effectiveness
    preference_stability_score: float = Field(ge=0.0, le=1.0)  # How stable preferences are
    adaptation_speed_score: float = Field(ge=0.0, le=1.0)     # How quickly learns changes
    context_awareness_score: float = Field(ge=0.0, le=1.0)    # Context understanding
    
    # User engagement
    active_feedback_rate: float = Field(ge=0.0, le=1.0)       # How often gives feedback
    preference_exploration_rate: float = Field(ge=0.0, le=1.0) # Tries new options
    system_trust_score: float = Field(ge=0.0, le=1.0)         # Trust in recommendations
    
    metrics_calculated: datetime = Field(default_factory=datetime.utcnow)


class PreferenceUpdateRequest(BaseModel):
    """Request to update user preferences based on feedback"""
    
    user_id: str
    update_type: str  # "explicit", "implicit", "correction"
    
    # What to update
    preference_changes: Dict[str, Any] = {}
    context_when_updated: Dict[str, Any] = {}
    
    # Learning parameters
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Feedback source
    feedback_source: str = "user"  # "user", "behavior", "system"
    feedback_data: Optional[Dict[str, Any]] = None
    
    requested_at: datetime = Field(default_factory=datetime.utcnow)