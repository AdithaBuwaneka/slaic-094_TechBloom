from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo  # Add this import

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

# Function to get current Sri Lanka time
def get_current_sl_time():
    return datetime.now(ZoneInfo("Asia/Colombo"))

class PathRequest(BaseModel):
    start: str
    end: str
    mode: TravelMode = TravelMode.DRIVING
    departure_time: datetime = Field(
        default_factory=get_current_sl_time,
        description="Departure time in ISO 8601 format. Defaults to the current time in Sri Lanka timezone if not provided."
    )
    transit_mode_preference: Optional[TransitMode] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start": "Colombo",
                    "end": "Kandy",
                    "mode": "driving",
                    "departure_time": get_current_sl_time().isoformat(),
                    "transit_mode_preference": "bus"
                }
            ]
        }
    }

class TransitDetails(BaseModel):
    """Model for transit-specific information."""
    arrival_stop: str
    departure_stop: str
    line_name: str
    vehicle_type: str # e.g., Bus, Train
    num_stops: int
    departure_time: Optional[str] = None

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