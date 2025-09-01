from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class DeviceType(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"

class User(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    email: EmailStr
    phone: Optional[str] = None
    password_hash: str = Field(..., exclude=True)  # Never expose in API
    full_name: str
    profile_picture: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    
    # Preferences
    preferred_language: str = "en"
    preferred_transport_modes: List[str] = ["bus", "train"]
    accessibility_needs: List[str] = []
    
    # App-specific
    fcm_token: Optional[str] = None  # Firebase Cloud Messaging
    last_location: Optional[dict] = None  # {lat, lng, timestamp}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    email_verified: bool = False
    phone_verified: bool = False

    class Config:
        arbitrary_types_allowed = True

class UserRegistration(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    preferred_language: str = "en"
    device_type: DeviceType
    fcm_token: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_type: DeviceType
    fcm_token: Optional[str] = None

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str

class DeviceInfo(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    device_type: DeviceType
    fcm_token: str
    device_id: str  # Unique device identifier
    app_version: str
    os_version: str
    last_active: datetime = Field(default_factory=datetime.utcnow)
    location_enabled: bool = False
    notifications_enabled: bool = True
    
    class Config:
        arbitrary_types_allowed = True

class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PushNotification(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    title: str
    body: str
    data: Optional[dict] = None
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    notification_type: str = "general"  # general, disruption, route_update, etc.
    
    class Config:
        arbitrary_types_allowed = True