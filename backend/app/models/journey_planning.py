from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, time
from enum import Enum

from .transport_data import Location, TransportMode, TransportOperator


class JourneyType(str, Enum):
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"
    MULTI_STOP = "multi_stop"


class TravelTime(str, Enum):
    NOW = "now"
    DEPART_AT = "depart_at"
    ARRIVE_BY = "arrive_by"


class JourneyPriority(str, Enum):
    FASTEST = "fastest"
    CHEAPEST = "cheapest"
    MOST_COMFORTABLE = "most_comfortable"
    MOST_ACCESSIBLE = "most_accessible"
    BALANCED = "balanced"


class BookingStatus(str, Enum):
    AVAILABLE = "available"
    BOOKING_REQUIRED = "booking_required"
    FULLY_BOOKED = "fully_booked"
    NOT_AVAILABLE = "not_available"


class JourneyLeg(BaseModel):
    leg_id: str = Field(default_factory=lambda: f"leg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Route details
    transport_mode: TransportMode
    operator: TransportOperator
    route_name: str
    service_number: Optional[str] = None
    
    # Locations
    departure_location: Location
    arrival_location: Location
    departure_stop: Optional[str] = None
    arrival_stop: Optional[str] = None
    
    # Timing
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    
    # Distance and travel details
    distance_km: float
    intermediate_stops: List[str] = []
    walking_distance_to_stop: float = 0.0  # km
    walking_distance_from_stop: float = 0.0  # km
    
    # Fare information
    fare_breakdown: Optional[Dict[str, Any]] = None
    
    # Accessibility
    accessibility_info: Optional[Dict[str, Any]] = None
    
    # Booking and availability
    booking_status: BookingStatus = BookingStatus.AVAILABLE
    booking_url: Optional[str] = None
    capacity_info: Optional[str] = None  # empty, moderate, full
    
    # Real-time information
    live_delay_minutes: int = 0
    is_live_data: bool = False
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional information
    notes: List[str] = []
    platform_info: Optional[str] = None


class TransferDetails(BaseModel):
    transfer_id: str = Field(default_factory=lambda: f"transfer_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Transfer location
    location: Location
    stop_name: str
    
    # Timing
    arrival_time: datetime
    departure_time: datetime
    transfer_duration_minutes: int
    
    # Transfer details
    walking_distance_meters: float
    walking_time_minutes: int
    is_same_platform: bool = False
    
    # Accessibility
    accessibility_info: Optional[Dict[str, Any]] = None
    step_free_access: bool = True
    
    # Additional info
    facilities: List[str] = []  # toilets, food, wifi, etc.
    instructions: List[str] = []
    
    # Risk factors
    transfer_risk_level: str = "low"  # low, medium, high
    minimum_transfer_time: int = 5  # minutes


class Journey(BaseModel):
    journey_id: str = Field(default_factory=lambda: f"journey_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Journey overview
    journey_type: JourneyType = JourneyType.ONE_WAY
    origin: Location
    destination: Location
    
    # Journey legs and transfers
    legs: List[JourneyLeg] = []
    transfers: List[TransferDetails] = []
    
    # Overall timing
    departure_time: datetime
    arrival_time: datetime
    total_duration_minutes: int
    total_walking_time_minutes: int = 0
    
    # Distance and cost
    total_distance_km: float
    total_fare: float
    total_fare_breakdown: Optional[Dict[str, Any]] = None
    
    # Journey quality metrics
    comfort_score: float = Field(ge=0.0, le=10.0)
    reliability_score: float = Field(ge=0.0, le=10.0)
    accessibility_score: float = Field(ge=0.0, le=10.0)
    environmental_score: float = Field(ge=0.0, le=10.0)
    overall_score: float = Field(ge=0.0, le=10.0)
    
    # Accessibility information
    is_wheelchair_accessible: bool = False
    accessibility_warnings: List[str] = []
    
    # Disruptions and alerts
    active_disruptions: List[Dict[str, Any]] = []
    journey_alerts: List[str] = []
    
    # Booking information
    requires_booking: bool = False
    booking_urls: List[str] = []
    booking_deadline: Optional[datetime] = None
    
    # Real-time status
    is_real_time: bool = False
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metadata
    journey_tags: List[str] = []  # scenic, express, local, etc.
    carbon_footprint_kg: Optional[float] = None
    weather_impact: Optional[str] = None


class JourneyPlanRequest(BaseModel):
    # Basic journey details
    origin: Location
    destination: Location
    journey_type: JourneyType = JourneyType.ONE_WAY
    
    # Timing preferences
    travel_time: TravelTime = TravelTime.NOW
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    return_departure_time: Optional[datetime] = None  # for round trips
    
    # Journey preferences
    priorities: List[JourneyPriority] = [JourneyPriority.BALANCED]
    max_transfers: int = Field(default=3, ge=0, le=5)
    max_walking_distance_km: float = Field(default=1.0, ge=0.1, le=5.0)
    max_journey_time_hours: float = Field(default=8.0, ge=0.5, le=24.0)
    
    # Transport mode preferences
    preferred_modes: List[TransportMode] = []
    excluded_modes: List[TransportMode] = []
    
    # Accessibility requirements
    accessibility_requirements: List[str] = []
    requires_wheelchair_access: bool = False
    
    # User context
    user_id: Optional[str] = None
    language_preference: str = "en"
    
    # Advanced options
    include_alternative_routes: bool = True
    max_alternatives: int = Field(default=5, ge=1, le=10)
    include_carbon_footprint: bool = False
    include_weather_info: bool = False
    
    # Budget constraints
    max_fare: Optional[float] = None
    apply_discounts: bool = True
    
    # Real-time preferences
    prefer_real_time_data: bool = True
    include_disruption_info: bool = True


class JourneyPlanResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Response metadata
    success: bool = True
    message: str = "Journey plan generated successfully"
    processing_time_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Journey results
    recommended_journey: Optional[Journey] = None
    alternative_journeys: List[Journey] = []
    total_journeys_found: int = 0
    
    # Request context
    original_request: JourneyPlanRequest
    
    # Personalization insights
    personalization_applied: bool = False
    personalization_notes: List[str] = []
    
    # System information
    data_sources_used: List[str] = []
    real_time_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Warnings and notices
    journey_warnings: List[str] = []
    system_notices: List[str] = []
    
    # Additional recommendations
    travel_tips: List[str] = []
    local_insights: List[str] = []


class MultiStopJourneyRequest(BaseModel):
    user_id: Optional[str] = None
    waypoints: List[Location] = Field(min_length=3)  # origin + stops + destination
    travel_preferences: Dict[str, Any]  # Changed from JourneyPlanRequest to Dict for flexibility
    optimize_order: bool = False  # optimize waypoint order
    max_total_time_hours: float = Field(default=12.0, ge=1.0, le=24.0)


class BookingRequest(BaseModel):
    journey_id: str
    user_id: str
    
    # Passenger details
    passenger_count: int = Field(default=1, ge=1, le=10)
    passenger_types: Dict[str, int] = {}  # adult, child, senior, student
    
    # Booking preferences
    seat_preferences: List[str] = []  # window, aisle, wheelchair_space
    special_requirements: List[str] = []
    
    # Contact information
    contact_email: str
    contact_phone: Optional[str] = None
    
    # Payment information (placeholder)
    payment_method: str = "cash"  # cash, card, mobile, wallet


class BookingResponse(BaseModel):
    booking_id: str = Field(default_factory=lambda: f"booking_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Booking status
    success: bool
    message: str
    booking_status: str  # confirmed, pending, failed
    
    # Booking details
    journey: Journey
    passenger_details: Dict[str, Any]
    total_fare: float
    
    # Confirmation details
    confirmation_number: Optional[str] = None
    qr_code_url: Optional[str] = None
    booking_reference: Optional[str] = None
    
    # Important information
    cancellation_policy: str = ""
    check_in_requirements: List[str] = []
    
    # Timing
    booking_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TripManagement(BaseModel):
    trip_id: str = Field(default_factory=lambda: f"trip_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    
    # Trip details
    journey: Journey
    booking_details: Optional[BookingResponse] = None
    
    # Trip status
    status: str = "planned"  # planned, active, completed, cancelled
    current_leg_index: int = 0
    
    # Real-time tracking
    live_updates_enabled: bool = True
    notifications_enabled: bool = True
    
    # Trip timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Feedback and rating
    user_rating: Optional[int] = Field(ge=1, le=5)
    user_feedback: Optional[str] = None
    journey_issues: List[str] = []


class JourneySearchFilters(BaseModel):
    # Time filters
    departure_time_range: Optional[tuple[datetime, datetime]] = None
    arrival_time_range: Optional[tuple[datetime, datetime]] = None
    
    # Cost filters
    min_fare: Optional[float] = None
    max_fare: Optional[float] = None
    
    # Duration filters
    max_duration_hours: Optional[float] = None
    max_transfers: Optional[int] = None
    
    # Quality filters
    min_comfort_score: Optional[float] = None
    min_reliability_score: Optional[float] = None
    
    # Accessibility filters
    wheelchair_accessible_only: bool = False
    visual_impairment_friendly: bool = False
    
    # Environmental filters
    low_carbon_only: bool = False
    max_carbon_footprint: Optional[float] = None


class JourneyAnalytics(BaseModel):
    analytics_id: str = Field(default_factory=lambda: f"analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Journey performance
    total_journeys_analyzed: int
    average_duration_minutes: float
    average_cost: float
    average_transfers: float
    
    # Popular routes
    popular_origins: List[tuple[str, int]] = []
    popular_destinations: List[tuple[str, int]] = []
    popular_routes: List[tuple[str, int]] = []
    
    # Transport mode usage
    mode_usage_stats: Dict[str, int] = {}
    
    # Time patterns
    peak_hours: List[int] = []
    peak_days: List[str] = []
    
    # User satisfaction
    average_rating: float = 0.0
    completion_rate: float = 0.0
    
    # Analysis period
    analysis_start: datetime
    analysis_end: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)