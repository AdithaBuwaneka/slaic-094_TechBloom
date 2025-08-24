from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib

from .transport_data import Location, TransportMode


class UserRole(str, Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class NotificationPreference(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class LanguagePreference(str, Enum):
    ENGLISH = "en"
    SINHALA = "si"
    TAMIL = "ta"


class AccessibilityFeature(str, Enum):
    SCREEN_READER = "screen_reader"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    VOICE_NAVIGATION = "voice_navigation"
    WHEELCHAIR_ACCESS = "wheelchair_access"


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: f"user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    
    # Authentication
    password_hash: Optional[str] = None
    salt: Optional[str] = None
    is_email_verified: bool = False
    email_verification_token: Optional[str] = None
    
    # Profile information
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    
    # Account details
    role: UserRole = UserRole.REGULAR
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    
    # Location preferences
    home_location: Optional[Location] = None
    work_location: Optional[Location] = None
    frequent_locations: List[Location] = []
    
    # Transport preferences
    preferred_transport_modes: List[TransportMode] = []
    mobility_preferences: Dict[str, Any] = {}
    
    # Accessibility settings
    accessibility_features: List[AccessibilityFeature] = []
    accessibility_notes: Optional[str] = None
    
    # Communication preferences
    language_preference: LanguagePreference = LanguagePreference.ENGLISH
    notification_preferences: List[NotificationPreference] = [NotificationPreference.IN_APP]
    marketing_consent: bool = False
    data_sharing_consent: bool = False

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, underscores, and hyphens')
        return v


class UserPreferences(BaseModel):
    user_id: str
    
    # Journey preferences
    walking_distance_preference: float = Field(default=1.0, ge=0.1, le=5.0)  # km
    max_transfers: int = Field(default=2, ge=0, le=5)
    arrival_buffer_minutes: int = Field(default=5, ge=0, le=30)
    
    # Route preferences
    prefer_fastest_route: bool = True
    prefer_cheapest_route: bool = False
    avoid_crowded_transport: bool = False
    prefer_accessible_routes: bool = False
    
    # Notification settings
    disruption_alerts: bool = True
    schedule_change_alerts: bool = True
    fare_change_alerts: bool = False
    arrival_reminders: bool = True
    departure_reminders: bool = True
    reminder_minutes_before: int = Field(default=10, ge=1, le=60)
    
    # Privacy settings
    location_tracking: bool = True
    usage_analytics: bool = True
    personalized_recommendations: bool = True
    
    # Display preferences
    map_view_preference: str = "hybrid"  # satellite, roadmap, hybrid, terrain
    distance_unit: str = "km"  # km, miles
    time_format: str = "24h"  # 12h, 24h
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"sess_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    
    # Session details
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Device information
    device_id: Optional[str] = None
    device_type: Optional[str] = None  # mobile, tablet, desktop
    os: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Location and context
    last_known_location: Optional[Location] = None
    timezone: Optional[str] = None
    
    # Session metadata
    login_method: str = "password"  # password, oauth, biometric
    two_factor_verified: bool = False


class UserActivity(BaseModel):
    activity_id: str = Field(default_factory=lambda: f"act_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    session_id: Optional[str] = None
    
    # Activity details
    activity_type: str  # login, logout, route_search, journey_start, etc.
    activity_data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Context
    location: Optional[Location] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None


class AuthToken(BaseModel):
    token_id: str = Field(default_factory=lambda: f"tok_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    token_type: str  # access, refresh, verification, reset
    
    # Token details
    token_hash: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    is_revoked: bool = False
    
    # Metadata
    issued_for: Optional[str] = None  # device_id, ip_address, etc.
    scope: List[str] = ["basic"]  # permissions granted


class PasswordResetRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"pwd_reset_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    email: EmailStr
    
    # Request details
    reset_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    is_used: bool = False
    
    # Security
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class UserVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"verify_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    verification_type: str  # email, phone, identity
    
    # Verification details
    verification_token: str
    verification_data: Dict[str, Any] = {}
    status: str = "pending"  # pending, completed, failed, expired
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    verified_at: Optional[datetime] = None
    
    # Attempts
    attempt_count: int = 0
    max_attempts: int = 3


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Preferences
    language_preference: LanguagePreference = LanguagePreference.ENGLISH
    notification_preferences: List[NotificationPreference] = [NotificationPreference.IN_APP]
    marketing_consent: bool = False
    data_sharing_consent: bool = False
    
    # Location (optional)
    home_location: Optional[Location] = None


class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str
    device_id: Optional[str] = None
    remember_me: bool = False


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Location updates
    home_location: Optional[Location] = None
    work_location: Optional[Location] = None
    
    # Preference updates
    language_preference: Optional[LanguagePreference] = None
    accessibility_features: Optional[List[AccessibilityFeature]] = None


class UserStats(BaseModel):
    user_id: str
    
    # Usage statistics
    total_journeys: int = 0
    total_distance_km: float = 0.0
    total_time_saved_minutes: int = 0
    
    # Transport mode usage
    transport_mode_stats: Dict[str, int] = {}  # mode -> count
    favorite_routes: List[str] = []
    
    # Interaction statistics
    searches_performed: int = 0
    alerts_received: int = 0
    notifications_sent: int = 0
    
    # Timestamps
    stats_period_start: datetime
    stats_period_end: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class UserFeedback(BaseModel):
    feedback_id: str = Field(default_factory=lambda: f"feedback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    
    # Feedback details
    feedback_type: str  # bug_report, feature_request, general, rating
    subject: str = Field(max_length=200)
    message: str = Field(max_length=2000)
    rating: Optional[int] = Field(ge=1, le=5)
    
    # Context
    feature_area: Optional[str] = None  # route_planning, disruptions, etc.
    journey_id: Optional[str] = None
    screenshot_url: Optional[str] = None
    
    # Status
    status: str = "pending"  # pending, acknowledged, resolved, closed
    admin_response: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class UserNotification(BaseModel):
    notification_id: str = Field(default_factory=lambda: f"notif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    user_id: str
    
    # Notification details
    title: str = Field(max_length=100)
    message: str = Field(max_length=500)
    notification_type: str  # info, warning, alert, success, marketing
    category: str = "general"  # disruption, schedule, fare, system, marketing
    
    # Delivery
    delivery_methods: List[NotificationPreference] = [NotificationPreference.IN_APP]
    priority: int = Field(default=5, ge=1, le=10)  # 1 = highest
    
    # Status
    is_read: bool = False
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Scheduling
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Metadata
    data: Dict[str, Any] = {}
    deep_link: Optional[str] = None
    action_buttons: List[Dict[str, str]] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserDevice(BaseModel):
    device_id: str
    user_id: str
    
    # Device information
    device_name: Optional[str] = None
    device_type: str  # mobile, tablet, desktop
    os: str
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    
    # Push notification token
    push_token: Optional[str] = None
    push_platform: Optional[str] = None  # fcm, apns
    
    # Device settings
    location_enabled: bool = True
    notifications_enabled: bool = True
    biometric_enabled: bool = False
    
    # Status
    is_active: bool = True
    last_used_at: datetime = Field(default_factory=datetime.utcnow)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Security
    device_fingerprint: Optional[str] = None
    is_trusted: bool = False
    security_flags: List[str] = []