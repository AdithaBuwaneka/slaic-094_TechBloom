from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

from app.models.user import User
from app.api.auth import get_current_user
from app.core.database import db

router = APIRouter()

class EventTracking(BaseModel):
    event_type: str
    event_name: str
    properties: Dict[str, Any] = {}
    user_agent: Optional[str] = None
    device_info: Optional[Dict] = None

class JourneyAnalytics(BaseModel):
    origin: str
    destination: str
    transport_mode: str
    search_duration: Optional[float] = None  # seconds
    booking_completed: bool = False
    user_satisfaction: Optional[int] = None  # 1-5 rating
    issues_encountered: List[str] = []

@router.post("/track/event")
async def track_event(
    event: EventTracking,
    current_user: User = Depends(get_current_user)
):
    """Track user events for analytics"""
    try:
        analytics_event = {
            "user_id": current_user.id,
            "event_type": event.event_type,
            "event_name": event.event_name,
            "properties": event.properties,
            "user_agent": event.user_agent,
            "device_info": event.device_info,
            "timestamp": datetime.utcnow(),
            "user_email": current_user.email,
            "user_role": current_user.role
        }
        
        await db.analytics_events_collection.insert_one(analytics_event)
        
        return {"message": "Event tracked successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event tracking failed: {str(e)}"
        )

@router.post("/track/journey")
async def track_journey_analytics(
    journey: JourneyAnalytics,
    current_user: User = Depends(get_current_user)
):
    """Track detailed journey analytics"""
    try:
        journey_analytics = {
            "user_id": current_user.id,
            "origin": journey.origin,
            "destination": journey.destination,
            "transport_mode": journey.transport_mode,
            "search_duration": journey.search_duration,
            "booking_completed": journey.booking_completed,
            "user_satisfaction": journey.user_satisfaction,
            "issues_encountered": journey.issues_encountered,
            "timestamp": datetime.utcnow(),
            "user_preferences": {
                "preferred_language": current_user.preferred_language,
                "preferred_transport_modes": current_user.preferred_transport_modes,
                "accessibility_needs": current_user.accessibility_needs
            }
        }
        
        await db.journey_analytics_collection.insert_one(journey_analytics)
        
        # Update user's journey history
        journey_history = {
            "user_id": current_user.id,
            "origin": journey.origin,
            "destination": journey.destination,
            "transport_mode": journey.transport_mode,
            "created_at": datetime.utcnow(),
            "completed": journey.booking_completed
        }
        
        await db.journey_history_collection.insert_one(journey_history)
        
        return {"message": "Journey analytics tracked successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Journey tracking failed: {str(e)}"
        )

@router.get("/user/insights")
async def get_user_insights(
    current_user: User = Depends(get_current_user)
):
    """Get personalized insights for the user"""
    try:
        # Get user's journey patterns
        journey_cursor = db.journey_analytics_collection.find({"user_id": current_user.id})\
            .sort("timestamp", -1)\
            .limit(50)
        
        journeys = []
        route_frequency = {}
        transport_mode_usage = {}
        
        async for journey in journey_cursor:
            journeys.append(journey)
            
            # Track route frequency
            route_key = f"{journey['origin']}-{journey['destination']}"
            route_frequency[route_key] = route_frequency.get(route_key, 0) + 1
            
            # Track transport mode usage
            mode = journey['transport_mode']
            transport_mode_usage[mode] = transport_mode_usage.get(mode, 0) + 1
        
        # Calculate insights
        most_frequent_route = max(route_frequency.items(), key=lambda x: x[1]) if route_frequency else None
        preferred_transport = max(transport_mode_usage.items(), key=lambda x: x[1]) if transport_mode_usage else None
        
        # Average satisfaction
        satisfaction_scores = [j.get('user_satisfaction') for j in journeys if j.get('user_satisfaction')]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
        
        # Money-saving suggestions
        savings_suggestions = []
        if preferred_transport and preferred_transport[0] == 'bus':
            savings_suggestions.append("Consider monthly bus passes for frequent travel")
        if current_user.passenger_type == 'student':
            savings_suggestions.append("Remember to use your student discount")
        
        return {
            "total_journeys": len(journeys),
            "most_frequent_route": {
                "route": most_frequent_route[0],
                "count": most_frequent_route[1]
            } if most_frequent_route else None,
            "preferred_transport": {
                "mode": preferred_transport[0],
                "usage_count": preferred_transport[1]
            } if preferred_transport else None,
            "average_satisfaction": round(avg_satisfaction, 1) if avg_satisfaction else None,
            "route_frequency": dict(sorted(route_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
            "transport_mode_distribution": transport_mode_usage,
            "savings_suggestions": savings_suggestions,
            "insights_generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user insights: {str(e)}"
        )

@router.get("/performance/metrics")
async def get_performance_metrics():
    """Get system performance metrics (public endpoint for monitoring)"""
    try:
        # Recent API response times (mock data - would come from actual monitoring)
        performance_metrics = {
            "avg_response_time": 245,  # ms
            "p95_response_time": 800,  # ms
            "error_rate": 0.02,  # 2%
            "uptime": 99.98,  # percentage
            "active_users_24h": 1247,
            "api_calls_24h": 15678,
            "database_health": "healthy",
            "cache_hit_rate": 87.5,  # percentage
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Add real database connection test
        try:
            await db.users_collection.count_documents({}, limit=1)
            performance_metrics["database_status"] = "connected"
            performance_metrics["database_response_time"] = 45  # ms
        except:
            performance_metrics["database_status"] = "error"
            performance_metrics["database_response_time"] = None
        
        return performance_metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance metrics failed: {str(e)}"
        )

@router.post("/feedback/submit")
async def submit_feedback(
    feedback_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Submit user feedback"""
    try:
        feedback = {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "feedback_type": feedback_data.get("type", "general"),
            "subject": feedback_data.get("subject", ""),
            "message": feedback_data.get("message", ""),
            "rating": feedback_data.get("rating", None),
            "category": feedback_data.get("category", "app"),
            "device_info": feedback_data.get("device_info", {}),
            "app_version": feedback_data.get("app_version", "1.0.0"),
            "screenshot_url": feedback_data.get("screenshot_url", None),
            "contact_email": feedback_data.get("contact_email", current_user.email),
            "status": "new",
            "created_at": datetime.utcnow(),
            "priority": feedback_data.get("priority", "medium")
        }
        
        result = await db.feedback_collection.insert_one(feedback)
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": str(result.inserted_id),
            "status": "received"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}"
        )

@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """Get intelligent search suggestions based on user history and popular searches"""
    try:
        suggestions = []
        
        # Get user's search history
        user_searches = []
        journey_cursor = db.journey_history_collection.find({"user_id": current_user.id})\
            .sort("created_at", -1)\
            .limit(20)
        
        async for journey in journey_cursor:
            origin = journey.get("origin", "")
            destination = journey.get("destination", "")
            if query.lower() in origin.lower() or query.lower() in destination.lower():
                user_searches.append({
                    "type": "history",
                    "text": f"{origin} → {destination}",
                    "origin": origin,
                    "destination": destination,
                    "frequency": 1  # Would be calculated from actual usage
                })
        
        # Get popular destinations matching query
        popular_locations = [
            "Colombo", "Kandy", "Galle", "Nuwara Eliya", "Jaffna", "Trincomalee",
            "Anuradhapura", "Polonnaruwa", "Sigiriya", "Dambulla", "Matara",
            "Negombo", "Mount Lavinia", "Hikkaduwa", "Unawatuna", "Ella"
        ]
        
        for location in popular_locations:
            if query.lower() in location.lower():
                suggestions.append({
                    "type": "location",
                    "text": location,
                    "category": "destination",
                    "popularity_score": 95  # Mock popularity
                })
        
        # Combine and sort suggestions
        all_suggestions = user_searches + suggestions
        
        # Sort by relevance (history first, then popularity)
        all_suggestions.sort(key=lambda x: (
            x["type"] == "history",  # History suggestions first
            x.get("popularity_score", 0),
            x.get("frequency", 0)
        ), reverse=True)
        
        return {
            "query": query,
            "suggestions": all_suggestions[:limit],
            "total": len(all_suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search suggestions failed: {str(e)}"
        )

@router.get("/app/feature-flags")
async def get_feature_flags(
    current_user: User = Depends(get_current_user)
):
    """Get feature flags for the mobile app"""
    try:
        # Feature flags based on user type and app version
        feature_flags = {
            "offline_mode": True,
            "voice_search": True,
            "ar_navigation": False,
            "real_time_tracking": current_user.role == "admin",
            "beta_features": current_user.role in ["admin", "moderator"],
            "advanced_analytics": current_user.role == "admin",
            "multi_language": True,
            "push_notifications": True,
            "location_services": True,
            "fare_prediction": True,
            "route_optimization": True,
            "community_features": True,
            "emergency_assistance": True
        }
        
        # A/B testing flags (could be database-driven)
        ab_testing = {
            "new_ui_design": hash(current_user.id) % 2 == 0,  # 50% split
            "improved_search": hash(current_user.email) % 3 == 0,  # 33% split
            "enhanced_recommendations": True
        }
        
        return {
            "feature_flags": feature_flags,
            "ab_testing": ab_testing,
            "user_segment": current_user.role,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature flags failed: {str(e)}"
        )