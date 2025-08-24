from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.models.user_management import (
    UserRegistrationRequest, UserLoginRequest, UserProfileUpdateRequest,
    User, UserPreferences
)
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()
user_service = UserService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    token_data = user_service._verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return token_data["user_id"]


@router.post("/register")
async def register_user(request: UserRegistrationRequest):
    """Register a new user"""
    result = await user_service.register_user(request)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "message": result["message"],
        "data": result["data"]
    }


@router.post("/login")
async def login_user(request: UserLoginRequest):
    """Authenticate user login"""
    result = await user_service.authenticate_user(request)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "message": result["message"],
        "data": result["data"]
    }


@router.post("/verify-email")
async def verify_email(verification_token: str):
    """Verify user email address"""
    result = await user_service.verify_email(verification_token)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "message": result["message"],
        "data": result["data"]
    }


@router.get("/profile")
async def get_user_profile(current_user: str = Depends(get_current_user)):
    """Get current user profile"""
    user = await user_service._find_user_by_id(current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "status": "success",
        "data": {
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "phone_number": user.phone_number,
            "profile_picture_url": user.profile_picture_url,
            "home_location": user.home_location.model_dump() if user.home_location else None,
            "work_location": user.work_location.model_dump() if user.work_location else None,
            "language_preference": user.language_preference,
            "accessibility_features": user.accessibility_features,
            "role": user.role,
            "status": user.status,
            "is_email_verified": user.is_email_verified,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    }


@router.put("/profile")
async def update_user_profile(
    request: UserProfileUpdateRequest,
    current_user: str = Depends(get_current_user)
):
    """Update user profile"""
    result = await user_service.update_profile(current_user, request)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "message": result["message"],
        "data": result["data"]
    }


@router.get("/preferences")
async def get_user_preferences(current_user: str = Depends(get_current_user)):
    """Get user preferences"""
    result = await user_service.get_user_preferences(current_user)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "data": result["data"]
    }


@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Update user preferences"""
    result = await user_service.update_user_preferences(current_user, preferences)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "message": result["message"],
        "data": result["data"]
    }


@router.get("/stats")
async def get_user_stats(
    period_days: int = 30,
    current_user: str = Depends(get_current_user)
):
    """Get user statistics"""
    result = await user_service.get_user_stats(current_user, period_days)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "status": "success",
        "data": result["data"]
    }


class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh-token")
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    refresh_token = request.refresh_token
    token_data = user_service._verify_token(refresh_token)
    if not token_data or token_data.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Generate new access token
    new_access_token, expires_at = user_service._generate_token(token_data["user_id"], "access")
    
    return {
        "status": "success",
        "data": {
            "access_token": new_access_token,
            "expires_at": expires_at.isoformat(),
            "token_type": "Bearer"
        }
    }


@router.post("/logout")
async def logout_user(current_user: str = Depends(get_current_user)):
    """Logout user (invalidate session)"""
    # In a real implementation, you would invalidate the token in a blacklist
    # For now, we'll just return success
    return {
        "status": "success",
        "message": "Logged out successfully"
    }


@router.get("/test-auth")
async def test_authentication(current_user: str = Depends(get_current_user)):
    """Test endpoint to verify authentication"""
    return {
        "status": "success",
        "message": "Authentication successful",
        "user_id": current_user
    }