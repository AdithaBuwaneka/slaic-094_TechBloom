from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.transport_data import Location, TransportMode


class Language(str, Enum):
    SINHALA = "sinhala"
    TAMIL = "tamil" 
    ENGLISH = "english"


class AccessibilityNeed(str, Enum):
    WHEELCHAIR = "wheelchair"
    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    MOBILITY_ASSISTANCE = "mobility_assistance"
    COGNITIVE_ASSISTANCE = "cognitive_assistance"
    ELDERLY_ASSISTANCE = "elderly_assistance"


class DisabilityType(str, Enum):
    MOBILITY = "mobility"
    VISUAL = "visual"
    HEARING = "hearing"
    COGNITIVE = "cognitive"
    MULTIPLE = "multiple"
    TEMPORARY = "temporary"


class AssistanceType(str, Enum):
    BOARDING = "boarding"
    NAVIGATION = "navigation"
    COMMUNICATION = "communication"
    EMERGENCY = "emergency"
    INFORMATION = "information"
    COMPANION = "companion"


class AccessibilityProfile(BaseModel):
    user_id: str
    primary_language: Language = Language.ENGLISH
    secondary_languages: List[Language] = []
    
    # Accessibility needs
    accessibility_needs: List[AccessibilityNeed] = []
    disability_types: List[DisabilityType] = []
    
    # Mobility aids
    uses_wheelchair: bool = False
    uses_walking_aid: bool = False
    uses_guide_dog: bool = False
    mobility_device_details: Optional[str] = None
    
    # Communication preferences
    prefers_audio_announcements: bool = False
    needs_visual_alerts: bool = False
    uses_screen_reader: bool = False
    preferred_text_size: str = "normal"  # "small", "normal", "large", "extra_large"
    high_contrast_mode: bool = False
    
    # Assistance requirements
    requires_boarding_assistance: bool = False
    requires_navigation_assistance: bool = False
    requires_companion: bool = False
    emergency_contact: Optional[Dict[str, str]] = None
    
    # Cognitive support
    needs_simplified_instructions: bool = False
    prefers_step_by_step_guidance: bool = False
    needs_reminder_notifications: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class TransportAccessibility(BaseModel):
    transport_mode: TransportMode
    operator: str
    route_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    
    # Physical accessibility
    wheelchair_accessible: bool = False
    low_floor_entry: bool = False
    audio_announcements: bool = False
    visual_displays: bool = False
    braille_signage: bool = False
    
    # Support services
    staff_assistance_available: bool = False
    priority_seating: bool = False
    designated_wheelchair_spaces: int = 0
    accessible_toilets: bool = False
    
    # Communication support
    sign_language_support: bool = False
    multilingual_announcements: List[Language] = []
    mobile_app_accessible: bool = False
    
    # Infrastructure
    platform_level_boarding: bool = False
    tactile_guidance_strips: bool = False
    elevator_access: bool = False
    ramp_access: bool = False
    
    accessibility_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityAlert(BaseModel):
    alert_id: str
    transport_mode: TransportMode
    operator: str
    route_id: Optional[str] = None
    
    # Alert details
    alert_type: str  # "service_disruption", "equipment_failure", "temporary_closure"
    accessibility_impact: List[AccessibilityNeed]
    severity: str = "medium"  # "low", "medium", "high", "critical"
    
    # Description
    title: Dict[Language, str]  # Multi-language support
    description: Dict[Language, str]
    alternative_options: Dict[Language, List[str]] = {}
    
    # Timeline
    start_time: datetime
    estimated_end_time: Optional[datetime] = None
    
    # Location impact
    affected_locations: List[Location] = []
    affected_routes: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class LanguageTranslation(BaseModel):
    translation_id: str
    original_language: Language
    target_language: Language
    original_text: str
    translated_text: str
    context: str  # "navigation", "announcement", "emergency", "general"
    confidence_score: float = Field(ge=0.0, le=1.0)
    translation_timestamp: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityRecommendation(BaseModel):
    recommendation_id: str
    user_id: str
    route_id: str
    
    # Accessibility scoring
    accessibility_score: float = Field(ge=0.0, le=10.0)
    accessibility_breakdown: Dict[str, float] = {}
    
    # Specific recommendations
    boarding_recommendations: List[str] = []
    navigation_recommendations: List[str] = []
    assistance_recommendations: List[str] = []
    
    # Required preparations
    advance_booking_required: bool = False
    assistance_notification_time: Optional[int] = None  # minutes
    special_equipment_needed: List[str] = []
    
    # Alternative options
    more_accessible_alternatives: List[Dict[str, Any]] = []
    fallback_options: List[Dict[str, Any]] = []
    
    # Support information
    support_contacts: Dict[str, str] = {}
    accessibility_features: List[str] = []
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class EmergencyAccessibilityInfo(BaseModel):
    info_id: str
    transport_mode: TransportMode
    operator: str
    
    # Emergency procedures
    emergency_procedures: Dict[Language, List[str]]
    evacuation_assistance: Dict[AccessibilityNeed, List[str]]
    
    # Emergency contacts
    emergency_contacts: List[Dict[str, str]]
    disability_support_hotline: Optional[str] = None
    
    # Communication methods
    emergency_communication_methods: List[str]  # ["audio", "visual", "vibration", "text"]
    sign_language_emergency_service: bool = False
    
    # Equipment and facilities
    emergency_equipment_locations: Dict[str, List[str]]
    accessible_emergency_exits: List[str] = []
    emergency_shelter_accessibility: Dict[str, bool] = {}
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityFeedback(BaseModel):
    feedback_id: str
    user_id: str
    transport_mode: TransportMode
    operator: str
    route_id: Optional[str] = None
    
    # Feedback details
    accessibility_rating: int = Field(ge=1, le=5)
    specific_ratings: Dict[str, int] = {}  # {"boarding": 4, "navigation": 3, etc.}
    
    # Experience details
    accessibility_features_used: List[AccessibilityNeed] = []
    issues_encountered: List[str] = []
    positive_experiences: List[str] = []
    
    # Improvement suggestions
    suggested_improvements: List[str] = []
    missing_features: List[str] = []
    
    # Context
    trip_date: datetime
    time_of_day: str
    weather_conditions: Optional[str] = None
    crowd_level: str = "normal"  # "light", "normal", "heavy"
    
    feedback_text: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityCompliance(BaseModel):
    compliance_id: str
    transport_mode: TransportMode
    operator: str
    
    # Legal compliance
    ada_compliant: bool = False
    local_disability_law_compliant: bool = False
    international_standards_met: List[str] = []
    
    # Compliance details
    compliance_level: str = "partial"  # "none", "partial", "full", "exceeds"
    non_compliance_areas: List[str] = []
    improvement_timeline: Optional[str] = None
    
    # Certification
    accessibility_certifications: List[str] = []
    last_inspection_date: Optional[datetime] = None
    next_inspection_due: Optional[datetime] = None
    
    # Documentation
    compliance_documentation: List[str] = []
    accessibility_statement_url: Optional[str] = None
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)