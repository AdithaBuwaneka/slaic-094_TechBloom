from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class TransportMode(str, Enum):
    BUS = "bus"
    TRAIN = "train"
    TAXI = "taxi"
    WALKING = "walking"
    TRAM = "tram"


class DataSource(str, Enum):
    RAILWAYS_API = "sri_lanka_railways"
    BUS_API = "bus_operator"
    WEATHER_API = "weather_service"
    TRAFFIC_API = "traffic_service"
    GTFS_FEED = "gtfs"
    COMMUNITY = "community"
    MANUAL = "manual"


class TransportOperator(BaseModel):
    operator_id: str
    name: str
    type: str  # bus, train, taxi, etc.
    contact_info: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    is_active: bool = True


class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None  # Added name field for waypoint identification
    address: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None


class RoutePoint(BaseModel):
    location: Location
    stop_name: Optional[str] = None
    stop_id: Optional[str] = None
    sequence: int = 0


class ScheduleEntry(BaseModel):
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    stop_id: str
    stop_name: str
    sequence: int
    delay_minutes: Optional[int] = 0
    status: str = "scheduled"  # scheduled, delayed, cancelled, arrived


class RouteData(BaseModel):
    route_id: str
    route_name: str
    transport_mode: TransportMode
    operator: str
    route_points: List[RoutePoint]
    schedule: List[ScheduleEntry]
    fare: Optional[float] = None
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_source: DataSource
    reliability_score: float = Field(default=0.8, ge=0.0, le=1.0)


class WeatherData(BaseModel):
    location: Location
    temperature_celsius: Optional[float] = None
    humidity_percent: Optional[int] = None
    rainfall_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_condition: Optional[str] = None  # sunny, rainy, cloudy, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TrafficData(BaseModel):
    location: Location
    traffic_level: str  # light, moderate, heavy, severe
    speed_kmh: Optional[float] = None
    incidents: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataQualityMetrics(BaseModel):
    source: DataSource
    freshness_minutes: int  # How old is the data
    completeness_score: float = Field(ge=0.0, le=1.0)  # How complete is the data
    accuracy_score: float = Field(ge=0.0, le=1.0)  # How accurate (based on validation)
    reliability_score: float = Field(ge=0.0, le=1.0)  # Historical reliability
    last_validated: datetime = Field(default_factory=datetime.utcnow)


class AggregatedTransportData(BaseModel):
    """Aggregated data from multiple sources for a specific transport query"""
    query_id: str
    origin: Location
    destination: Optional[Location] = None
    transport_modes: List[TransportMode]
    routes: List[RouteData]
    weather: Optional[WeatherData] = None
    traffic: List[TrafficData] = []
    quality_metrics: List[DataQualityMetrics] = []
    aggregation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_sources: int = 0
    successful_sources: int = 0