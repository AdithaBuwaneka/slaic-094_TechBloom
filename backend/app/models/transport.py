# app/models/transport.py

from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

# Helper for MongoDB's _id field
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# --- Add this new model ---
class MockBusRoute(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    route_number: str
    origin: str
    destination: str
    stops: List[str]
    operator: str = "SLTB" # Sri Lanka Transport Board

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# --- No changes needed for the models below, they are for reference ---
class JourneyRequest(BaseModel):
    origin: str
    destination: str
    mode: str = "transit"

class Location(BaseModel):
    address: str
    lat: float
    lng: float

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