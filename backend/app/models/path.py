from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

# An enum for the user to express a preference
class TransitMode(str, Enum):
    BUS = "bus"
    TRAIN = "train"

# Define the allowed travel modes using an Enum
class TravelMode(str, Enum):
    DRIVING = "driving"
    TRANSIT = "transit"
    WALKING = "walking"
    BICYCLING = "bicycling"
    THREE_WHEELER = "three_wheeler" 

class PathRequest(BaseModel):
    start: str
    end: str
    mode: TravelMode = TravelMode.DRIVING
    departure_time: datetime = Field(
        default_factory=datetime.now,
        description="Departure time in ISO 8601 format. Defaults to the current time if not provided.",
        example="2025-08-25T16:30:00"
    )

    transit_mode_preference: Optional[TransitMode] = None

class TransitDetails(BaseModel):
    """Model for transit-specific information."""
    arrival_stop: str
    departure_stop: str
    line_name: str
    vehicle_type: str # e.g., Bus, Train
    num_stops: int

class RouteStep(BaseModel):
    """Represents a single step in the directions. Now more flexible."""
    instruction: str = Field(..., alias="html_instructions")
    distance: str
    duration: str
    travel_mode: str 
    transit_details: Optional[TransitDetails] = None

class RouteResponse(BaseModel):
    """Defines the structure for the successful API response."""
    origin: str
    destination: str
    distance_text: str
    duration_text: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    steps: List[RouteStep]