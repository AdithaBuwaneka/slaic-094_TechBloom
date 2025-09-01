from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.models.transport import JourneyRequest, RouteOption, UserProfile, Disruption, CommunityUpdate, TransportMode
from app.services.google_maps_service1 import GoogleMapsService
from app.agents.graph import agentic_graph
from app.agents.disruption_agent import DisruptionManagementAgent
from app.agents.personalization_agent import PersonalizationAgent
from app.agents.language_accessibility_agent import LanguageAccessibilityAgent
from app.agents.fare_optimization_agent import FareOptimizationAgent
from app.agents.local_knowledge_agent import LocalKnowledgeAgent

# Initialize agent instances
disruption_agent = DisruptionManagementAgent()
personalization_agent = PersonalizationAgent()
language_agent = LanguageAccessibilityAgent()
fare_agent = FareOptimizationAgent()
local_knowledge_agent = LocalKnowledgeAgent()
from app.core.database import db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
gmaps_service = GoogleMapsService()

@router.post("/plan-journey/direct", response_model=List[RouteOption])
def get_direct_journey(request: JourneyRequest):
    if not request.origin or not request.destination:
        raise HTTPException(status_code=400, detail="Origin and destination cannot be empty.")
    routes = gmaps_service.get_directions(request.origin, request.destination, request.mode)
    if not routes:
        raise HTTPException(status_code=404, detail="Could not find a route for the given locations in Sri Lanka.")
    return routes


class AgenticJourneyRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    language_preference: Optional[str] = "en"
    accessibility_needs: Optional[List[str]] = []
    budget_preference: Optional[float] = None
    passenger_type: Optional[str] = "adult"

@router.post("/plan-journey/agentic", response_model=Dict[str, Any])
async def get_agentic_journey(request: AgenticJourneyRequest):
    """
    Comprehensive AI-powered journey planning with all specialized agents.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    # Enhanced input with user preferences
    inputs = {
        "user_query": request.query,
        "user_id": request.user_id,
        "language_preference": request.language_preference,
        "accessibility_needs": request.accessibility_needs,
        "budget_preference": request.budget_preference,
        "passenger_type": request.passenger_type
    }

    # Run the comprehensive multi-agent graph
    final_state = await agentic_graph.ainvoke(inputs)
    
    return final_state

# =================== DISRUPTION MANAGEMENT ENDPOINTS ===================

class DisruptionCheckRequest(BaseModel):
    origin: str
    destination: str
    transport_mode: Optional[str] = "any"

@router.post("/disruptions/check", response_model=Dict[str, Any])
async def check_disruptions(request: DisruptionCheckRequest):
    """Check for current disruptions affecting a journey."""
    try:
        analysis = await disruption_agent.check_disruptions(
            origin=request.origin,
            destination=request.destination,
            transport_mode=request.transport_mode
        )
        return analysis.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking disruptions: {str(e)}")

@router.get("/disruptions/active", response_model=List[Dict[str, Any]])
async def get_active_disruptions():
    """Get all currently active disruptions."""
    try:
        current_time = datetime.utcnow()
        disruptions_cursor = db.disruptions_collection.find({
            "start_time": {"$lte": current_time},
            "$or": [
                {"end_time": {"$gte": current_time}},
                {"end_time": None}
            ]
        })
        
        disruptions = await disruptions_cursor.to_list(length=50)
        return [
            {
                "id": str(disruption["_id"]),
                "title": disruption.get("title", ""),
                "description": disruption.get("description", ""),
                "severity": disruption.get("severity", "medium"),
                "transport_mode": disruption.get("transport_mode", ""),
                "affected_stops": disruption.get("affected_stops", [])
            }
            for disruption in disruptions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving disruptions: {str(e)}")

# =================== USER PROFILE MANAGEMENT ENDPOINTS ===================

@router.post("/users/profile", response_model=Dict[str, str])
async def create_or_update_user_profile(profile: UserProfile):
    """Create or update user profile."""
    try:
        existing_profile = await db.user_profiles_collection.find_one({"user_id": profile.user_id})
        
        if existing_profile:
            # Update existing profile
            result = await db.user_profiles_collection.update_one(
                {"user_id": profile.user_id},
                {"$set": profile.dict(exclude={"id"})}
            )
            return {"message": "Profile updated successfully", "user_id": profile.user_id}
        else:
            # Create new profile
            result = await db.user_profiles_collection.insert_one(profile.dict(exclude={"id"}))
            return {"message": "Profile created successfully", "user_id": profile.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing user profile: {str(e)}")

@router.get("/users/profile/{user_id}", response_model=Dict[str, Any])
async def get_user_profile(user_id: str):
    """Get user profile by ID."""
    try:
        profile = await db.user_profiles_collection.find_one({"user_id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Convert ObjectId to string for JSON serialization
        profile["_id"] = str(profile["_id"])
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user profile: {str(e)}")

# =================== PERSONALIZATION ENDPOINTS ===================

class PersonalizedRecommendationRequest(BaseModel):
    user_id: str
    origin: str
    destination: str
    travel_time: Optional[str] = None

@router.post("/personalization/recommendations", response_model=Dict[str, Any])
async def get_personalized_recommendations(request: PersonalizedRecommendationRequest):
    """Get personalized route recommendations."""
    try:
        # Get available routes first
        routes = gmaps_service.get_directions(request.origin, request.destination)
        routes_data = [
            {
                "summary": route.summary,
                "duration": route.total_duration,
                "distance": route.total_distance,
                "legs": len(route.legs)
            }
            for route in routes
        ]
        
        recommendations = await personalization_agent.get_personalized_recommendations(
            user_id=request.user_id,
            origin=request.origin,
            destination=request.destination,
            available_routes=routes_data,
            travel_time=request.travel_time
        )
        
        return recommendations.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating personalized recommendations: {str(e)}")

# =================== FARE OPTIMIZATION ENDPOINTS ===================

class FareOptimizationRequest(BaseModel):
    origin: str
    destination: str
    passenger_type: Optional[str] = "adult"
    budget_preference: Optional[float] = None
    travel_frequency: Optional[str] = "occasional"

@router.post("/fare/optimize", response_model=Dict[str, Any])
async def optimize_fare(request: FareOptimizationRequest):
    """Get fare optimization recommendations."""
    try:
        # Get available routes
        routes = gmaps_service.get_directions(request.origin, request.destination)
        routes_data = [
            {
                "transport_mode": "mixed",
                "distance": route.total_distance,
                "duration": route.total_duration,
                "summary": route.summary
            }
            for route in routes
        ]
        
        optimization = await fare_agent.optimize_fare(
            origin=request.origin,
            destination=request.destination,
            available_routes=routes_data,
            passenger_type=request.passenger_type,
            budget_preference=request.budget_preference,
            travel_frequency=request.travel_frequency
        )
        
        return optimization.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing fare: {str(e)}")

@router.get("/fare/passes/{user_id}", response_model=List[Dict[str, Any]])
async def get_travel_passes(user_id: str):
    """Get recommended travel passes for a user."""
    try:
        user_profile = await personalization_agent.get_user_profile(user_id)
        passes = await fare_agent.get_travel_passes(user_profile or {})
        return passes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving travel passes: {str(e)}")

@router.get("/fare/promotions", response_model=List[Dict[str, Any]])
async def get_current_promotions():
    """Get current promotional offers."""
    try:
        offers = await fare_agent.check_promotional_offers()
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving promotions: {str(e)}")

# =================== LANGUAGE & ACCESSIBILITY ENDPOINTS ===================

class TranslationRequest(BaseModel):
    content: str
    preferred_language: Optional[str] = "en"
    accessibility_needs: Optional[List[str]] = []
    user_type: Optional[str] = "local"

@router.post("/language/translate", response_model=Dict[str, Any])
async def translate_content(request: TranslationRequest):
    """Translate and adapt content for accessibility."""
    try:
        response = await language_agent.translate_response(
            content=request.content,
            preferred_language=request.preferred_language,
            accessibility_needs=request.accessibility_needs,
            user_type=request.user_type
        )
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating content: {str(e)}")

@router.get("/language/emergency-phrases", response_model=Dict[str, str])
async def get_emergency_phrases(language: str = Query("en", description="Language code (en, si, ta)")):
    """Get emergency phrases in specified language."""
    try:
        phrases = await language_agent.generate_emergency_phrases(language)
        return phrases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emergency phrases: {str(e)}")

@router.get("/language/supported", response_model=Dict[str, str])
async def get_supported_languages():
    """Get list of supported languages."""
    return language_agent.get_supported_languages()

# =================== LOCAL KNOWLEDGE ENDPOINTS ===================

class LocalInsightsRequest(BaseModel):
    origin: str
    destination: str
    transport_mode: Optional[str] = "any"
    travel_time: Optional[str] = None

@router.post("/local/insights", response_model=Dict[str, Any])
async def get_local_insights(request: LocalInsightsRequest):
    """Get local knowledge and community insights."""
    try:
        insights = await local_knowledge_agent.get_local_insights(
            origin=request.origin,
            destination=request.destination,
            transport_mode=request.transport_mode,
            travel_time=request.travel_time
        )
        return insights.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving local insights: {str(e)}")

class CommunityUpdateRequest(BaseModel):
    user_id: str
    route_id: str
    transport_mode: TransportMode
    update_type: str
    message: str

@router.post("/local/community-update", response_model=Dict[str, str])
async def add_community_update(request: CommunityUpdateRequest):
    """Add a community-contributed update."""
    try:
        success = await local_knowledge_agent.add_community_update(
            user_id=request.user_id,
            route_id=request.route_id,
            transport_mode=request.transport_mode,
            update_type=request.update_type,
            message=request.message
        )
        
        if success:
            return {"message": "Community update added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add community update")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding community update: {str(e)}")

@router.get("/local/landmarks", response_model=List[Dict[str, str]])
async def get_local_landmarks(
    origin: str = Query(..., description="Origin location"),
    destination: str = Query(..., description="Destination location")
):
    """Get local landmarks for navigation."""
    try:
        landmarks = await local_knowledge_agent.get_local_landmarks(origin, destination)
        return landmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving landmarks: {str(e)}")

# =================== COMPREHENSIVE SEARCH ENDPOINT ===================

class ComprehensiveSearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    language_preference: Optional[str] = "en"
    accessibility_needs: Optional[List[str]] = []
    budget_preference: Optional[float] = None
    passenger_type: Optional[str] = "adult"
    include_disruptions: Optional[bool] = True
    include_local_insights: Optional[bool] = True
    include_fare_optimization: Optional[bool] = True

@router.post("/search/comprehensive", response_model=Dict[str, Any])
async def comprehensive_search(request: ComprehensiveSearchRequest):
    """
    Comprehensive search that runs through all agents for complete results.
    This is the flagship endpoint that demonstrates the full Smart Transit Companion capabilities.
    """
    try:
        # Enhanced input for the complete multi-agent pipeline
        inputs = {
            "user_query": request.query,
            "user_id": request.user_id,
            "origin": request.origin,
            "destination": request.destination,
            "language_preference": request.language_preference,
            "accessibility_needs": request.accessibility_needs,
            "budget_preference": request.budget_preference,
            "passenger_type": request.passenger_type
        }

        # Run through the complete multi-agent system
        final_state = await agentic_graph.ainvoke(inputs)
        
        # Structure the response for comprehensive information
        response = {
            "query": request.query,
            "route_options": final_state.get("direct_route_options", []),
            "final_answer": final_state.get("final_response", ""),
            "enhanced_response": final_state.get("enhanced_response", {}),
        }
        
        # Add optional insights based on request
        if request.include_disruptions and final_state.get("disruption_analysis"):
            response["disruption_analysis"] = final_state["disruption_analysis"]
            
        if request.include_local_insights and final_state.get("local_insights"):
            response["local_insights"] = final_state["local_insights"]
            
        if request.include_fare_optimization and final_state.get("fare_optimization"):
            response["fare_optimization"] = final_state["fare_optimization"]
            
        # Always include personalization if user_id provided
        if request.user_id and final_state.get("personalized_recommendations"):
            response["personalized_recommendations"] = final_state["personalized_recommendations"]
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comprehensive search: {str(e)}")