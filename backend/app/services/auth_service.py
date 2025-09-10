# Authentication Service for Transit Companion Backend
# JWT-based authentication with user and admin roles

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
import uuid

class AuthenticationService:
    """
    Complete authentication service with JWT tokens
    Supports both regular users and admin users
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours
        self.refresh_token_expire_days = 7  # 7 days
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def create_user_tokens(self, user_id: str, email: str, role: str = "user") -> Dict[str, str]:
        """Create both access and refresh tokens for a user"""
        token_data = {
            "sub": user_id,
            "email": email,
            "role": role,
            "iat": datetime.utcnow()
        }
        
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60  # seconds
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Create new access token using refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        
        new_token_data = {
            "sub": payload["sub"],
            "email": payload["email"], 
            "role": payload["role"],
            "iat": datetime.utcnow()
        }
        
        new_access_token = self.create_access_token(new_token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def validate_user_registration(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Validate user registration data"""
        errors = []
        
        # Email validation
        if not email or "@" not in email:
            errors.append("Valid email is required")
        
        # Password validation
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        # Name validation
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if errors:
            return {"valid": False, "errors": errors}
        
        return {"valid": True, "errors": []}
    
    def create_user_profile(self, name: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Create complete user profile"""
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        
        user_profile = {
            "user_id": user_id,
            "name": name,
            "email": email.lower(),
            "password_hash": hashed_password,
            "role": role,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "email_verified": False,
            "profile": {
                "avatar_url": None,
                "phone": None,
                "date_of_birth": None,
                "preferred_language": "en",
                "notification_preferences": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "sms_notifications": False
                }
            },
            "travel_preferences": {
                "preferred_transit_modes": ["bus", "train"],
                "max_walking_distance": 1.0,  # km
                "budget_preference": "medium",  # low, medium, high
                "time_vs_cost_weight": 0.5,  # 0=cost priority, 1=time priority
                "comfort_preference": 0.7,  # 0=basic, 1=premium
                "accessibility_needs": [],
                "avoid_preferences": [],  # tolls, highways, etc.
                "default_departure_buffer": 10  # minutes before departure
            },
            "usage_stats": {
                "total_trips_planned": 0,
                "favorite_destinations": [],
                "most_used_mode": None,
                "total_distance_traveled": 0.0,
                "total_fare_saved": 0.0
            }
        }
        
        return user_profile

# Initialize global authentication service
auth_service = AuthenticationService()