from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from enum import Enum

class TransportMode(str, Enum):
    BUS = "bus"
    TRAIN = "train"
    TUK_TUK = "tuk_tuk"
    WALKING = "walking"
    TAXI = "taxi"

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    DISRUPTED = "disrupted"

class Stop(BaseModel):
    name: str
    lat: float
    lng: float
    arrival_time: Optional[time] = None
    departure_time: Optional[time] = None
    platform: Optional[str] = None

class Schedule(BaseModel):
    departure_time: time
    arrival_time: time
    days_of_week: List[str] = Field(default=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])
    frequency_minutes: Optional[int] = None

class FareStructure(BaseModel):
    base_fare: float
    per_km_rate: Optional[float] = None
    distance_brackets: Optional[Dict[str, float]] = None  # {"0-10": 50, "10-25": 75}
    concessions: Optional[Dict[str, float]] = None  # {"student": 0.5, "senior": 0.6}

class BusRoute(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    route_number: str
    route_name: str
    operator: str  # "SLTB", "CTB", "Private"
    origin: str
    destination: str
    stops: List[Stop]
    schedules: List[Schedule]
    fare_structure: FareStructure
    route_type: str  # "intercity", "local", "express"
    distance_km: float
    status: ServiceStatus = ServiceStatus.ACTIVE
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

class TrainRoute(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    route_number: str
    route_name: str
    line: str  # "Main Line", "Coastal Line", "Northern Line"
    origin: str
    destination: str
    stations: List[Stop]
    schedules: List[Schedule]
    fare_structure: FareStructure
    train_type: str  # "express", "intercity", "slow", "freight"
    distance_km: float
    status: ServiceStatus = ServiceStatus.ACTIVE
    amenities: List[str] = []  # ["AC", "WiFi", "Food"]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

class Location(BaseModel):
    address: str
    lat: float
    lng: float

class TukTukService(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    service_name: str
    coverage_area: str
    base_fare: float
    per_km_rate: float
    waiting_time_rate: float  # per minute
    night_surcharge: Optional[float] = None
    contact_number: Optional[str] = None
    app_booking: bool = False
    estimated_arrival_time: int = 5  # minutes
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

class Disruption(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    transport_mode: TransportMode
    route_id: str
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    start_time: datetime
    end_time: Optional[datetime] = None
    affected_stops: List[str] = []
    alternative_routes: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: str  # "official", "community", "automatic"

    class Config:
        arbitrary_types_allowed = True

class UserProfile(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    preferred_language: str = "en"
    accessibility_needs: List[str] = []  # ["wheelchair", "audio_guidance", "visual_aids"]
    preferred_transport_modes: List[TransportMode] = []
    home_location: Optional[Location] = None
    work_location: Optional[Location] = None
    budget_preferences: Optional[Dict[str, Any]] = None
    notification_preferences: Dict[str, bool] = Field(default={"disruptions": True, "delays": True, "offers": False})
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

class CommunityUpdate(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    route_id: str
    transport_mode: TransportMode
    update_type: str  # "schedule_change", "crowding", "delay", "fare_change", "new_route"
    message: str
    user_id: str
    location: Optional[Location] = None
    verified: bool = False
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

# Keep existing models for backward compatibility
class MockBusRoute(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    route_number: str
    origin: str
    destination: str
    stops: List[str]
    operator: str = "SLTB" 

    class Config:
        arbitrary_types_allowed = True

class JourneyRequest(BaseModel):
    origin: str
    destination: str
    mode: str = "transit"

class JourneyLeg(BaseModel):
    distance: str
    duration: str
    summary: str
    start_location: Location
    end_location: Location
    travel_mode: str

class RouteOption(BaseModel):
    total_duration: str
    total_distance: str
    legs: List[JourneyLeg]
    summary: Optional[str] = None
    polyline: Optional[str] = None
    total_cost: Optional[float] = None