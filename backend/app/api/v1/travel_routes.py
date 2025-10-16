from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.workflow import run_travel_agent
from app.core.database import db
from app.core.auth_middleware import get_current_active_user, get_optional_user
from bson import ObjectId
import json

router = APIRouter()

# Request Models
class TravelRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    source: str = Field(..., description="Starting location")
    destination: str = Field(..., description="Destination location")
    mode: str = Field(..., description="Travel mode: driving, two_wheeler, transit, uber")
    preferred_transit: Optional[str] = Field(None, description="Preferred transit mode for transit routes")
    departure_time: Optional[datetime] = Field(None, description="Departure time")

class RouteSelectionRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    route_id: str = Field(..., description="Selected route ID")
    source: str = Field(..., description="Source location")
    destination: str = Field(..., description="Destination location")
    mode: str = Field(..., description="Travel mode used")
    selected_route_data: Dict[str, Any] = Field(..., description="Complete route data that was selected")
    selection_reason: Optional[str] = Field(None, description="Reason for selecting this route (e.g., 'fastest', 'cheapest', 'most_comfortable')")
    request_id: Optional[str] = Field(None, description="Original request ID from the route planning")

class DisruptionReportRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    route_id: str = Field(..., description="Affected route ID")
    location: str = Field(..., description="Location of disruption")
    disruption_type: str = Field(..., description="Type of disruption: traffic, construction, weather, accident, etc.")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")
    description: str = Field(..., description="Description of the disruption")
    affected_routes: List[str] = Field(..., description="List of affected route IDs")

# Response Models
class TravelResponse(BaseModel):
    request_id: str
    status: str
    response: Dict[str, Any]
    processing_time: float
    agents_used: List[str]
    trace_id: Optional[str] = None

class UserPreferenceUpdateResponse(BaseModel):
    user_id: str
    status: str
    message: str
    updated_preferences: Dict[str, Any]
    timestamp: datetime

class DisruptionResponse(BaseModel):
    disruption_id: str
    status: str
    message: str
    alternative_routes: List[Dict[str, Any]]
    timestamp: datetime

class SaveRouteRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    route_id: str = Field(..., description="Route ID")
    source: str = Field(..., description="Source location")
    destination: str = Field(..., description="Destination location")
    route_data: Dict[str, Any] = Field(..., description="Complete route data")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class RouteHistoryResponse(BaseModel):
    routes: List[Dict[str, Any]]
    total_count: int
    user_id: str
    timestamp: datetime

class SaveRouteResponse(BaseModel):
    route_id: str
    status: str
    message: str
    timestamp: datetime

@router.post("/plan-route", response_model=TravelResponse)
async def plan_travel_route(
    request: TravelRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Plan a travel route using the multi-agent system.
    
    This endpoint triggers the complete agentic workflow to:
    1. Process user input and preferences
    2. Generate multiple route options
    3. Consider disruptions and local knowledge
    4. Return optimized recommendations
    """
    try:
        print(f"Route handler: Processing request for {request.source} to {request.destination} ({request.mode})")
        
        # Run the travel agent workflow
        result = run_travel_agent(
            source=request.source,
            destination=request.destination,
            mode=request.mode,
            user_id=request.user_id,
            preferred_transit=request.preferred_transit
        )
        
        print(f"Route handler: Workflow result status: {result.get('status')}")
        
        if result.get('status') == 'error':
            print(f"Route handler: Workflow returned error: {result.get('error')}")
        else:
            print(f"Route handler: Workflow completed successfully with {len(result.get('agents_used', []))} agents")
        
        # Store the request in database for tracking
        await db.database.travel_requests.insert_one({
            "user_id": request.user_id,
            "source": request.source,
            "destination": request.destination,
            "mode": request.mode,
            "preferred_transit": request.preferred_transit,
            "departure_time": request.departure_time,
            "request_timestamp": datetime.now(),
            "result": result
        })
        
        # Auto-save successful routes to history
        if result.get('status') == 'success' and result.get('response', {}).get('best_route'):
            try:
                best_route = result['response']['best_route']
                response_data = result.get('response', {})
                
                # Create comprehensive route history document with ALL agent data
                route_document = {
                    "user_id": request.user_id,
                    "route_id": best_route.get('route_id', f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    "source": request.source,
                    "destination": request.destination,
                    "route_data": best_route,
                    "created_at": datetime.utcnow(),
                    "saved_at": datetime.utcnow(),
                    "metadata": {
                        "agent_count": len(result.get('agents_used', [])),
                        "processing_time": result.get('processing_time', 0.0),
                        "auto_saved": True,
                        "mode": request.mode
                    },
                    # FIX: Save AI disruption analysis
                    "ai_disruption_analysis": response_data.get('ai_disruption_analysis'),
                    # FIX: Save destination insights
                    "destination_summary": response_data.get('destination_summary'),
                    # FIX: Save all routes for reference
                    "all_routes": response_data.get('all_routes', []),
                    # FIX: Save total routes found
                    "total_routes_found": response_data.get('total_routes_found', 0),
                    # FIX: Save any active disruptions
                    "active_disruptions": response_data.get('active_disruptions', [])
                }
                
                # Insert into route_history collection
                await db.database.route_history.insert_one(route_document)
                print(f"Route handler: Auto-saved route {best_route.get('route_id')} to history")
                
            except Exception as save_error:
                print(f"Route handler: Failed to auto-save route: {save_error}")
                # Don't fail the main request if auto-save fails
        
        return TravelResponse(
            request_id=result.get("response", {}).get("request_id", "unknown"),
            status=result.get("status", "success"),
            response=result.get("response", {}),
            processing_time=result.get("processing_time", 0.0),
            agents_used=result.get("agents_used", []),
            trace_id=result.get("trace_id")
        )
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.now(),
            "user_id": request.user_id,
            "endpoint": "/plan-route",
            "error": str(e),
            "request_data": request.dict()
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to plan route: {str(e)}"
        )

@router.post("/select-route", response_model=UserPreferenceUpdateResponse)
async def select_route(request: RouteSelectionRequest):
    """
    Handle user route selection and update preferences based on the choice.
    
    This endpoint is triggered when a user selects a route from the multi-agent
    system recommendations, allowing the system to learn from user choices and
    improve future recommendations.
    """
    try:
        # Extract preference indicators from the selected route
        route_data = request.selected_route_data
        
        # Analyze the selected route to understand user preferences
        preference_updates = {
            "last_selected_route": {
                "route_id": request.route_id,
                "timestamp": datetime.now(),
                "route_data": route_data,
                "selection_reason": request.selection_reason
            },
            "mode_preference": {
                "mode": request.mode,
                "frequency": 1,
                "last_used": datetime.now()
            }
        }
        
        # Extract specific preferences from route data
        estimated_cost = route_data.get("estimated_cost", 0)
        duration_text = route_data.get("duration_text", "")
        transit_modes = route_data.get("transit_modes", [])
        transfers = route_data.get("transfers", 0)
        walking_distance = route_data.get("walking_distance", 0)
        
        # Analyze cost preference
        if estimated_cost > 0:
            if estimated_cost < 20:
                preference_updates["budget_preference"] = "low"
            elif estimated_cost < 50:
                preference_updates["budget_preference"] = "medium"
            else:
                preference_updates["budget_preference"] = "high"
        
        # Analyze time preference based on duration
        if "hour" in duration_text.lower():
            # Extract hours from duration text
            import re
            hours_match = re.search(r'(\d+)\s*hour', duration_text)
            if hours_match:
                hours = int(hours_match.group(1))
                if hours < 1:
                    preference_updates["time_preference"] = "fast"
                elif hours < 2:
                    preference_updates["time_preference"] = "balanced"
                else:
                    preference_updates["time_preference"] = "scenic"
        
        # Analyze transit mode preferences
        if transit_modes:
            preference_updates["preferred_transit_modes"] = transit_modes
        
        # Analyze comfort preferences based on transfers and walking
        if transfers == 0 and walking_distance < 0.5:
            preference_updates["comfort_preference"] = 0.9  # High comfort
        elif transfers <= 1 and walking_distance < 1.0:
            preference_updates["comfort_preference"] = 0.7  # Medium comfort
        else:
            preference_updates["comfort_preference"] = 0.5  # Lower comfort
        
        # Analyze walking tolerance
        if walking_distance <= 0.2:
            preference_updates["max_walking_distance"] = 0.5
        elif walking_distance <= 0.5:
            preference_updates["max_walking_distance"] = 1.0
        else:
            preference_updates["max_walking_distance"] = 2.0
        
        # Get existing preferences to merge with updates
        existing_prefs = await db.database.user_preferences.find_one({"user_id": request.user_id})
        
        if existing_prefs:
            # Merge with existing preferences using learning algorithm
            current_prefs = existing_prefs.get("current_preferences", {})
            
            # Update time vs cost weight based on selection reason
            if request.selection_reason:
                if "fast" in request.selection_reason.lower():
                    current_prefs["time_vs_cost_weight"] = min(1.0, current_prefs.get("time_vs_cost_weight", 0.5) + 0.1)
                elif "cheap" in request.selection_reason.lower() or "cost" in request.selection_reason.lower():
                    current_prefs["time_vs_cost_weight"] = max(0.0, current_prefs.get("time_vs_cost_weight", 0.5) - 0.1)
            
            # Merge preference updates
            for key, value in preference_updates.items():
                if key in current_prefs:
                    # For numeric values, use weighted average
                    if isinstance(value, (int, float)) and isinstance(current_prefs[key], (int, float)):
                        current_prefs[key] = (current_prefs[key] * 0.7) + (value * 0.3)
                    else:
                        current_prefs[key] = value
                else:
                    current_prefs[key] = value
            
            preference_updates = current_prefs
        
        # Update or create user preferences in database
        update_result = await db.database.user_preferences.update_one(
            {"user_id": request.user_id},
            {
                "$set": {
                    "last_updated": datetime.now(),
                    "current_preferences": preference_updates
                },
                "$inc": {
                    "route_selection_count": 1
                },
                "$push": {
                    "route_history": {
                        "route_id": request.route_id,
                        "source": request.source,
                        "destination": request.destination,
                        "mode": request.mode,
                        "selected_at": datetime.now(),
                        "route_data": route_data,
                        "selection_reason": request.selection_reason,
                        "request_id": request.request_id
                    }
                }
            },
            upsert=True
        )
        
        # Store the selection for analytics
        await db.database.route_selections.insert_one({
            "user_id": request.user_id,
            "route_id": request.route_id,
            "source": request.source,
            "destination": request.destination,
            "mode": request.mode,
            "selected_at": datetime.now(),
            "selection_reason": request.selection_reason,
            "route_data": route_data,
            "request_id": request.request_id,
            "preference_updates": preference_updates
        })
        
        return UserPreferenceUpdateResponse(
            user_id=request.user_id,
            status="success",
            message="Route selection recorded and preferences updated successfully",
            updated_preferences=preference_updates,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.now(),
            "user_id": request.user_id,
            "endpoint": "/select-route",
            "error": str(e),
            "request_data": request.dict()
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record route selection: {str(e)}"
        )

# Keep the old endpoint for backward compatibility
@router.post("/update-user-preferences", response_model=UserPreferenceUpdateResponse)
async def update_user_preferences(request: RouteSelectionRequest):
    """
    Legacy endpoint - redirects to select-route
    """
    return await select_route(request)

@router.post("/report-disruption", response_model=DisruptionResponse)
async def report_disruption(request: DisruptionReportRequest):
    """
    Report a disruption and get alternative routes.
    
    This endpoint allows users to report disruptions in their selected route
    and receive alternative route suggestions.
    """
    try:
        # Create disruption record
        disruption_id = str(ObjectId())
        disruption_record = {
            "_id": ObjectId(disruption_id),
            "user_id": request.user_id,
            "route_id": request.route_id,
            "location": request.location,
            "disruption_type": request.disruption_type,
            "severity": request.severity,
            "description": request.description,
            "affected_routes": request.affected_routes,
            "reported_at": datetime.now(),
            "status": "active"
        }
        
        # Store disruption in database
        await db.database.disruptions.insert_one(disruption_record)
        
        # Find alternative routes for the affected route
        affected_route = await db.database.travel_requests.find_one(
            {"response.request_id": request.route_id}
        )
        
        alternative_routes = []
        if affected_route:
            # Generate alternative routes using the travel agent
            try:
                alt_result = run_travel_agent(
                    source=affected_route["source"],
                    destination=affected_route["destination"],
                    mode=affected_route["mode"],
                    user_id=request.user_id,
                    preferred_transit=affected_route.get("preferred_transit")
                )
                
                if alt_result.get("status") == "success":
                    # Filter out the affected route and provide alternatives
                    recommended_routes = alt_result.get("response", {}).get("recommended_routes", [])
                    alternative_routes = [
                        route for route in recommended_routes 
                        if route.get("route_id") != request.route_id
                    ][:3]  # Limit to 3 alternatives
                    
            except Exception as e:
                # If alternative route generation fails, provide basic alternatives
                alternative_routes = [
                    {
                        "route_id": f"alt_{disruption_id}_1",
                        "summary": {
                            "duration_minutes": "Unknown",
                            "distance_km": "Unknown",
                            "estimated_fare": None
                        },
                        "disruption_note": "Alternative route generation failed, please try planning a new route"
                    }
                ]
        
        # Update the original route with disruption information
        await db.database.travel_requests.update_one(
            {"response.request_id": request.route_id},
            {
                "$set": {
                    "has_disruption": True,
                    "disruption_info": {
                        "disruption_id": disruption_id,
                        "reported_at": datetime.now(),
                        "status": "active"
                    }
                }
            }
        )
        
        return DisruptionResponse(
            disruption_id=disruption_id,
            status="reported",
            message="Disruption reported successfully",
            alternative_routes=alternative_routes,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.now(),
            "user_id": request.user_id,
            "endpoint": "/report-disruption",
            "error": str(e),
            "request_data": request.dict()
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to report disruption: {str(e)}"
        )

@router.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """
    Get current user preferences and route history.
    """
    try:
        user_prefs = await db.database.user_preferences.find_one({"user_id": user_id})
        
        if not user_prefs:
            return {
                "user_id": user_id,
                "message": "No preferences found for this user",
                "preferences": {},
                "route_history": []
            }
        
        return {
            "user_id": user_id,
            "preferences": user_prefs.get("current_preferences", {}),
            "route_history": user_prefs.get("route_history", []),
            "last_updated": user_prefs.get("last_updated"),
            "route_selection_count": user_prefs.get("route_selection_count", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user preferences: {str(e)}"
        )

@router.get("/active-disruptions")
async def get_active_disruptions():
    """
    Get all currently active disruptions.
    """
    try:
        disruptions = await db.database.transit_disruptions.find(
            {"is_resolved": False}
        ).sort("reported_at", -1).limit(50).to_list(length=50)
        
        return {
            "active_disruptions_count": len(disruptions),
            "disruptions": [
                {
                    "disruption_id": d.get("disruption_id", str(d["_id"])),
                    "route_id": d.get("route_id"),
                    "disruption_type": d.get("disruption_type"),
                    "severity": d.get("severity"),
                    "description": d.get("description"),
                    "affected_stops": d.get("affected_stops", []),
                    "estimated_duration": d.get("estimated_duration"),
                    "alternative_routes": d.get("alternative_routes", []),
                    "reported_by": d.get("reported_by"),
                    "reported_at": d.get("reported_at"),
                    "is_resolved": d.get("is_resolved", False),
                    "location": d.get("location", {})
                }
                for d in disruptions
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active disruptions: {str(e)}"
        )

@router.post("/test-search")
async def test_search_functionality():
    """
    Test the search functionality to ensure Serper API is working correctly.
    This endpoint helps debug search-related issues.
    """
    try:
        from app.services.agent_nodes import serper_tool
        
        # Test search queries
        test_queries = [
            "transportation Colombo to Kandy local tips routes",
            "attractions points of interest landmarks between Colombo Kandy",
            "current traffic conditions roadworks Colombo Kandy today"
        ]
        
        search_results = {}
        for query in test_queries:
            try:
                result = serper_tool._run(query)
                search_results[query] = result
            except Exception as e:
                search_results[query] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "message": "Search functionality test completed",
            "test_queries": test_queries,
            "results": search_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test search functionality: {str(e)}"
        )

@router.post("/test-llm-summarizer")
async def test_llm_summarizer():
    """
    Test the LLM summarizer service to ensure it's working correctly.
    This endpoint helps debug LLM-related issues.
    """
    try:
        from app.services.llm_summarizer import LLMSummarizerService
        
        # Initialize the service
        summarizer = LLMSummarizerService()
        
        # Test with sample data
        test_search_results = {
            "general_info": {
                "summary": "Multiple transportation options available from Colombo to Kandy",
                "key_points": [
                    "Express buses take 3-4 hours and cost 200-300 LKR",
                    "Regular buses take 5-6 hours and cost 150-200 LKR",
                    "Trains available but limited schedule",
                    "Private taxis cost 8000-12000 LKR"
                ],
                "relevant_links": [
                    "https://example.com/bus-routes",
                    "https://example.com/train-schedule"
                ]
            },
            "raw_results": "Additional search data about local conditions and attractions"
        }
        
        # Test summarization
        summary_result = summarizer.summarize_search_results(
            test_search_results,
            "How do I get from Colombo to Kandy?",
            "User is in Colombo and needs to reach Kandy by evening"
        )
        
        # Test destination insights
        test_preferences = {
            "preferred_transit_modes": ["bus", "train"],
            "budget_preference": "medium",
            "max_walking_distance": 1.0
        }
        
        test_context = {
            "summary": "Traveling to Kandy from Colombo"
        }
        
        insights = summarizer.generate_route_recommendation(
            [],  # Empty routes list for destination focus
            test_preferences,
            test_context
        )
        
        return {
            "status": "success",
            "message": "LLM Summarizer test completed successfully",
            "test_results": {
                "summarization": summary_result,
                "destination_insights": insights
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.now(),
            "user_id": "test_user",
            "endpoint": "/test-llm-summarizer",
            "error": str(e),
            "request_data": {"test": "llm_summarizer"}
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test LLM summarizer: {str(e)}"
        )

@router.post("/search-route-info")
async def search_route_information(request: TravelRequest):
    """
    Search for comprehensive information about a route using the Serper API.
    This endpoint provides detailed search results for planning purposes.
    """
    try:
        from app.services.agent_nodes import serper_tool
        
        # Generate comprehensive search queries
        search_queries = [
            {
                "query": f"transportation {request.source} to {request.destination} local tips routes",
                "category": "route_info",
                "description": "General route and transportation information"
            },
            {
                "query": f"attractions points of interest landmarks between {request.source} {request.destination}",
                "category": "poi_info",
                "description": "Points of interest along the route"
            },
            {
                "query": f"current traffic conditions roadworks {request.source} {request.destination} today",
                "category": "traffic_info",
                "description": "Current traffic and road conditions"
            },
            {
                "query": f"weather conditions {request.source} {request.destination} current",
                "category": "weather_info",
                "description": "Current weather conditions"
            },
            {
                "query": f"local events festivals {request.source} {request.destination} today this week",
                "category": "events_info",
                "description": "Local events and activities"
            },
            {
                "query": f"public transport bus train schedule {request.source} {request.destination}",
                "category": "transit_info",
                "description": "Public transport information"
            }
        ]
        
        # Execute all searches
        search_results = {}
        for search_item in search_queries:
            try:
                result = serper_tool._run(search_item["query"])
                search_results[search_item["category"]] = {
                    "query": search_item["query"],
                    "description": search_item["description"],
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                search_results[search_item["category"]] = {
                    "query": search_item["query"],
                    "description": search_item["description"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Store search results in database for tracking
        await db.database.search_requests.insert_one({
            "user_id": request.user_id,
            "source": request.source,
            "destination": request.destination,
            "mode": request.mode,
            "search_results": search_results,
            "request_timestamp": datetime.now()
        })
        
        return {
            "status": "success",
            "message": "Route information search completed",
            "request_id": f"search_{datetime.now().timestamp()}",
            "query": {
                "source": request.source,
                "destination": request.destination,
                "mode": request.mode,
                "user_id": request.user_id
            },
            "search_results": search_results,
            "summary": {
                "total_searches": len(search_queries),
                "successful_searches": len([r for r in search_results.values() if "result" in r]),
                "failed_searches": len([r for r in search_results.values() if "error" in r]),
                "search_categories": list(search_results.keys())
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.now(),
            "user_id": request.user_id,
            "endpoint": "/search-route-info",
            "error": str(e),
            "request_data": request.dict()
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search route information: {str(e)}"
        )

@router.post("/save-route", response_model=SaveRouteResponse)
async def save_route_to_history(
    request: SaveRouteRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Save a route to user's route history for future reference.
    """
    try:
        # Create route history document
        route_document = {
            "user_id": request.user_id,
            "route_id": request.route_id,
            "source": request.source,
            "destination": request.destination,
            "route_data": request.route_data,
            "created_at": request.created_at,
            "metadata": request.metadata,
            "saved_at": datetime.utcnow()
        }
        
        # Insert into route_history collection
        result = await db.database.route_history.insert_one(route_document)
        
        # Also update user's route history in user_preferences
        await db.database.user_preferences.update_one(
            {"user_id": request.user_id},
            {
                "$push": {
                    "route_history": {
                        "$each": [route_document],
                        "$slice": -50  # Keep only last 50 routes
                    }
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return SaveRouteResponse(
            route_id=request.route_id,
            status="success",
            message="Route saved to history successfully",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "user_id": request.user_id,
            "endpoint": "/save-route",
            "error": str(e),
            "request_data": request.dict()
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save route: {str(e)}"
        )

@router.get("/requests")
async def get_travel_requests(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get user's travel requests from the database (with full agent-generated data).
    """
    try:
        # Query travel_requests collection (contains complete agent results)
        cursor = db.database.travel_requests.find(
            {"user_id": user_id}
        ).sort("request_timestamp", -1).skip(offset).limit(limit)
        
        requests = await cursor.to_list(length=limit)
        total_count = await db.database.travel_requests.count_documents({"user_id": user_id})
        
        # Convert ObjectId to string for JSON serialization
        for request in requests:
            if "_id" in request:
                request["_id"] = str(request["_id"])
        
        return {
            "requests": requests,
            "total_count": total_count,
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(requests) < total_count,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "endpoint": "/requests",
            "error": str(e)
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get travel requests: {str(e)}"
        )

@router.get("/route-history", response_model=RouteHistoryResponse)
async def get_route_history(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get user's route history from the database (saved routes only).
    """
    try:
        # Query route history collection
        cursor = db.database.route_history.find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(offset).limit(limit)
        
        routes = await cursor.to_list(length=limit)
        total_count = await db.database.route_history.count_documents({"user_id": user_id})
        
        # Convert ObjectId to string for JSON serialization
        for route in routes:
            if "_id" in route:
                route["_id"] = str(route["_id"])
        
        return RouteHistoryResponse(
            routes=routes,
            total_count=total_count,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "endpoint": "/route-history",
            "error": str(e)
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get route history: {str(e)}"
        )

@router.delete("/delete-route/{route_id}")
async def delete_route_from_history(
    route_id: str,
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a specific route from user's history.
    """
    try:
        # Delete from route_history collection
        delete_result = await db.database.route_history.delete_one({
            "route_id": route_id,
            "user_id": user_id
        })
        
        # Also remove from user_preferences.route_history
        await db.database.user_preferences.update_one(
            {"user_id": user_id},
            {
                "$pull": {
                    "route_history": {"route_id": route_id}
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if delete_result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Route not found in history"
            )
        
        return {
            "status": "success",
            "message": "Route deleted from history successfully",
            "route_id": route_id,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        await db.database.error_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "endpoint": f"/delete-route/{route_id}",
            "error": str(e)
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete route: {str(e)}"
        )
