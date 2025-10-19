# Mobile App Specific API Routes
# Device registration, push notifications, and mobile-optimized endpoints

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.push_notification_service import push_notification_service
from app.core.auth_middleware import get_current_active_user, get_optional_user
from app.core.database import db
import uuid

router = APIRouter()

# Request Models
class DeviceRegistrationRequest(BaseModel):
    device_token: str = Field(..., description="Expo push token or FCM token")
    platform: str = Field(..., description="Platform: ios or android")
    app_version: str = Field(..., description="App version")
    device_info: Dict[str, Any] = Field(default={}, description="Device information (model, OS version, etc.)")

class PushNotificationRequest(BaseModel):
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Dict[str, Any] = Field(default={}, description="Additional data")
    user_ids: Optional[List[str]] = Field(None, description="Specific user IDs to send to")

class LocationUpdateRequest(BaseModel):
    latitude: float = Field(..., description="Current latitude")
    longitude: float = Field(..., description="Current longitude")
    accuracy: Optional[float] = Field(None, description="Location accuracy in meters")
    timestamp: Optional[datetime] = Field(None, description="Location timestamp")

class OfflineDataRequest(BaseModel):
    routes: List[str] = Field(default=[], description="Route IDs to cache offline")
    preferences: Dict[str, Any] = Field(default={}, description="User preferences for offline data")

# Response Models
class DeviceRegistrationResponse(BaseModel):
    status: str
    message: str
    device_id: str
    registered_at: datetime

class MobileAppConfigResponse(BaseModel):
    app_config: Dict[str, Any]
    feature_flags: Dict[str, bool]
    api_endpoints: Dict[str, str]
    push_notifications_enabled: bool

@router.post("/register-device", response_model=DeviceRegistrationResponse)
async def register_mobile_device(
    request: DeviceRegistrationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Register a mobile device for push notifications
    """
    try:
        # Add app version to device info
        device_info = request.device_info.copy()
        device_info["app_version"] = request.app_version
        device_info["registered_via"] = "mobile_app"
        
        result = await push_notification_service.register_device(
            user_id=current_user["user_id"],
            device_token=request.device_token,
            platform=request.platform,
            device_info=device_info
        )
        
        if result["status"] == "success":
            return DeviceRegistrationResponse(
                status="success",
                message=result["message"],
                device_id=result["device_id"],
                registered_at=datetime.utcnow()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Device registration failed: {str(e)}"
        )

@router.delete("/unregister-device")
async def unregister_mobile_device(
    device_token: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Unregister a mobile device from push notifications
    """
    try:
        result = await push_notification_service.unregister_device(
            user_id=current_user["user_id"],
            device_token=device_token
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Device unregistration failed: {str(e)}"
        )

@router.post("/send-test-notification")
async def send_test_notification(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Send a test push notification to the current user's devices
    """
    try:
        result = await push_notification_service.send_notification(
            user_id=current_user["user_id"],
            title="Test Notification",
            body=f"Hello {current_user['name']}! Your notifications are working correctly.",
            data={"type": "test", "timestamp": datetime.utcnow().isoformat()}
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test notification failed: {str(e)}"
        )

@router.get("/notifications", response_model=List[Dict[str, Any]])
async def get_user_notifications(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get notification history for the current user
    """
    try:
        notifications = await push_notification_service.get_user_notifications(
            user_id=current_user["user_id"],
            limit=limit
        )
        
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Mark a notification as read
    """
    try:
        result = await push_notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user["user_id"]
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Mark all notifications as read for the current user
    """
    try:
        # Get all user notifications
        notifications = await push_notification_service.get_user_notifications(
            user_id=current_user["user_id"],
            limit=1000
        )

        marked_count = 0
        for notification in notifications:
            # Check if already read by this user
            if notification.get("read_by") and current_user["user_id"] in notification.get("read_by", []):
                continue

            # Mark as read
            await push_notification_service.mark_notification_read(
                notification_id=notification["notification_id"],
                user_id=current_user["user_id"]
            )
            marked_count += 1

        return {
            "status": "success",
            "message": f"Marked {marked_count} notifications as read",
            "marked_count": marked_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.post("/update-location")
async def update_user_location(
    request: LocationUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update user's current location for location-based services
    """
    try:
        location_data = {
            "user_id": current_user["user_id"],
            "latitude": request.latitude,
            "longitude": request.longitude,
            "accuracy": request.accuracy,
            "timestamp": request.timestamp or datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Update or insert location
        result = await db.database.user_locations.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": location_data},
            upsert=True
        )
        
        return {
            "status": "success",
            "message": "Location updated successfully",
            "timestamp": location_data["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Location update failed: {str(e)}"
        )

@router.get("/app-config", response_model=MobileAppConfigResponse)
async def get_mobile_app_config(
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get mobile app configuration and feature flags
    """
    try:
        # Base configuration for all users
        config = {
            "api_base_url": "/api/v1",
            "google_maps_enabled": True,
            "weather_integration_enabled": True,
            "multilingual_support": ["en", "si", "ta"],
            "sri_lankan_transit_modes": ["bus", "train", "tuk-tuk"],
            "max_route_alternatives": 5,
            "cache_duration_hours": 24
        }
        
        # User-specific configuration
        if current_user:
            user_preferences = current_user.get("travel_preferences", {})
            config.update({
                "user_preferred_modes": user_preferences.get("preferred_transit_modes", ["bus", "train"]),
                "max_walking_distance": user_preferences.get("max_walking_distance", 1.0),
                "preferred_language": current_user.get("profile", {}).get("preferred_language", "en")
            })
        
        # Feature flags
        feature_flags = {
            "push_notifications": True,
            "offline_mode": True,
            "real_time_tracking": True,
            "community_reporting": True,
            "ai_route_optimization": True,
            "disruption_monitoring": True,
            "fare_optimization": True,
            "multi_language_support": True,
            "location_services": True,
            "background_location": False  # Requires special permissions
        }
        
        # API endpoints for mobile app
        api_endpoints = {
            "travel_planning": "/api/v1/travel/plan-route",
            "user_preferences": "/api/v1/user-preferences",
            "weather": "/api/v1/weather",
            "sri_lanka_transit": "/api/v1/sri-lanka",
            "community": "/api/v1/community",
            "chatbot": "/api/v1/chatbot/ask",
            "auth": "/api/v1/auth",
            "mobile": "/api/v1/mobile"
        }
        
        return MobileAppConfigResponse(
            app_config=config,
            feature_flags=feature_flags,
            api_endpoints=api_endpoints,
            push_notifications_enabled=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get app config: {str(e)}"
        )

@router.post("/offline-data")
async def prepare_offline_data(
    request: OfflineDataRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Prepare and return data for offline usage
    """
    try:
        offline_data = {
            "user_id": current_user["user_id"],
            "prepared_at": datetime.utcnow(),
            "data": {}
        }
        
        # Get user's favorite routes if requested
        if request.routes:
            routes_data = []
            for route_id in request.routes:
                route = await db.database.transit_routes.find_one({"route_id": route_id})
                if route:
                    route["_id"] = str(route["_id"])
                    routes_data.append(route)
            offline_data["data"]["routes"] = routes_data
        
        # Get user's favorite destinations
        favorites = current_user.get("usage_stats", {}).get("favorite_destinations", [])
        offline_data["data"]["favorite_destinations"] = favorites
        
        # Get user preferences for offline use
        offline_data["data"]["user_preferences"] = current_user.get("travel_preferences", {})
        
        # Get basic Sri Lankan transit data
        offline_data["data"]["transit_modes"] = [
            {"id": "bus", "name": "Bus", "icon": "bus"},
            {"id": "train", "name": "Train", "icon": "train"},
            {"id": "tuk-tuk", "name": "Tuk-tuk", "icon": "car"},
            {"id": "uber", "name": "Uber", "icon": "car"}
        ]
        
        return {
            "status": "success",
            "message": "Offline data prepared successfully",
            "data_size": len(str(offline_data)),
            "offline_data": offline_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Offline data preparation failed: {str(e)}"
        )

@router.get("/health")
async def mobile_health_check():
    """
    Mobile-specific health check endpoint
    """
    try:
        # Check database connection
        await db.database.command("ping")
        
        # Check push notification service
        push_service_status = "operational"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "database": "operational",
                "push_notifications": push_service_status,
                "api": "operational"
            },
            "mobile_features": {
                "device_registration": "available",
                "push_notifications": "available",
                "offline_data": "available",
                "location_services": "available"
            }
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/user-devices")
async def get_user_devices(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get all registered devices for the current user
    """
    try:
        devices = await db.database.device_tokens.find({
            "user_id": current_user["user_id"],
            "is_active": True
        }).to_list(length=None)
        
        # Clean up device data for response
        for device in devices:
            device["_id"] = str(device["_id"])
        
        return {
            "status": "success",
            "device_count": len(devices),
            "devices": devices
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user devices: {str(e)}"
        )