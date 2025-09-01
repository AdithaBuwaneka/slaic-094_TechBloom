from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.models.user import User, DeviceInfo, PushNotification, LocationUpdate
from app.api.auth import get_current_user
from app.core.database import db

router = APIRouter()

class FCMTokenUpdate(BaseModel):
    fcm_token: str
    device_type: str
    device_id: str
    app_version: str = "1.0.0"
    os_version: str = "unknown"

class NotificationPreferences(BaseModel):
    disruptions: bool = True
    route_updates: bool = True
    promotions: bool = False
    general: bool = True

class OfflineSyncRequest(BaseModel):
    last_sync: datetime
    user_actions: List[dict] = []

@router.post("/devices/register")
async def register_device(
    device_data: FCMTokenUpdate,
    current_user: User = Depends(get_current_user)
):
    """Register or update user's device for push notifications"""
    try:
        device_doc = {
            "user_id": current_user.id,
            "device_type": device_data.device_type,
            "fcm_token": device_data.fcm_token,
            "device_id": device_data.device_id,
            "app_version": device_data.app_version,
            "os_version": device_data.os_version,
            "last_active": datetime.utcnow(),
            "location_enabled": False,
            "notifications_enabled": True
        }
        
        # Upsert device record
        await db.devices_collection.update_one(
            {"user_id": current_user.id, "device_id": device_data.device_id},
            {"$set": device_doc},
            upsert=True
        )
        
        # Update user's FCM token
        await db.users_collection.update_one(
            {"_id": current_user.id},
            {"$set": {"fcm_token": device_data.fcm_token}}
        )
        
        return {"message": "Device registered successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Device registration failed: {str(e)}"
        )

@router.get("/notifications/", response_model=List[Dict])
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False)
):
    """Get user's push notifications with pagination"""
    try:
        query = {"user_id": current_user.id}
        if unread_only:
            query["read_at"] = {"$exists": False}
            
        notifications_cursor = db.notifications_collection.find(query)\
            .sort("sent_at", -1)\
            .skip(offset)\
            .limit(limit)
        
        notifications = []
        async for notification in notifications_cursor:
            notifications.append({
                "id": str(notification["_id"]),
                "title": notification.get("title", ""),
                "body": notification.get("body", ""),
                "data": notification.get("data", {}),
                "sent_at": notification.get("sent_at").isoformat(),
                "read_at": notification.get("read_at").isoformat() if notification.get("read_at") else None,
                "notification_type": notification.get("notification_type", "general")
            })
        
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        result = await db.notifications_collection.update_one(
            {"_id": notification_id, "user_id": current_user.id},
            {"$set": {"read_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.post("/preferences/notifications")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update user's notification preferences"""
    try:
        await db.users_collection.update_one(
            {"_id": current_user.id},
            {"$set": {
                "notification_preferences": preferences.dict(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {"message": "Notification preferences updated"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.get("/sync/essential-data")
async def get_essential_data(
    current_user: User = Depends(get_current_user),
    last_sync: Optional[datetime] = Query(None)
):
    """Get essential data for offline functionality"""
    try:
        # Get recent bus routes (for offline route planning)
        bus_routes = []
        bus_cursor = db.bus_routes_collection.find().limit(50)
        async for route in bus_cursor:
            bus_routes.append({
                "id": str(route["_id"]),
                "route_number": route.get("route_number", ""),
                "origin": route.get("origin", ""),
                "destination": route.get("destination", ""),
                "stops": route.get("stops", []),
                "operator": route.get("operator", ""),
                "fare": route.get("fare", 0),
                "frequency": route.get("frequency", ""),
                "operating_hours": route.get("operating_hours", "")
            })
        
        # Get train routes
        train_routes = []
        train_cursor = db.train_routes_collection.find().limit(20)
        async for route in train_cursor:
            train_routes.append({
                "id": str(route["_id"]),
                "route_name": route.get("route_name", ""),
                "origin": route.get("origin", ""),
                "destination": route.get("destination", ""),
                "stops": route.get("stops", []),
                "operator": route.get("operator", ""),
                "classes": route.get("classes", []),
                "fares": route.get("fares", {}),
                "frequency": route.get("frequency", "")
            })
        
        # Get active disruptions
        current_time = datetime.utcnow()
        disruptions = []
        disruptions_cursor = db.disruptions_collection.find({
            "start_time": {"$lte": current_time},
            "$or": [
                {"end_time": {"$gte": current_time}},
                {"end_time": None}
            ]
        }).limit(10)
        
        async for disruption in disruptions_cursor:
            disruptions.append({
                "id": str(disruption["_id"]),
                "title": disruption.get("title", ""),
                "description": disruption.get("description", ""),
                "severity": disruption.get("severity", "medium"),
                "transport_mode": disruption.get("transport_mode", ""),
                "affected_stops": disruption.get("affected_stops", [])
            })
        
        # Emergency phrases for offline use
        emergency_phrases = {
            "en": {
                "help": "I need help",
                "emergency": "This is an emergency",
                "hospital": "Please take me to a hospital",
                "police": "Please call the police",
                "lost": "I am lost",
                "phone": "Can I use your phone?",
                "no_understand": "I don't understand",
                "thank_you": "Thank you"
            },
            "si": {
                "help": "කරුණාකර මට උදව් කරන්න",
                "emergency": "මේක හදිසි අවස්ථාවකි",
                "hospital": "කරුණාකර මාව රෝහලකට ගෙන යන්න",
                "police": "කරුණාකර පොලිසියට කතා කරන්න",
                "lost": "මම පාර අතරමං වෙලා",
                "phone": "ඔයාගේ ෆෝන් එක පාවිච්චි කරන්න පුළුවන්ද?",
                "no_understand": "මට තේරෙන්නේ නැහැ",
                "thank_you": "ඔබට ස්තූතියි"
            },
            "ta": {
                "help": "எனக்கு உதவி தேவை",
                "emergency": "இது அவசரநிலை",
                "hospital": "என்னை மருத்துவமனைக்கு அழைத்துச் செல்லுங்கள்",
                "police": "காவல்துறையை அழைக்கவும்",
                "lost": "நான் வழி தெரியாமல் இருக்கிறேன்",
                "phone": "உங்கள் தொலைபேசியை பயன்படுத்தலாமா?",
                "no_understand": "எனக்கு புரியவில்லை", 
                "thank_you": "நன்றி"
            }
        }
        
        return {
            "bus_routes": bus_routes,
            "train_routes": train_routes,
            "disruptions": disruptions,
            "emergency_phrases": emergency_phrases,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get essential data: {str(e)}"
        )

@router.post("/sync/user-actions")
async def sync_user_actions(
    sync_data: OfflineSyncRequest,
    current_user: User = Depends(get_current_user)
):
    """Sync user actions performed while offline"""
    try:
        synced_actions = []
        
        for action in sync_data.user_actions:
            action_type = action.get("type")
            
            if action_type == "location_update":
                await db.users_collection.update_one(
                    {"_id": current_user.id},
                    {"$set": {
                        "last_location": action.get("data"),
                        "updated_at": datetime.utcnow()
                    }}
                )
                synced_actions.append({"type": action_type, "status": "synced"})
                
            elif action_type == "journey_history":
                # Add to user's journey history
                journey_data = action.get("data", {})
                journey_data["user_id"] = current_user.id
                journey_data["synced_at"] = datetime.utcnow()
                
                await db.journey_history_collection.insert_one(journey_data)
                synced_actions.append({"type": action_type, "status": "synced"})
                
            elif action_type == "community_update":
                # Add community update
                update_data = action.get("data", {})
                update_data["user_id"] = current_user.id
                update_data["created_at"] = datetime.utcnow()
                update_data["verified"] = False
                
                await db.community_updates_collection.insert_one(update_data)
                synced_actions.append({"type": action_type, "status": "synced"})
            else:
                synced_actions.append({"type": action_type, "status": "unsupported"})
        
        return {
            "message": f"Synced {len(synced_actions)} actions",
            "synced_actions": synced_actions,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )

@router.get("/app/config")
async def get_app_config():
    """Get app configuration for mobile clients"""
    return {
        "api_version": "1.0.0",
        "min_app_version": "1.0.0",
        "features": {
            "offline_mode": True,
            "push_notifications": True,
            "location_services": True,
            "multi_language": True,
            "voice_assistance": False,
            "ar_navigation": False
        },
        "supported_languages": ["en", "si", "ta"],
        "default_language": "en",
        "cache_duration": 3600,  # 1 hour
        "max_offline_days": 7,
        "update_intervals": {
            "routes": 86400,  # 24 hours
            "disruptions": 300,  # 5 minutes
            "notifications": 60  # 1 minute
        }
    }