from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime
import re

from app.models.user import User, UserRegistration, UserLogin, TokenData, DeviceInfo, LocationUpdate
from app.core.security import security
from app.core.database import db
from bson import ObjectId

router = APIRouter()
bearer_scheme = HTTPBearer()

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        payload = security.verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        try:
            user_doc = await db.users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user_doc = None
        if user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Convert ObjectId to string for Pydantic model
        user_doc["_id"] = str(user_doc["_id"])
        return User(**user_doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

@router.post("/register", response_model=TokenData, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        # Validate email format
        if not EMAIL_REGEX.match(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if user already exists
        existing_user = await db.users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = security.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "phone": user_data.phone,
            "password_hash": password_hash,
            "full_name": user_data.full_name,
            "preferred_language": user_data.preferred_language,
            "role": "user",
            "status": "active",
            "fcm_token": user_data.fcm_token,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "email_verified": False,
            "phone_verified": False,
            "preferred_transport_modes": ["bus", "train"],
            "accessibility_needs": []
        }
        
        # Insert user
        result = await db.users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Register device if FCM token provided
        if user_data.fcm_token:
            device_doc = {
                "user_id": user_id,
                "device_type": user_data.device_type,
                "fcm_token": user_data.fcm_token,
                "device_id": f"{user_data.device_type}_{user_id}",
                "app_version": "1.0.0",
                "os_version": "unknown",
                "last_active": datetime.utcnow(),
                "location_enabled": False,
                "notifications_enabled": True
            }
            await db.devices_collection.insert_one(device_doc)
        
        # Generate tokens
        token_data = {
            "sub": user_id,
            "email": user_data.email,
            "role": "user"
        }
        
        access_token = security.create_access_token(token_data)
        refresh_token = security.create_refresh_token(token_data)
        
        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,  # 30 minutes
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenData)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        # Find user by email
        user_doc = await db.users_collection.find_one({"email": login_data.email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not security.verify_password(login_data.password, user_doc["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check user status
        if user_doc.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is suspended"
            )
        
        user_id = str(user_doc["_id"])
        
        # Update last login
        await db.users_collection.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Update or create device record
        if login_data.fcm_token:
            await db.devices_collection.update_one(
                {"user_id": user_id, "device_type": login_data.device_type},
                {
                    "$set": {
                        "fcm_token": login_data.fcm_token,
                        "last_active": datetime.utcnow()
                    }
                },
                upsert=True
            )
        
        # Generate tokens
        token_data = {
            "sub": user_id,
            "email": user_doc["email"],
            "role": user_doc.get("role", "user")
        }
        
        access_token = security.create_access_token(token_data)
        refresh_token = security.create_refresh_token(token_data)
        
        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,  # 30 minutes
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh-token", response_model=TokenData)
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = security.verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")
        
        # Check if user still exists and is active
        try:
            user_doc = await db.users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user_doc = None
        if not user_doc or user_doc.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        token_data = {
            "sub": user_id,
            "email": user_doc["email"],
            "role": user_doc.get("role", "user")
        }
        
        new_access_token = security.create_access_token(token_data)
        new_refresh_token = security.create_refresh_token(token_data)
        
        return TokenData(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=1800,
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user and invalidate tokens"""
    try:
        # In a production system, you'd maintain a blacklist of tokens
        # For now, we'll just clear the FCM token
        await db.users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$unset": {"fcm_token": ""}}
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/me")
async def update_current_user_profile(
    user_updates: dict,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Filter allowed updates (exclude sensitive fields)
        allowed_fields = {
            "full_name", "profile_picture", "preferred_language",
            "preferred_transport_modes", "accessibility_needs", "phone"
        }
        
        updates = {k: v for k, v in user_updates.items() if k in allowed_fields}
        updates["updated_at"] = datetime.utcnow()
        
        await db.users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": updates}
        )
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

@router.post("/update-location")
async def update_user_location(
    location: LocationUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user's current location"""
    try:
        location_data = {
            "lat": location.latitude,
            "lng": location.longitude,
            "accuracy": location.accuracy,
            "timestamp": location.timestamp
        }
        
        await db.users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"last_location": location_data, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Location updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Location update failed: {str(e)}"
        )