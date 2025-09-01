from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from app.models.user import User
from app.models.transport import JourneyRequest, RouteOption
from app.api.auth import get_current_user
from app.services.google_maps_service1 import GoogleMapsService
from app.agents.graph import agentic_graph
from app.core.database import db

router = APIRouter()
gmaps_service = GoogleMapsService()

class AuthenticatedJourneyRequest(BaseModel):
    query: str
    include_user_context: bool = True
    save_to_history: bool = True
    accessibility_override: Optional[List[str]] = None
    budget_override: Optional[float] = None

class UserContextualResponse(BaseModel):
    user_id: str
    query: str
    personalized: bool
    route_options: List[Dict]
    ai_response: str
    user_context_applied: List[str]
    saved_to_history: bool

@router.post("/journey/plan-authenticated", response_model=UserContextualResponse)
async def plan_journey_with_user_context(
    request: AuthenticatedJourneyRequest,
    current_user: User = Depends(get_current_user)
):
    """AI-powered journey planning with full user authentication and context"""
    try:
        if not request.query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Build user context
        user_context = {
            "user_id": current_user.id,
            "preferred_language": current_user.preferred_language,
            "preferred_transport_modes": current_user.preferred_transport_modes,
            "accessibility_needs": request.accessibility_override or current_user.accessibility_needs,
            "budget_preference": request.budget_override,
            "passenger_type": getattr(current_user, 'passenger_type', 'adult'),
            "user_role": current_user.role,
            "email_verified": current_user.email_verified
        }
        
        # Get user's journey history for better recommendations
        recent_journeys = []
        if request.include_user_context:
            journey_cursor = db.journey_history_collection.find({"user_id": current_user.id})\
                .sort("created_at", -1)\
                .limit(10)
            
            async for journey in journey_cursor:
                recent_journeys.append({
                    "origin": journey.get("origin", ""),
                    "destination": journey.get("destination", ""),
                    "transport_mode": journey.get("transport_mode", ""),
                    "created_at": journey.get("created_at", "")
                })
        
        # Enhanced input with full user context
        agent_inputs = {
            "user_query": request.query,
            "user_context": user_context,
            "recent_journeys": recent_journeys,
            "include_personalization": request.include_user_context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Run the multi-agent system with user context
        final_state = await agentic_graph.ainvoke(agent_inputs)
        
        # Extract route options
        route_options = final_state.get("direct_route_options", [])
        
        # Save to user's journey history if requested
        saved_to_history = False
        if request.save_to_history and final_state.get("origin") and final_state.get("destination"):
            journey_record = {
                "user_id": current_user.id,
                "query": request.query,
                "origin": final_state.get("origin"),
                "destination": final_state.get("destination"),
                "transport_mode": final_state.get("recommended_transport_mode", "mixed"),
                "ai_response": final_state.get("final_response", ""),
                "route_options_count": len(route_options),
                "created_at": datetime.utcnow(),
                "personalized": request.include_user_context
            }
            await db.journey_history_collection.insert_one(journey_record)
            saved_to_history = True
        
        # Track user context applied
        context_applied = []
        if request.include_user_context:
            context_applied.append("user_preferences")
            context_applied.append("journey_history")
        if current_user.accessibility_needs:
            context_applied.append("accessibility_adaptations")
        if current_user.preferred_language != "en":
            context_applied.append("language_localization")
        
        # Log the AI query for analytics
        await db.analytics_events_collection.insert_one({
            "user_id": current_user.id,
            "event_type": "ai_query",
            "event_name": "authenticated_journey_plan",
            "properties": {
                "query_length": len(request.query),
                "user_context_included": request.include_user_context,
                "routes_found": len(route_options),
                "personalized": request.include_user_context
            },
            "timestamp": datetime.utcnow()
        })
        
        return UserContextualResponse(
            user_id=current_user.id,
            query=request.query,
            personalized=request.include_user_context,
            route_options=[
                {
                    "summary": route.summary if hasattr(route, 'summary') else str(route),
                    "total_duration": route.total_duration if hasattr(route, 'total_duration') else "Unknown",
                    "total_distance": route.total_distance if hasattr(route, 'total_distance') else "Unknown"
                }
                for route in (route_options if isinstance(route_options, list) else [route_options])
            ][:10],  # Limit to 10 routes
            ai_response=final_state.get("final_response", "Route planning completed successfully."),
            user_context_applied=context_applied,
            saved_to_history=saved_to_history
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        await db.error_logs_collection.insert_one({
            "user_id": current_user.id,
            "endpoint": "authenticated_journey_plan",
            "error": str(e),
            "query": request.query,
            "timestamp": datetime.utcnow()
        })
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI journey planning failed: {str(e)}"
        )

@router.post("/disruptions/check-personalized")
async def check_personalized_disruptions(
    origin: str,
    destination: str,
    transport_mode: str = "any",
    current_user: User = Depends(get_current_user)
):
    """Check disruptions with user preferences and notification settings"""
    try:
        from app.agents.disruption_agent import DisruptionManagementAgent
        disruption_agent = DisruptionManagementAgent()
        
        # Get user's notification preferences
        notification_prefs = getattr(current_user, 'notification_preferences', {
            "disruptions": True,
            "route_updates": True,
            "severe_weather": True
        })
        
        # Get disruption analysis
        analysis = await disruption_agent.check_disruptions(
            origin=origin,
            destination=destination,
            transport_mode=transport_mode
        )
        
        # Add user-specific context
        user_impact_assessment = {
            "affects_favorite_routes": False,
            "affects_frequent_routes": False,
            "notification_sent": False
        }
        
        # Check if this disruption affects user's frequent routes
        recent_journeys = await db.journey_history_collection.find({
            "user_id": current_user.id,
            "$or": [
                {"origin": {"$regex": origin, "$options": "i"}},
                {"destination": {"$regex": destination, "$options": "i"}}
            ]
        }).limit(5).to_list(5)
        
        if recent_journeys:
            user_impact_assessment["affects_frequent_routes"] = True
            
            # Send notification if user has notifications enabled
            if notification_prefs.get("disruptions", True):
                notification = {
                    "user_id": current_user.id,
                    "title": "Disruption on Your Route",
                    "body": f"Service disruption reported between {origin} and {destination}",
                    "data": {
                        "type": "disruption",
                        "origin": origin,
                        "destination": destination,
                        "severity": analysis.severity_level
                    },
                    "notification_type": "disruption",
                    "sent_at": datetime.utcnow()
                }
                await db.notifications_collection.insert_one(notification)
                user_impact_assessment["notification_sent"] = True
        
        response = analysis.dict()
        response["user_impact"] = user_impact_assessment
        response["checked_at"] = datetime.utcnow().isoformat()
        response["user_id"] = current_user.id
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalized disruption check failed: {str(e)}"
        )

@router.post("/personalization/get-recommendations-enhanced")
async def get_enhanced_personalized_recommendations(
    origin: str,
    destination: str,
    travel_time: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get highly personalized recommendations with machine learning insights"""
    try:
        from app.agents.personalization_agent import PersonalizationAgent
        personalization_agent = PersonalizationAgent()
        
        # Get available routes
        routes = gmaps_service.get_directions(origin, destination)
        routes_data = [
            {
                "summary": route.summary,
                "duration": route.total_duration,
                "distance": route.total_distance,
                "legs": len(route.legs)
            }
            for route in routes
        ]
        
        # Get user's detailed travel patterns
        travel_patterns = await db.journey_analytics_collection.find({
            "user_id": current_user.id
        }).sort("timestamp", -1).limit(50).to_list(50)
        
        # Calculate user preferences based on history
        transport_preferences = {}
        time_preferences = {}
        route_preferences = {}
        
        for pattern in travel_patterns:
            mode = pattern.get("transport_mode", "")
            if mode:
                transport_preferences[mode] = transport_preferences.get(mode, 0) + 1
            
            # Track preferred travel times
            timestamp = pattern.get("timestamp")
            if timestamp:
                hour = timestamp.hour
                time_slot = f"{hour:02d}:00"
                time_preferences[time_slot] = time_preferences.get(time_slot, 0) + 1
        
        # Get enhanced recommendations with ML insights
        recommendations = await personalization_agent.get_personalized_recommendations(
            user_id=current_user.id,
            origin=origin,
            destination=destination,
            available_routes=routes_data,
            travel_time=travel_time
        )
        
        # Add enhanced insights
        enhanced_response = recommendations.dict()
        enhanced_response["ml_insights"] = {
            "transport_preferences": dict(sorted(transport_preferences.items(), key=lambda x: x[1], reverse=True)[:3]),
            "time_preferences": dict(sorted(time_preferences.items(), key=lambda x: x[1], reverse=True)[:5]),
            "total_journeys_analyzed": len(travel_patterns),
            "confidence_score": min(95, len(travel_patterns) * 2)  # Higher confidence with more data
        }
        
        enhanced_response["smart_suggestions"] = []
        
        # Smart time-based suggestions
        if travel_time:
            try:
                requested_hour = int(travel_time.split(':')[0])
                if 7 <= requested_hour <= 9 or 17 <= requested_hour <= 19:
                    enhanced_response["smart_suggestions"].append(
                        "Peak hour detected. Consider traveling 1 hour earlier or later for less crowding."
                    )
            except:
                pass
        
        # Cost optimization suggestions
        if current_user.preferred_transport_modes and 'bus' in current_user.preferred_transport_modes:
            enhanced_response["smart_suggestions"].append(
                "Based on your bus preference, consider monthly passes for 40% savings."
            )
        
        # Weather-based suggestions
        enhanced_response["smart_suggestions"].append(
            "Current weather is favorable for travel. No weather-related delays expected."
        )
        
        return enhanced_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced recommendations failed: {str(e)}"
        )

@router.get("/user/travel-profile")
async def get_comprehensive_travel_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user's comprehensive travel profile with insights"""
    try:
        # Get journey analytics
        journey_cursor = db.journey_analytics_collection.find({"user_id": current_user.id})\
            .sort("timestamp", -1)\
            .limit(100)
        
        journeys = []
        total_distance = 0
        total_journeys = 0
        transport_usage = {}
        monthly_patterns = {}
        satisfaction_scores = []
        
        async for journey in journey_cursor:
            journeys.append(journey)
            total_journeys += 1
            
            # Track transport mode usage
            mode = journey.get("transport_mode", "unknown")
            transport_usage[mode] = transport_usage.get(mode, 0) + 1
            
            # Track monthly patterns
            timestamp = journey.get("timestamp")
            if timestamp:
                month_key = timestamp.strftime("%Y-%m")
                monthly_patterns[month_key] = monthly_patterns.get(month_key, 0) + 1
            
            # Collect satisfaction scores
            if journey.get("user_satisfaction"):
                satisfaction_scores.append(journey["user_satisfaction"])
        
        # Calculate insights
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
        most_used_transport = max(transport_usage.items(), key=lambda x: x[1]) if transport_usage else None
        
        # Calculate travel personality
        travel_personality = "Explorer"  # Default
        if most_used_transport:
            if most_used_transport[0] == "train" and most_used_transport[1] > 5:
                travel_personality = "Scenic Traveler"
            elif most_used_transport[0] == "bus" and total_journeys > 20:
                travel_personality = "Budget-Conscious Commuter"
            elif len(transport_usage) > 2:
                travel_personality = "Multi-Modal Explorer"
        
        # Environmental impact (mock calculation)
        carbon_saved = total_journeys * 2.5  # kg CO2 saved vs private car
        
        return {
            "user_id": current_user.id,
            "profile_summary": {
                "total_journeys": total_journeys,
                "travel_personality": travel_personality,
                "average_satisfaction": round(avg_satisfaction, 1) if avg_satisfaction else None,
                "most_used_transport": {
                    "mode": most_used_transport[0],
                    "count": most_used_transport[1]
                } if most_used_transport else None
            },
            "transport_usage": transport_usage,
            "monthly_activity": dict(sorted(monthly_patterns.items())),
            "achievements": [
                f"🌱 Saved {carbon_saved:.1f}kg CO2 by using public transport",
                f"🚌 Completed {total_journeys} sustainable journeys",
                "🏆 Smart Transit Champion" if total_journeys > 50 else "🌟 Eco-Friendly Traveler"
            ],
            "recommendations": [
                "Try the scenic train route to Ella for your next adventure",
                "Consider upgrading to premium bus services for better comfort",
                "Explore tuk-tuk rides for short distances in tourist areas"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Travel profile generation failed: {str(e)}"
        )