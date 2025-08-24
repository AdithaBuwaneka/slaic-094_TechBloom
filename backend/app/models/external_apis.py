from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, time
from enum import Enum

from .transport_data import Location, TransportMode


class APIProvider(str, Enum):
    SLTB = "sltb"  # Sri Lanka Transport Board
    SRI_LANKA_RAILWAYS = "sri_lanka_railways" 
    WEATHER_API = "openweather"
    TRAFFIC_API = "google_traffic"
    GOOGLE_MAPS = "google_maps"
    UBER_API = "uber"
    PICKME_API = "pickme"
    AIRPORT_API = "airport_express"


class APIStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class DataType(str, Enum):
    SCHEDULES = "schedules"
    FARES = "fares"
    REAL_TIME = "real_time"
    WEATHER = "weather"
    TRAFFIC = "traffic"
    ROUTES = "routes"
    STOPS = "stops"


class ExternalAPIConfig(BaseModel):
    api_id: str
    provider: APIProvider
    name: str
    description: str
    
    # Connection details
    base_url: HttpUrl
    api_key: Optional[str] = None
    auth_type: str = "api_key"  # api_key, oauth, basic, none
    headers: Dict[str, str] = {}
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    concurrent_requests: int = 5
    
    # Data capabilities
    supported_data_types: List[DataType] = []
    coverage_areas: List[str] = []  # districts, provinces
    
    # Status and reliability
    status: APIStatus = APIStatus.ACTIVE
    reliability_score: float = Field(default=0.8, ge=0.0, le=1.0)
    average_response_time_ms: int = 500
    
    # Configuration
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_duration_minutes: int = 15
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    last_successful_call: Optional[datetime] = None


class APIEndpoint(BaseModel):
    endpoint_id: str
    api_id: str
    name: str
    path: str
    method: str = "GET"
    
    # Endpoint details
    description: str
    data_type: DataType
    required_params: List[str] = []
    optional_params: List[str] = []
    
    # Response format
    response_format: str = "json"  # json, xml, csv
    response_schema: Optional[Dict[str, Any]] = None
    
    # Performance
    cache_duration_minutes: int = 15
    timeout_seconds: int = 15
    
    # Status
    is_active: bool = True
    last_tested: Optional[datetime] = None
    success_rate: float = Field(default=0.95, ge=0.0, le=1.0)


class APIRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    api_id: str
    endpoint_id: str
    
    # Request details
    method: str = "GET"
    url: str
    headers: Dict[str, str] = {}
    params: Dict[str, Any] = {}
    body: Optional[Dict[str, Any]] = None
    
    # Timing
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    timeout_seconds: int = 30
    
    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_source: str = "agent"  # agent, user, system


class APIResponse(BaseModel):
    response_id: str = Field(default_factory=lambda: f"resp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    request_id: str
    
    # Response details
    status_code: int
    success: bool
    data: Optional[Dict[str, Any]] = None
    raw_response: Optional[str] = None
    
    # Error details
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Performance metrics
    response_time_ms: int
    data_size_bytes: int = 0
    
    # Timestamps
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Cache info
    from_cache: bool = False
    cache_expires_at: Optional[datetime] = None


class WeatherData(BaseModel):
    location: Location
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Current conditions
    temperature_celsius: float
    humidity_percent: int = Field(ge=0, le=100)
    weather_condition: str  # sunny, cloudy, rainy, etc.
    wind_speed_kmh: float = 0.0
    visibility_km: float = 10.0
    
    # Precipitation
    rainfall_mm: float = 0.0
    chance_of_rain_percent: int = Field(default=0, ge=0, le=100)
    
    # Travel impact
    travel_advisory: Optional[str] = None
    impact_on_transport: str = "none"  # none, minimal, moderate, severe
    
    # Forecast
    forecast_hours: int = 24
    hourly_forecast: List[Dict[str, Any]] = []


class TrafficData(BaseModel):
    route_segment: str
    start_location: Location
    end_location: Location
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Traffic conditions
    traffic_level: str = "normal"  # light, normal, heavy, severe
    average_speed_kmh: float = 50.0
    travel_time_minutes: int
    delay_minutes: int = 0
    
    # Incidents
    incidents: List[Dict[str, Any]] = []
    road_closures: List[str] = []
    
    # Alternative routes
    alternative_routes_available: bool = False
    recommended_alternatives: List[str] = []


class PublicTransportSchedule(BaseModel):
    route_id: str
    service_id: str
    operator: str
    transport_mode: TransportMode
    
    # Route details
    route_name: str
    direction: str
    start_stop: str
    end_stop: str
    
    # Schedule
    departure_times: List[time] = []
    frequency_minutes: Optional[int] = None
    operating_days: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    # Real-time data
    real_time_updates: bool = False
    current_delays: List[Dict[str, Any]] = []
    next_departure: Optional[datetime] = None
    
    # Validity
    valid_from: datetime
    valid_until: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class FareInformation(BaseModel):
    route_id: str
    operator: str
    transport_mode: TransportMode
    
    # Fare structure
    base_fare: float
    distance_based: bool = False
    fare_per_km: Optional[float] = None
    
    # Passenger types
    adult_fare: float
    child_fare: Optional[float] = None
    senior_fare: Optional[float] = None
    student_fare: Optional[float] = None
    
    # Discounts and passes
    available_passes: List[Dict[str, Any]] = []
    bulk_discounts: List[Dict[str, Any]] = []
    
    # Payment methods
    accepted_payment_methods: List[str] = ["cash"]
    digital_payment_available: bool = False
    
    # Validity
    effective_date: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class RealTimeVehiclePosition(BaseModel):
    vehicle_id: str
    route_id: str
    operator: str
    transport_mode: TransportMode
    
    # Position
    current_location: Location
    heading_degrees: Optional[float] = None
    speed_kmh: Optional[float] = None
    
    # Status
    service_status: str = "in_service"  # in_service, out_of_service, maintenance
    occupancy_level: str = "unknown"  # empty, few_seats, standing_room, full
    next_stop_id: Optional[str] = None
    next_stop_eta: Optional[datetime] = None
    
    # Real-time info
    delay_minutes: int = 0
    last_stop_departure: Optional[datetime] = None
    
    # Data quality
    gps_accuracy_meters: float = 10.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_age_seconds: int = 0


class APIIntegrationStatus(BaseModel):
    integration_id: str = Field(default_factory=lambda: f"int_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Overall status
    total_apis: int = 0
    active_apis: int = 0
    failed_apis: int = 0
    
    # Performance metrics
    total_requests_today: int = 0
    successful_requests_today: int = 0
    failed_requests_today: int = 0
    average_response_time_ms: float = 0.0
    
    # API status breakdown
    api_statuses: Dict[str, APIStatus] = {}
    last_health_check: datetime = Field(default_factory=datetime.utcnow)
    
    # Data freshness
    oldest_cached_data_minutes: int = 0
    real_time_coverage_percent: float = 0.0
    
    # Alerts
    active_alerts: List[str] = []
    system_warnings: List[str] = []


class ExternalDataSource(BaseModel):
    source_id: str
    name: str
    provider: APIProvider
    data_types: List[DataType]
    
    # Connection details
    api_config: ExternalAPIConfig
    endpoints: List[APIEndpoint] = []
    
    # Data mapping
    field_mappings: Dict[str, str] = {}  # external_field -> internal_field
    data_transformations: Dict[str, Any] = {}
    
    # Sync settings
    sync_frequency_minutes: int = 15
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    
    # Quality metrics
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0)
    completeness_percent: float = Field(default=90.0, ge=0.0, le=100.0)
    accuracy_score: float = Field(default=0.9, ge=0.0, le=1.0)


class APIUsageStatistics(BaseModel):
    api_id: str
    period_start: datetime
    period_end: datetime
    
    # Request statistics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_responses: int = 0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    min_response_time_ms: int = 0
    max_response_time_ms: int = 0
    timeout_count: int = 0
    
    # Error analysis
    error_types: Dict[str, int] = {}
    status_code_breakdown: Dict[str, int] = {}
    
    # Usage patterns
    requests_by_hour: Dict[str, int] = {}
    peak_usage_hour: Optional[int] = None
    
    # Data volume
    total_data_transferred_mb: float = 0.0
    largest_response_bytes: int = 0
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class IntegrationHealthCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: f"health_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    
    # Check details
    api_id: str
    endpoint_id: Optional[str] = None
    check_type: str = "connectivity"  # connectivity, data_quality, performance
    
    # Results
    status: str = "passed"  # passed, failed, warning
    response_time_ms: int = 0
    details: Dict[str, Any] = {}
    
    # Issues found
    issues: List[str] = []
    recommendations: List[str] = []
    
    # Timing
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    next_check_at: Optional[datetime] = None