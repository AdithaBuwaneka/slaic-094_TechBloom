# User Preferences Management API Routes
# Travel preferences, notification settings, and user customization

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.auth_middleware import get_current_active_user
from app.core.database import db

router = APIRouter()

# Request Models
class TravelPreferencesRequest(BaseModel):
    preferred_transit_modes: Optional[List[str]] = Field(None, description="Preferred transport modes")
    max_walking_distance: Optional[float] = Field(None, ge=0, le=10, description="Max walking distance in km")
    budget_preference: Optional[str] = Field(None, description="Budget preference: low, medium, high")
    time_vs_cost_weight: Optional[float] = Field(None, ge=0, le=1, description="0=cost priority, 1=time priority")
    comfort_preference: Optional[float] = Field(None, ge=0, le=1, description="0=basic, 1=premium")
    accessibility_needs: Optional[List[str]] = Field(None, description="Accessibility requirements")
    avoid_preferences: Optional[List[str]] = Field(None, description="Things to avoid (tolls, highways, etc.)")
    default_departure_buffer: Optional[int] = Field(None, ge=0, le=60, description="Default buffer time in minutes")

class NotificationPreferencesRequest(BaseModel):
    email_notifications: Optional[bool] = Field(None, description="Enable email notifications")
    push_notifications: Optional[bool] = Field(None, description="Enable push notifications")
    sms_notifications: Optional[bool] = Field(None, description="Enable SMS notifications")
    disruption_alerts: Optional[bool] = Field(None, description="Enable disruption alerts")
    fare_change_alerts: Optional[bool] = Field(None, description="Enable fare change alerts")
    route_recommendations: Optional[bool] = Field(None, description="Enable route recommendations")

class FavoriteDestinationRequest(BaseModel):
    name: str = Field(..., description="Destination name")
    address: str = Field(..., description="Full address")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Lat/lng coordinates")
    category: Optional[str] = Field("other", description="Category: home, work, shopping, entertainment, other")
    notes: Optional[str] = Field(None, description="Personal notes")

# Response Models
class UserPreferencesResponse(BaseModel):
    travel_preferences: Dict[str, Any]
    notification_preferences: Dict[str, Any]
    favorite_destinations: List[Dict[str, Any]]
    usage_stats: Dict[str, Any]

@router.get("/travel-preferences")
async def get_travel_preferences(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get user's current travel preferences
    """
    return {
        "user_id": current_user["user_id"],
        "travel_preferences": current_user.get("travel_preferences", {}),
        "last_updated": current_user.get("updated_at")
    }

@router.put("/travel-preferences")
async def update_travel_preferences(
    preferences: TravelPreferencesRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update user's travel preferences
    Used after registration to customize user experience
    """
    try:
        # Get current preferences
        current_prefs = current_user.get("travel_preferences", {})
        
        # Update only provided fields
        updates = {}
        if preferences.preferred_transit_modes is not None:
            updates["travel_preferences.preferred_transit_modes"] = preferences.preferred_transit_modes
        if preferences.max_walking_distance is not None:
            updates["travel_preferences.max_walking_distance"] = preferences.max_walking_distance
        if preferences.budget_preference is not None:
            updates["travel_preferences.budget_preference"] = preferences.budget_preference
        if preferences.time_vs_cost_weight is not None:
            updates["travel_preferences.time_vs_cost_weight"] = preferences.time_vs_cost_weight
        if preferences.comfort_preference is not None:
            updates["travel_preferences.comfort_preference"] = preferences.comfort_preference
        if preferences.accessibility_needs is not None:
            updates["travel_preferences.accessibility_needs"] = preferences.accessibility_needs
        if preferences.avoid_preferences is not None:
            updates["travel_preferences.avoid_preferences"] = preferences.avoid_preferences
        if preferences.default_departure_buffer is not None:
            updates["travel_preferences.default_departure_buffer"] = preferences.default_departure_buffer
        
        updates["updated_at"] = datetime.utcnow()
        
        # Update database
        result = await db.database.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or no changes made"
            )
        
        # Get updated preferences
        updated_user = await db.database.users.find_one({"user_id": current_user["user_id"]})
        
        return {
            "message": "Travel preferences updated successfully",
            "travel_preferences": updated_user.get("travel_preferences", {}),
            "updated_at": updated_user.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update travel preferences: {str(e)}"
        )

@router.get("/notification-preferences")
async def get_notification_preferences(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get user's notification preferences
    """
    profile = current_user.get("profile", {})
    return {
        "user_id": current_user["user_id"],
        "notification_preferences": profile.get("notification_preferences", {}),
        "last_updated": current_user.get("updated_at")
    }

@router.put("/notification-preferences")
async def update_notification_preferences(
    preferences: NotificationPreferencesRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update user's notification preferences
    """
    try:
        # Update only provided fields
        updates = {}
        if preferences.email_notifications is not None:
            updates["profile.notification_preferences.email_notifications"] = preferences.email_notifications
        if preferences.push_notifications is not None:
            updates["profile.notification_preferences.push_notifications"] = preferences.push_notifications
        if preferences.sms_notifications is not None:
            updates["profile.notification_preferences.sms_notifications"] = preferences.sms_notifications
        if preferences.disruption_alerts is not None:
            updates["profile.notification_preferences.disruption_alerts"] = preferences.disruption_alerts
        if preferences.fare_change_alerts is not None:
            updates["profile.notification_preferences.fare_change_alerts"] = preferences.fare_change_alerts
        if preferences.route_recommendations is not None:
            updates["profile.notification_preferences.route_recommendations"] = preferences.route_recommendations
        
        updates["updated_at"] = datetime.utcnow()
        
        # Update database
        result = await db.database.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or no changes made"
            )
        
        return {"message": "Notification preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification preferences: {str(e)}"
        )

@router.get("/favorite-destinations")
async def get_favorite_destinations(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get user's favorite destinations
    """
    usage_stats = current_user.get("usage_stats", {})
    return {
        "user_id": current_user["user_id"],
        "favorite_destinations": usage_stats.get("favorite_destinations", [])
    }

@router.post("/favorite-destinations")
async def add_favorite_destination(
    destination: FavoriteDestinationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Add a favorite destination
    """
    try:
        new_destination = {
            "destination_id": f"dest_{datetime.utcnow().timestamp()}",
            "name": destination.name,
            "address": destination.address,
            "coordinates": destination.coordinates,
            "category": destination.category,
            "notes": destination.notes,
            "added_at": datetime.utcnow(),
            "usage_count": 0
        }
        
        # Add to favorites list
        result = await db.database.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$push": {"usage_stats.favorite_destinations": new_destination},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "message": "Favorite destination added successfully",
            "destination": new_destination
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add favorite destination: {str(e)}"
        )

@router.delete("/favorite-destinations/{destination_id}")
async def remove_favorite_destination(
    destination_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Remove a favorite destination
    """
    try:
        result = await db.database.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$pull": {"usage_stats.favorite_destinations": {"destination_id": destination_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination not found"
            )
        
        return {"message": "Favorite destination removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove favorite destination: {str(e)}"
        )

@router.get("/usage-stats")
async def get_usage_statistics(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get user's usage statistics
    """
    usage_stats = current_user.get("usage_stats", {})
    return {
        "user_id": current_user["user_id"],
        "usage_stats": usage_stats,
        "member_since": current_user.get("created_at")
    }

@router.post("/update-usage-stats")
async def update_usage_statistics(
    stats_update: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update user usage statistics (called internally after trip planning)
    """
    try:
        updates = {}
        
        # Update usage statistics
        if "trip_completed" in stats_update:
            updates["$inc"] = {"usage_stats.total_trips_planned": 1}
        
        if "distance_traveled" in stats_update:
            updates.setdefault("$inc", {})["usage_stats.total_distance_traveled"] = stats_update["distance_traveled"]
        
        if "fare_saved" in stats_update:
            updates.setdefault("$inc", {})["usage_stats.total_fare_saved"] = stats_update["fare_saved"]
        
        if "mode_used" in stats_update:
            updates["$set"] = {"usage_stats.most_used_mode": stats_update["mode_used"]}
        
        updates.setdefault("$set", {})["updated_at"] = datetime.utcnow()
        
        # Update database
        result = await db.database.users.update_one(
            {"user_id": current_user["user_id"]},
            updates
        )
        
        return {"message": "Usage statistics updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update usage statistics: {str(e)}"
        )

@router.get("/all-preferences", response_model=UserPreferencesResponse)
async def get_all_user_preferences(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get all user preferences in one response
    """
    profile = current_user.get("profile", {})
    usage_stats = current_user.get("usage_stats", {})
    
    return {
        "travel_preferences": current_user.get("travel_preferences", {}),
        "notification_preferences": profile.get("notification_preferences", {}),
        "favorite_destinations": usage_stats.get("favorite_destinations", []),
        "usage_stats": usage_stats
    }