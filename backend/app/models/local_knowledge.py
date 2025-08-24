from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from .transport_data import Location, TransportMode


class KnowledgeType(str, Enum):
    CULTURAL_INFO = "cultural_info"
    LOCAL_TIPS = "local_tips"
    TOURIST_GUIDANCE = "tourist_guidance"
    SAFETY_INFO = "safety_info"
    POPULAR_DESTINATIONS = "popular_destinations"
    LOCAL_EVENTS = "local_events"
    FOOD_RECOMMENDATIONS = "food_recommendations"
    SHOPPING_AREAS = "shopping_areas"
    ACCOMMODATION = "accommodation"
    EMERGENCY_CONTACTS = "emergency_contacts"


class ContentCategory(str, Enum):
    TRANSPORTATION = "transportation"
    CULTURE = "culture"
    SAFETY = "safety"
    TOURISM = "tourism"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    FOOD = "food"
    SHOPPING = "shopping"
    ACCOMMODATION = "accommodation"
    EMERGENCY = "emergency"


class Language(str, Enum):
    ENGLISH = "en"
    SINHALA = "si"
    TAMIL = "ta"


class UserType(str, Enum):
    TOURIST = "tourist"
    LOCAL_COMMUTER = "local_commuter"
    BUSINESS_TRAVELER = "business_traveler"
    STUDENT = "student"
    SENIOR = "senior"
    FAMILY = "family"


class LocalKnowledgeEntry(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    knowledge_type: KnowledgeType
    category: ContentCategory
    location: Location
    relevant_radius_km: float = Field(default=5.0, gt=0)
    languages: List[Language] = [Language.ENGLISH]
    target_user_types: List[UserType] = []
    transport_modes_relevant: List[TransportMode] = []
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reliability_score: float = Field(default=0.8, ge=0.0, le=1.0)
    source: str = "community"
    last_verified: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CulturalGuidance(BaseModel):
    location: Location
    cultural_norms: List[str] = []
    dress_code: Optional[str] = None
    religious_considerations: List[str] = []
    local_customs: List[str] = []
    language_tips: Dict[str, str] = {}
    greeting_etiquette: Optional[str] = None
    business_etiquette: Optional[str] = None
    tipping_guidelines: Optional[str] = None


class TouristAttraction(BaseModel):
    name: str
    location: Location
    description: str
    category: str  # temple, museum, park, etc.
    entry_fee: Optional[float] = None
    opening_hours: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    transport_access: List[Dict[str, Any]] = []
    cultural_significance: Optional[str] = None
    visitor_tips: List[str] = []
    languages_supported: List[Language] = [Language.ENGLISH]


class LocalEvent(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    location: Location
    start_date: datetime
    end_date: Optional[datetime] = None
    event_type: str  # festival, ceremony, market, etc.
    transport_impact: Optional[str] = None
    cultural_significance: Optional[str] = None
    visitor_guidelines: List[str] = []
    contact_info: Optional[str] = None


class SafetyInformation(BaseModel):
    location: Location
    safety_level: str  # safe, moderate, caution, avoid
    safety_tips: List[str] = []
    emergency_contacts: List[Dict[str, str]] = []
    common_risks: List[str] = []
    recommended_precautions: List[str] = []
    tourist_police_contact: Optional[str] = None
    hospital_nearby: Optional[Dict[str, Any]] = None


class LocalRecommendation(BaseModel):
    id: Optional[str] = None
    location: Location
    recommendation_type: KnowledgeType
    title: str
    description: str
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    price_range: Optional[str] = None  # budget, moderate, expensive
    operating_hours: Optional[str] = None
    contact_info: Optional[str] = None
    special_notes: List[str] = []
    user_reviews: List[str] = []


class LocalKnowledgeQuery(BaseModel):
    location: Optional[Location] = None
    radius_km: Optional[float] = Field(default=10.0, gt=0)
    knowledge_types: Optional[List[KnowledgeType]] = None
    categories: Optional[List[ContentCategory]] = None
    user_type: Optional[UserType] = None
    language: Language = Language.ENGLISH
    include_cultural_info: bool = True
    include_safety_info: bool = True
    include_tourist_attractions: bool = True
    include_local_events: bool = True


class LocalKnowledgeResponse(BaseModel):
    knowledge_entries: List[LocalKnowledgeEntry] = []
    cultural_guidance: Optional[CulturalGuidance] = None
    tourist_attractions: List[TouristAttraction] = []
    local_events: List[LocalEvent] = []
    safety_information: Optional[SafetyInformation] = None
    recommendations: List[LocalRecommendation] = []
    total_count: int = 0
    query_location: Optional[Location] = None
    language: Language = Language.ENGLISH


class CreateKnowledgeRequest(BaseModel):
    title: str
    description: str
    knowledge_type: KnowledgeType
    category: ContentCategory
    location: Location
    relevant_radius_km: float = Field(default=5.0, gt=0)
    languages: List[Language] = [Language.ENGLISH]
    target_user_types: List[UserType] = []
    source: str = "community"


class UpdateKnowledgeRequest(BaseModel):
    entry_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    last_verified: Optional[datetime] = None


class CulturalInsightRequest(BaseModel):
    location: Location
    user_type: UserType = UserType.TOURIST
    language: Language = Language.ENGLISH
    specific_interests: List[str] = []  # temples, food, shopping, etc.


class TouristGuidanceRequest(BaseModel):
    origin: Location
    destination: Location
    user_type: UserType = UserType.TOURIST
    language: Language = Language.ENGLISH
    interests: List[str] = []
    budget_range: Optional[str] = None
    duration_days: Optional[int] = None