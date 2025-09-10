from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo

class TransitMode(str, Enum):
    BUS = "bus"
    TRAIN = "train"
    UBER = "uber"
    THREE_WHEELER = "three_wheeler"
    WALKING = "walking"

class FareType(str, Enum):
    FIXED = "fixed"
    DISTANCE_BASED = "distance_based"
    TIME_BASED = "time_based"
    ZONE_BASED = "zone_based"

class TransitFare(BaseModel):
    """Model for transit fare information"""
    route_id: str
    origin: str
    destination: str
    mode: TransitMode
    fare_type: FareType
    base_fare: float
    distance_fare: Optional[float] = None
    time_fare: Optional[float] = None
    currency: str = "LKR"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    
    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "route_001",
                "origin": "Colombo",
                "destination": "Kandy",
                "mode": "train",
                "fare_type": "fixed",
                "base_fare": 150.0,
                "currency": "LKR",
                "is_active": True
            }
        }

class TransitRoute(BaseModel):
    """Model for transit route information"""
    route_id: str
    route_number: Optional[str] = None
    origin: str
    destination: str
    mode: TransitMode
    operator: str
    stops: List[str]
    frequency: str  # e.g., "every 15 minutes", "hourly"
    operating_hours: Dict[str, str]  # e.g., {"start": "06:00", "end": "22:00"}
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    
    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "route_001",
                "route_number": "138",
                "origin": "Pettah",
                "destination": "Maharagama",
                "mode": "bus",
                "operator": "SLTB",
                "stops": ["Fort", "Maradana", "Borella", "Narahenpita", "Nugegoda"],
                "frequency": "every 10 minutes",
                "operating_hours": {"start": "05:00", "end": "23:00"},
                "is_active": True
            }
        }

class DisruptionType(str, Enum):
    DELAY = "delay"
    CANCELLATION = "cancellation"
    REROUTE = "reroute"
    MAINTENANCE = "maintenance"
    ACCIDENT = "accident"
    WEATHER = "weather"
    STRIKE = "strike"

class DisruptionSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TransitDisruption(BaseModel):
    """Model for transit disruption information"""
    disruption_id: str
    route_id: str
    disruption_type: DisruptionType
    severity: DisruptionSeverity
    description: str
    affected_stops: List[str]
    estimated_duration: Optional[int] = None  # in minutes
    alternative_routes: List[str] = []
    reported_by: str
    reported_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    location: Optional[Dict[str, float]] = None  # {"lat": 6.9271, "lng": 79.8612}
    
    class Config:
        json_schema_extra = {
            "example": {
                "disruption_id": "disp_001",
                "route_id": "route_001",
                "disruption_type": "delay",
                "severity": "medium",
                "description": "Traffic congestion due to road construction",
                "affected_stops": ["Maradana", "Borella"],
                "estimated_duration": 30,
                "alternative_routes": ["route_002", "route_003"],
                "reported_by": "user123",
                "is_resolved": False
            }
        }

class LastMileOption(BaseModel):
    """Model for last mile connectivity options"""
    option_id: str
    name: str
    mode: TransitMode
    origin: str
    destination: str
    estimated_duration: int  # in minutes
    estimated_cost: float
    currency: str = "LKR"
    availability: str = "24/7"  # e.g., "24/7", "06:00-22:00"
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "option_id": "last_mile_001",
                "name": "Uber from Maharagama Station",
                "mode": "uber",
                "origin": "Maharagama Station",
                "destination": "Maharagama City Center",
                "estimated_duration": 8,
                "estimated_cost": 250.0,
                "currency": "LKR",
                "availability": "24/7",
                "is_active": True
            }
        }
