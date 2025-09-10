from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo

class PreferenceType(str, Enum):
    COST = "cost"
    TIME = "time"
    COMFORT = "comfort"
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"
    RELIABILITY = "reliability"

class UserPreference(BaseModel):
    """Model for user preferences"""
    user_id: str
    preference_type: PreferenceType
    weight: float = Field(ge=0.0, le=1.0, description="Weight of this preference (0.0 to 1.0)")
    value: Any = Field(description="The actual preference value")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "preference_type": "cost",
                "weight": 0.8,
                "value": {"max_fare": 500, "prefer_cheaper": True},
                "last_updated": "2025-01-27T10:00:00+05:30"
            }
        }

class UserProfile(BaseModel):
    """Model for complete user profile"""
    user_id: str
    preferences: List[UserPreference]
    travel_history: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Colombo")))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "preferences": [
                    {
                        "preference_type": "cost",
                        "weight": 0.8,
                        "value": {"max_fare": 500, "prefer_cheaper": True}
                    },
                    {
                        "preference_type": "time",
                        "weight": 0.6,
                        "value": {"max_duration": 120, "prefer_faster": True}
                    }
                ],
                "travel_history": [],
                "created_at": "2025-01-27T10:00:00+05:30",
                "updated_at": "2025-01-27T10:00:00+05:30"
            }
        }
