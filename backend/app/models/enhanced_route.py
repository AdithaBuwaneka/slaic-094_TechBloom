from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from .transit_data import TransitMode, TransitFare, LastMileOption, TransitDisruption

class RouteSegment(BaseModel):
    """Enhanced route segment with multi-modal information"""
    segment_id: str
    origin: str
    destination: str
    mode: TransitMode
    duration: int  # in minutes
    distance: float  # in km
    cost: float
    currency: str = "LKR"
    route_details: Optional[Dict[str, Any]] = None
    fare_info: Optional[TransitFare] = None
    last_mile_options: List[LastMileOption] = []
    disruptions: List[TransitDisruption] = []
    alternatives: List['RouteSegment'] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "seg_001",
                "origin": "Colombo Fort",
                "destination": "Maharagama",
                "mode": "bus",
                "duration": 45,
                "distance": 12.5,
                "cost": 25.0,
                "currency": "LKR",
                "route_details": {
                    "route_number": "138",
                    "operator": "SLTB",
                    "stops": ["Fort", "Maradana", "Borella", "Narahenpita", "Nugegoda"]
                }
            }
        }

class LocalKnowledge(BaseModel):
    """Local knowledge and insights about the route"""
    knowledge_id: str
    route_segment_id: str
    category: str  # e.g., "safety", "culture", "food", "attractions"
    title: str
    description: str
    source: str  # e.g., "web_search", "community", "official"
    relevance_score: float = Field(ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    
    class Config:
        json_schema_extra = {
            "example": {
                "knowledge_id": "lk_001",
                "route_segment_id": "seg_001",
                "category": "safety",
                "title": "Safe area during day, avoid late night",
                "description": "This area is generally safe during daylight hours but exercise caution after dark.",
                "source": "community_reports",
                "relevance_score": 0.8
            }
        }

class UserPreferenceMatch(BaseModel):
    """How well a route matches user preferences"""
    preference_type: str
    match_score: float = Field(ge=0.0, le=1.0)
    explanation: str
    weight: float = Field(ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "preference_type": "cost",
                "match_score": 0.9,
                "explanation": "This route is very cost-effective at Rs. 25",
                "weight": 0.8
            }
        }

class EnhancedRouteResponse(BaseModel):
    """Enhanced route response with multi-agent analysis"""
    route_id: str
    origin: str
    destination: str
    total_duration: int  # in minutes
    total_distance: float  # in km
    total_cost: float
    currency: str = "LKR"
    segments: List[RouteSegment]
    local_knowledge: List[LocalKnowledge] = []
    preference_matches: List[UserPreferenceMatch] = []
    overall_score: float = Field(ge=0.0, le=1.0)
    alternative_routes: List['EnhancedRouteResponse'] = []
    disruptions: List[TransitDisruption] = []
    recommendations: List[str] = []
    last_updated: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    
    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "route_001",
                "origin": "Colombo Fort",
                "destination": "Maharagama",
                "total_duration": 45,
                "total_distance": 12.5,
                "total_cost": 25.0,
                "currency": "LKR",
                "overall_score": 0.85,
                "recommendations": [
                    "Take bus 138 for the most cost-effective route",
                    "Consider leaving early to avoid rush hour",
                    "This route is safe and well-lit"
                ]
            }
        }

class MultiAgentRequest(BaseModel):
    """Request model for multi-agent route planning"""
    origin: str
    destination: str
    mode: TransitMode
    transit_preference: Optional[str] = None  # "bus" or "train"
    user_id: Optional[str] = None
    departure_time: Optional[datetime] = None
    include_local_knowledge: bool = True
    include_preferences: bool = True
    include_disruptions: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": "Colombo Fort",
                "destination": "Maharagama",
                "mode": "transit",
                "transit_preference": "bus",
                "user_id": "user123",
                "include_local_knowledge": True,
                "include_preferences": True,
                "include_disruptions": True
            }
        }
