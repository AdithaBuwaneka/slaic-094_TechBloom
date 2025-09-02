from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.models.travel_schema import TravelState
from app.services.tool_functions import *
from app.services.analysis_tools import *
from app.services.llm_summarizer import LLMSummarizerService
from app.services.langfuse_service import langfuse_service
import json
from datetime import datetime, timedelta

# Initialize tools
google_maps_tool = GoogleMapsAPITool()
serper_tool = SerperWebSearchTool()
fare_tool = FareDatabaseTool()
preference_tool = UserPreferenceTool()
disruption_tool = DisruptionDatabaseTool()
route_comparison_tool = RouteComparisonTool()
last_mile_tool = LastMileOptimizerTool()
preference_learning_tool = PreferenceLearningTool()

# Initialize LLM summarizer service
try:
    llm_summarizer = LLMSummarizerService()
    print("✅ LLM Summarizer Service initialized successfully")
except Exception as e:
    print(f"⚠️  LLM Summarizer Service initialization failed: {str(e)}")
    llm_summarizer = None

def input_processing_node(state: TravelState) -> TravelState:
    """
    Process and validate user input, initialize preferences
    """
    print(f"Processing input for {state.mode} travel from {state.source} to {state.destination}")
    
    # Start Langfuse span for this agent action
    with langfuse_service.start_span(
        name="input_processing_agent",
        metadata={
            "agent_type": "input_processing",
            "source": state.source,
            "destination": state.destination,
            "mode": state.mode,
            "user_id": state.user_id
        }
    ) as span:
        try:
            # Get user preferences
            pref_result = preference_tool.get_preferences(state.user_id)
            if pref_result["status"] == "success":
                state.current_user_preferences = pref_result["preferences"]
                span.update(
                    input={"user_id": state.user_id},
                    output={"preferences_loaded": True, "preferences": pref_result["preferences"]}
                )
            else:
                span.update(
                    input={"user_id": state.user_id},
                    output={"preferences_loaded": False, "error": pref_result.get("error")}
                )
            
            # Set processing step
            state.current_step = "input_processed"
            state.agents_completed.append("input_processing")
            
            span.update(status="completed")
            return state
            
        except Exception as e:
            span.update(
                status="error",
                error=str(e)
            )
            state.errors.append({
                "node": "input_processing",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return state

def mode_router_node(state: TravelState) -> TravelState:
    """
    Route to appropriate processing based on travel mode
    """
    print(f"Routing for mode: {state.mode}")
    
    state.current_step = f"routing_{state.mode}"
    state.agents_completed.append("mode_router")
    
    return state

def standard_route_node(state: TravelState) -> TravelState:
    """
    Handle standard routing (driving, two_wheeler, uber)
    """
    print(f"Getting standard routes for {state.mode}")
    
    # Start Langfuse span for this agent action
    with langfuse_service.start_span(
        name="standard_route_agent",
        metadata={
            "agent_type": "standard_route",
            "source": state.source,
            "destination": state.destination,
            "mode": state.mode,
            "user_id": state.user_id
        }
    ) as span:
        try:
            # Get routes from Google Maps
            route_result = google_maps_tool._run(
                origin=state.source,
                destination=state.destination,
                mode=state.mode if state.mode != "uber" else "driving",
                alternatives=True,
                departure_time=state.departure_time
            )
            
            print(f"Google Maps API result: {route_result['status']}")
            
            span.update(
                input={
                    "origin": state.source,
                    "destination": state.destination,
                    "mode": state.mode,
                    "departure_time": state.departure_time.isoformat() if state.departure_time else None
                },
                output={"google_maps_result": route_result}
            )
            
            if route_result["status"] == "success":
                routes = route_result["routes"]
                print(f"Number of routes returned: {len(routes) if routes else 0}")
                
                # Process primary route
                if routes:
                    primary_route = routes[0]
                    print(f"Processing primary route: {primary_route.get('summary', 'No summary')}")
                    
                    state.primary_routes.append({
                        "route_id": f"primary_{state.mode}",
                        "duration": primary_route["legs"][0]["duration"]["value"] // 60,
                        "distance": primary_route["legs"][0]["distance"]["value"] / 1000,
                        "steps": primary_route["legs"][0]["steps"],
                        "polyline": primary_route["overview_polyline"]["points"],
                        "fare_estimate": None,
                        "transit_modes": [],
                        "transfers": 0,
                        "walking_distance": 0.0,
                        "category": "standard",
                        "mode_details": {"mode": state.mode}
                    })
                    
                    print(f"Added primary route: {state.primary_routes[-1]['route_id']}")
                    
                    # Process supplementary routes
                    for i, route in enumerate(routes[1:], 1):
                        state.supplementary_routes.append({
                            "route_id": f"alt_{state.mode}_{i}",
                            "duration": route["legs"][0]["duration"]["value"] // 60,
                            "distance": route["legs"][0]["distance"]["value"] / 1000,
                            "steps": route["legs"][0]["steps"],
                            "polyline": route["overview_polyline"]["points"],
                            "fare_estimate": None,
                            "transit_modes": [],
                            "transfers": 0,
                            "walking_distance": 0.0,
                            "category": "alternative",
                            "mode_details": {"mode": state.mode}
                        })
                else:
                    print("No routes returned from Google Maps API")
            else:
                print(f"Google Maps API failed: {route_result.get('error', 'Unknown error')}")
            
            print(f"Total routes in state: {len(state.primary_routes) + len(state.supplementary_routes)}")
            
            state.current_step = "standard_routes_completed"
            state.agents_completed.append("standard_route")
            
            span.update(
                status="completed",
                output={
                    "routes_found": len(state.primary_routes) + len(state.supplementary_routes),
                    "primary_routes": len(state.primary_routes),
                    "supplementary_routes": len(state.supplementary_routes)
                }
            )
            
        except Exception as e:
            print(f"Error in standard_route_node: {str(e)}")
            span.update(
                status="error",
                error=str(e)
            )
            state.errors.append({
                "node": "standard_route",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        return state

def transit_route_aggregation_node(state: TravelState) -> TravelState:
    """
    Aggregate transit routes from Google Maps API
    """
    print("Aggregating transit routes")
    
    try:
        # Get transit routes
        route_result = google_maps_tool._run(
            origin=state.source,
            destination=state.destination,
            mode="transit",
            alternatives=True,
            departure_time=state.departure_time,
            transit_mode_preference=state.preferred_transit
        )
        
        if route_result["status"] == "success":
            routes = route_result["routes"]
            
            for i, route in enumerate(routes):
                transit_modes = []
                transfers = 0
                walking_distance = 0
                
                # Analyze route steps
                for step in route["legs"][0]["steps"]:
                    if step["travel_mode"] == "TRANSIT":
                        transit_detail = step.get("transit_details", {})
                        line = transit_detail.get("line", {})
                        vehicle_type = line.get("vehicle", {}).get("type", "").lower()
                        if vehicle_type not in transit_modes:
                            transit_modes.append(vehicle_type)
                        if len(transit_modes) > 1:
                            transfers += 1
                    elif step["travel_mode"] == "WALKING":
                        walking_distance += step["distance"]["value"] / 1000
                
                state.transit_routes.append({
                    "route_id": f"transit_{i}",
                    "duration": route["legs"][0]["duration"]["value"] // 60,
                    "distance": route["legs"][0]["distance"]["value"] / 1000,
                    "steps": route["legs"][0]["steps"],
                    "polyline": route["overview_polyline"]["points"],
                    "fare_estimate": None,
                    "transit_modes": transit_modes,
                    "transfers": max(0, transfers - 1),
                    "walking_distance": walking_distance,
                    "category": "transit",
                    "mode_details": {
                        "modes": transit_modes,
                        "transfers": transfers,
                        "walking_km": walking_distance
                    }
                })
        
        state.current_step = "transit_aggregation_completed"
        state.agents_completed.append("transit_route_aggregation")
        
    except Exception as e:
        state.errors.append({
            "node": "transit_route_aggregation",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def fare_calculation_node(state: TravelState) -> TravelState:
    """
    Calculate fares for transit routes and last mile options
    """
    print("Calculating fares for transit routes")
    
    try:
        total_estimated_fare = 0
        
        for route in state.transit_routes:
            route_fare = 0
            step_fares = []
            
            # Process each step in the route
            for step in route.get("steps", []):
                if step.get("travel_mode") == "TRANSIT":
                    # Calculate fare for this transit step
                    step_fare_result = fare_tool.get_step_fare(step)
                    
                    if step_fare_result["status"] == "success":
                        step_fare = step_fare_result["fare"]
                        step_fares.append(step_fare)
                        route_fare += step_fare["base_fare"]
                        
                        # Add fare details to the step
                        step["fare_details"] = step_fare
                        
                        print(f"🚌 Step fare: {step_fare['base_fare']} LKR ({step_fare['source']})")
                    else:
                        print(f"❌ Failed to calculate fare for step: {step_fare_result.get('error', 'Unknown error')}")
                else:
                    # Walking step - check if we should offer Uber alternative
                    walking_distance_km = step.get("distance", {}).get("value", 0) / 1000
                    
                    # Check if user prefers time over cost and walking distance > 0.5km
                    user_prefs = state.current_user_preferences
                    time_preference = user_prefs.get("time_vs_cost_weight", 0.5) if user_prefs else 0.5
                    prefers_time_over_cost = time_preference > 0.5
                    
                    if walking_distance_km > 0.5 and prefers_time_over_cost:
                        # Calculate Uber alternative
                        uber_duration = max(5, walking_distance_km * 3)  # 3 min per km + 5 min wait
                        uber_cost = max(50, walking_distance_km * 25)  # Minimum 50 LKR or 25 LKR per km
                        
                        # Add Uber alternative to the step
                        step["fare_details"] = {
                            "base_fare": 0,
                            "vehicle_type": "walking",
                            "source": "free",
                            "uber_alternative": {
                                "available": True,
                                "duration_minutes": int(uber_duration),
                                "cost_lkr": int(uber_cost),
                                "distance_km": round(walking_distance_km, 2),
                                "reason": "Long walking distance with time preference"
                            }
                        }
                        
                        print(f"🚶 Walking step: {walking_distance_km:.2f}km - Uber alternative: {int(uber_duration)}min, {int(uber_cost)} LKR")
                    else:
                        # Regular walking step - no fare
                        step["fare_details"] = {
                            "base_fare": 0,
                            "vehicle_type": "walking",
                            "source": "free"
                        }
            
            # Add transfer penalty if there are multiple transit steps
            transit_steps = [s for s in route.get("steps", []) if s.get("travel_mode") == "TRANSIT"]
            if len(transit_steps) > 1:
                transfer_penalty = (len(transit_steps) - 1) * 5  # 5 LKR per transfer
                route_fare += transfer_penalty
                print(f"🔄 Added transfer penalty: {transfer_penalty} LKR for {len(transit_steps) - 1} transfers")
            
            # Check if last mile is needed
            route_end_distance = route.get("walking_distance", 0)
            if route_end_distance > 0.2:  # If more than 200m walking needed
                # Calculate last mile options
                last_mile_result = last_mile_tool._run(
                    route, state.destination, state.current_user_preferences
                )
                if last_mile_result["status"] == "success":
                    best_last_mile = last_mile_result["recommendation"]
                    if best_last_mile:
                        route_fare += best_last_mile["cost"]
                        state.last_mile_options.append({
                            "route_id": route["route_id"],
                            "option": best_last_mile
                        })
                        print(f"🚶 Added last mile cost: {best_last_mile['cost']} LKR")
            
            # Store the calculated fare and step details
            route["fare_estimate"] = round(route_fare, 2)
            route["step_fares"] = step_fares
            total_estimated_fare = max(total_estimated_fare, route_fare)
            
            print(f"💰 Total fare for route {route.get('route_id')}: {route_fare:.0f} LKR (from {len(step_fares)} transit steps)")
        
        # Also calculate fares for standard routes if they exist
        for route in state.primary_routes + state.supplementary_routes:
            if route.get("mode_details", {}).get("mode") in ["driving", "two_wheeler"]:
                distance = route.get("distance", 0)
                # Fuel cost estimation: 2 LKR per km for driving, 1 LKR per km for two-wheeler
                fuel_cost_per_km = 2 if route.get("mode_details", {}).get("mode") == "driving" else 1
                fuel_cost = distance * fuel_cost_per_km
                
                # Add parking cost (assume 50 LKR for destination parking)
                parking_cost = 50
                
                total_cost = fuel_cost + parking_cost
                route["fare_estimate"] = round(total_cost, 2)
                print(f"⛽ Calculated cost for {route.get('mode_details', {}).get('mode')}: {total_cost:.0f} LKR (fuel: {fuel_cost:.0f}, parking: {parking_cost})")
        
        state.total_fare_estimate = round(total_estimated_fare, 2)
        state.current_step = "fare_calculation_completed"
        state.agents_completed.append("fare_calculation")
        
        print(f"💳 Total estimated fare across all routes: {state.total_fare_estimate} LKR")
        
    except Exception as e:
        print(f"❌ Error in fare_calculation_node: {str(e)}")
        state.errors.append({
            "node": "fare_calculation",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def user_preference_analysis_node(state: TravelState) -> TravelState:
    """
    Analyze user preferences and apply them to route selection
    """
    print("Analyzing user preferences")
    
    try:
        if not state.current_user_preferences:
            return state
        
        # Calculate preference weight factors based on user history
        preferences = state.current_user_preferences
        
        # Set weight factors based on user preferences
        state.preference_weight_factors = {
            "time_priority": preferences.get("time_vs_cost_weight", 0.5),
            "cost_priority": 1 - preferences.get("time_vs_cost_weight", 0.5),
            "comfort_priority": preferences.get("comfort_preference", 0.7),
            "walking_tolerance": preferences.get("max_walking_distance", 1.0),
            "preferred_modes": preferences.get("preferred_transit_modes", ["bus", "train"])
        }
        
        # Filter routes based on strict preferences
        if state.transit_routes:
            filtered_routes = []
            for route in state.transit_routes:
                # Check walking distance tolerance
                if route.get("walking_distance", 0) <= state.preference_weight_factors["walking_tolerance"]:
                    # Check if route uses preferred modes
                    route_modes = route.get("transit_modes", [])
                    if any(mode in state.preference_weight_factors["preferred_modes"] for mode in route_modes):
                        filtered_routes.append(route)
                    elif not state.preference_weight_factors["preferred_modes"]:  # No strict preference
                        filtered_routes.append(route)
            
            # If filtering removes all routes, use original list with warning
            if filtered_routes:
                state.transit_routes = filtered_routes
            else:
                state.errors.append({
                    "node": "user_preference_analysis",
                    "error": "No routes match user preferences, showing all options",
                    "timestamp": datetime.now().isoformat()
                })
        
        state.current_step = "preference_analysis_completed"
        state.agents_completed.append("user_preference_analysis")
        
    except Exception as e:
        state.errors.append({
            "node": "user_preference_analysis",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def local_knowledge_agent_node(state: TravelState) -> TravelState:
    """
    Gather local knowledge about the route using web search
    """
    print("Gathering local knowledge about the route")
    
    # Start Langfuse span for this agent action
    with langfuse_service.start_span(
        name="local_knowledge_agent",
        metadata={
            "agent_type": "local_knowledge",
            "source": state.source,
            "destination": state.destination,
            "mode": state.mode,
            "user_id": state.user_id
        }
    ) as span:
        try:
            # Create a copy of the state to avoid conflicts
            state_copy = state.model_copy(deep=True)
            
            # Comprehensive search for route information
            search_queries = [
                {
                    "query": f"transportation {state_copy.source} to {state_copy.destination} local tips routes",
                    "category": "route_info",
                    "description": "General route and transportation information"
                },
                {
                    "query": f"attractions points of interest landmarks between {state_copy.source} {state_copy.destination}",
                    "category": "poi_info",
                    "description": "Points of interest along the route"
                },
                {
                    "query": f"current traffic conditions roadworks {state_copy.source} {state_copy.destination} today",
                    "category": "traffic_info",
                    "description": "Current traffic and road conditions"
                },
                {
                    "query": f"weather conditions {state_copy.source} {state_copy.destination} current",
                    "category": "weather_info",
                    "description": "Current weather conditions"
                },
                {
                    "query": f"local events festivals {state_copy.source} {state_copy.destination} today this week",
                    "category": "events_info",
                    "description": "Local events and activities"
                },
                {
                    "query": f"public transport bus train schedule {state_copy.source} {state_copy.destination}",
                    "category": "transit_info",
                    "description": "Public transport information"
                }
            ]
            
            span.update(
                input={
                    "search_queries": search_queries,
                    "source": state.source,
                    "destination": state.destination
                }
            )
            
            # Execute all searches
            search_results = {}
            successful_searches = 0
            for search_item in search_queries:
                try:
                    result = serper_tool._run(search_item["query"])
                    if result["status"] == "success":
                        search_results[search_item["category"]] = {
                            "query": search_item["query"],
                            "description": search_item["description"],
                            "data": result["general_info"],
                            "timestamp": datetime.now().isoformat()
                        }
                        successful_searches += 1
                    else:
                        print(f"Search failed for {search_item['category']}: {result.get('error', 'Unknown error')}")
                        search_results[search_item["category"]] = {
                            "query": search_item["query"],
                            "description": search_item["description"],
                            "error": result.get('error', 'Unknown error'),
                            "timestamp": datetime.now().isoformat()
                        }
                except Exception as e:
                    print(f"Exception during search for {search_item['category']}: {str(e)}")
                    search_results[search_item["category"]] = {
                        "query": search_item["query"],
                        "description": search_item["description"],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Organize results into state fields
            state.local_insights = {
                "route_info": search_results.get("route_info", {}),
                "traffic_info": search_results.get("traffic_info", {}),
                "weather_info": search_results.get("weather_info", {}),
                "events_info": search_results.get("events_info", {}),
                "transit_info": search_results.get("transit_info", {})
            }
            
            # POI information
            poi_data = search_results.get("poi_info", {})
            if poi_data and "data" in poi_data:
                state.poi_information = [{
                    "type": "attractions",
                    "data": poi_data["data"],
                    "query": poi_data["query"],
                    "timestamp": poi_data["timestamp"]
                }]
            
            # Route context data
            state.route_context_data = []
            for category, data in search_results.items():
                if data and "data" in data and data["data"]:
                    state.route_context_data.append({
                        "type": category,
                        "data": data["data"],
                        "query": data["query"],
                        "timestamp": data["timestamp"]
                    })
            
            print(f"Local knowledge gathered: {successful_searches}/{len(search_queries)} searches successful")
            
            state.current_step = "local_knowledge_completed"
            state.agents_completed.append("local_knowledge_agent")
            
            span.update(
                status="completed",
                output={
                    "searches_executed": len(search_queries),
                    "successful_searches": successful_searches,
                    "search_results": search_results,
                    "local_insights_categories": list(state.local_insights.keys()),
                    "poi_information_count": len(state.poi_information) if state.poi_information else 0,
                    "route_context_data_count": len(state.route_context_data)
                }
            )
            
        except Exception as e:
            print(f"Error in local knowledge agent: {str(e)}")
            span.update(
                status="error",
                error=str(e)
            )
            state.errors.append({
                "node": "local_knowledge_agent",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        return state

def disruption_monitoring_node(state: TravelState) -> TravelState:
    """
    Monitor for disruptions and provide alternative routes
    """
    print("Monitoring for disruptions along selected routes")
    
    try:
        route_areas = []
        
        # Collect route areas for disruption checking
        all_routes = state.primary_routes + state.supplementary_routes + state.transit_routes
        for route in all_routes:
            # Extract area information from route (simplified)
            route_area = f"{state.source}-{state.destination}"
            route_areas.append(route_area)
        
        # Check for disruptions
        for area in set(route_areas):  # Remove duplicates
            disruption_result = disruption_tool.get_disruptions(area)
            
            if disruption_result["status"] == "success":
                disruptions = disruption_result["disruptions"]
                for disruption in disruptions:
                    state.current_disruptions.append({
                        "disruption_id": disruption["disruption_id"],
                        "location": disruption["location"],
                        "type": disruption["type"],
                        "severity": disruption["severity"],
                        "description": disruption["description"],
                        "timestamp": disruption["timestamp"]
                    })
        
        # Generate alternative routes if high-severity disruptions found
        high_severity_disruptions = [d for d in state.current_disruptions 
                                   if d["severity"] == "high"]
        
        if high_severity_disruptions:
            print(f"Found {len(high_severity_disruptions)} high-severity disruptions")
            
            # Get alternative routes (re-run routing with different parameters)
            alt_route_result = google_maps_tool._run(
                origin=state.source,
                destination=state.destination,
                mode="transit" if state.mode == "transit" else state.mode,
                alternatives=True
            )
            
            if alt_route_result["status"] == "success":
                alt_routes = alt_route_result["routes"][2:]  # Get additional alternatives
                for i, route in enumerate(alt_routes):
                    state.alternative_routes_due_disruptions.append({
                        "route_id": f"disruption_alt_{i}",
                        "duration": route["legs"][0]["duration"]["value"] // 60,
                        "distance": route["legs"][0]["distance"]["value"] / 1000,
                        "reason": "avoiding_disruption",
                        "avoided_disruptions": [d["disruption_id"] for d in high_severity_disruptions]
                    })
        
        state.current_step = "disruption_monitoring_completed"
        state.agents_completed.append("disruption_monitoring")
        
    except Exception as e:
        state.errors.append({
            "node": "disruption_monitoring",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def route_optimization_node(state: TravelState) -> TravelState:
    """
    Optimize and rank all routes based on multiple criteria
    """
    print("Optimizing and ranking routes")
    
    try:
        # Collect all routes for comparison
        all_routes = []
        
        print(f"Starting with {len(state.primary_routes)} primary routes and {len(state.supplementary_routes)} supplementary routes")
        
        # Add standard routes - convert RouteInfo objects to dictionaries
        for route in state.primary_routes + state.supplementary_routes:
            print(f"Processing route: {getattr(route, 'route_id', 'unknown')}")
            
            # Convert RouteInfo to dict if it's not already a dict
            if hasattr(route, 'dict'):
                route_dict = route.dict()
                print(f"✓ Converted RouteInfo to dict")
            elif isinstance(route, dict):
                route_dict = route
                print(f"✓ Route is already a dict")
            else:
                # If it's a RouteInfo object, access attributes directly
                route_dict = {
                    "route_id": getattr(route, 'route_id', str(route)),
                    "duration": getattr(route, 'duration', 60),
                    "distance": getattr(route, 'distance', 10),
                    "steps": getattr(route, 'steps', []),
                    "mode_details": getattr(route, 'mode_details', {"mode": "unknown"})
                }
                print(f"✓ Created dict from RouteInfo object")
            
            route_with_category = {
                **route_dict,
                "category": "standard"
            }
            all_routes.append(route_with_category)
            print(f"  → Added route: {route_with_category['route_id']} ({route_with_category['duration']} min, {route_with_category['distance']:.1f} km)")
        
        # Add transit routes - same conversion
        for route in state.transit_routes:
            print(f"Processing transit route: {getattr(route, 'route_id', 'unknown')}")
            if hasattr(route, 'dict'):
                route_dict = route.dict()
            elif isinstance(route, dict):
                route_dict = route
            else:
                route_dict = {
                    "route_id": getattr(route, 'route_id', str(route)),
                    "duration": getattr(route, 'duration', 60),
                    "distance": getattr(route, 'distance', 10),
                    "steps": getattr(route, 'steps', []),
                    "mode_details": getattr(route, 'mode_details', {"mode": "transit"})
                }
            
            route_with_category = {
                **route_dict,
                "category": "transit"
            }
            all_routes.append(route_with_category)
            print(f"  → Added transit route: {route_with_category['route_id']}")
        
        # Add disruption alternative routes - same conversion
        for route in state.alternative_routes_due_disruptions:
            print(f"Processing disruption route: {getattr(route, 'route_id', 'unknown')}")
            if hasattr(route, 'dict'):
                route_dict = route.dict()
            elif isinstance(route, dict):
                route_dict = route
            else:
                route_dict = {
                    "route_id": getattr(route, 'route_id', str(route)),
                    "duration": getattr(route, 'duration', 60),
                    "distance": getattr(route, 'distance', 10),
                    "steps": getattr(route, 'steps', []),
                    "mode_details": getattr(route, 'mode_details', {"mode": "alternative"})
                }
            
            route_with_category = {
                **route_dict,
                "category": "disruption_alternative"
            }
            all_routes.append(route_with_category)
            print(f"  → Added disruption route: {route_with_category['route_id']}")
        
        print(f"\n📊 Total routes collected for comparison: {len(all_routes)}")
        
        if all_routes:
            print(f"🔍 First route summary: {all_routes[0]['route_id']} - {all_routes[0]['duration']} min, {all_routes[0]['distance']:.1f} km")
            
            # Use route comparison tool
            print("\n⚖️  Calling route comparison tool...")
            
            # Create default user preferences if none exist
            user_prefs = state.current_user_preferences
            if user_prefs is None:
                user_prefs = {
                    "budget_preference": "medium",
                    "time_vs_cost_weight": 0.5,
                    "comfort_preference": 0.7,
                    "max_walking_distance": 1.0,
                    "preferred_transit_modes": ["bus", "train"]
                }
                print("⚠️  No user preferences found, using defaults")
            
            # Ensure weights exist
            weights = state.preference_weight_factors
            if not weights:
                weights = {
                    "time": 0.3,
                    "cost": 0.25,
                    "comfort": 0.2,
                    "convenience": 0.15,
                    "reliability": 0.1
                }
                print("⚠️  No preference weights found, using defaults")
            
            comparison_result = route_comparison_tool._run(
                routes=all_routes,
                user_preferences=user_prefs,
                weights=weights
            )
            
            print(f"📈 Route comparison result: {comparison_result['status']}")
            
            if comparison_result["status"] == "success":
                ranked_routes = comparison_result["ranked_routes"]
                print(f"🏆 Number of ranked routes: {len(ranked_routes)}")
                
                # Store top recommendations
                state.recommended_routes = ranked_routes[:state.config.get("max_routes", 5)]
                print(f"💾 Stored {len(state.recommended_routes)} recommended routes")
                
                # Store route rankings
                for ranked_route in ranked_routes:
                    route_id = ranked_route["route"]["route_id"]
                    state.route_rankings[route_id] = ranked_route["score"]["total"]
                    print(f"  → Route {route_id}: Score {ranked_route['score']['total']:.3f}")
            else:
                print(f"❌ Route comparison failed: {comparison_result.get('error', 'Unknown error')}")
        else:
            print("⚠️  No routes to compare!")
        
        state.current_step = "route_optimization_completed"
        state.agents_completed.append("route_optimization")
        
    except Exception as e:
        print(f"❌ Error in route_optimization_node: {str(e)}")
        import traceback
        traceback.print_exc()
        state.errors.append({
            "node": "route_optimization",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def response_compilation_node(state: TravelState) -> TravelState:
    """
    Compile final response with all route information in Google Maps API format
    """
    print("Compiling final response")
    
    try:
        # Build response in Google Maps API format
        response = {
            "request_id": state.request_id,
            "origin": f"{state.source}, Sri Lanka",
            "destination": f"{state.destination}, Sri Lanka",
            "mode": state.mode,
            "user_id": state.user_id,
            "all_routes": [],
            "best_route": None,
            "total_routes_found": 0
        }
        
        # Collect all routes from different sources
        all_routes = []
        
        # Add primary routes
        for route in state.primary_routes:
            all_routes.append({
                "source": "primary",
                "route_data": route
            })
        
        # Add supplementary routes
        for route in state.supplementary_routes:
            all_routes.append({
                "source": "supplementary", 
                "route_data": route
            })
        
        # Add transit routes
        for route in state.transit_routes:
            all_routes.append({
                "source": "transit",
                "route_data": route
            })
        
        # Add disruption alternative routes
        for route in state.alternative_routes_due_disruptions:
            all_routes.append({
                "source": "disruption_alternative",
                "route_data": route
            })
        
        # Process each route into Google Maps format
        processed_routes = []
        best_route_score = -1
        best_route_index = 0
        
        for i, route_info in enumerate(all_routes):
            route = route_info["route_data"]
            source = route_info["source"]
            
            # Format route in Google Maps API structure
            formatted_route = _format_route_for_response(route, state, source)
            
            # Add recommendation score if available
            if state.recommended_routes:
                for rec in state.recommended_routes:
                    if rec["route"]["route_id"] == route.get("route_id"):
                        formatted_route["recommendation_score"] = rec["score"]["total"]
                        formatted_route["score_breakdown"] = rec["breakdown"]
                        break
                else:
                    # If no recommendation score found, set default
                    formatted_route["recommendation_score"] = 0.0
            else:
                # If no recommended routes, set default
                formatted_route["recommendation_score"] = 0.0
            
            processed_routes.append(formatted_route)
            
            # Track best route
            if formatted_route.get("recommendation_score", 0) > best_route_score:
                best_route_score = formatted_route["recommendation_score"]
                best_route_index = i
        
        response["all_routes"] = processed_routes
        response["total_routes_found"] = len(processed_routes)
        
        # Set best route
        if processed_routes:
            response["best_route"] = processed_routes[best_route_index]
            response["best_route"]["is_recommended"] = True
            
            # Mark other routes as not recommended
            for i, route in enumerate(response["all_routes"]):
                if i != best_route_index:
                    route["is_recommended"] = False
        

        
        # Add comprehensive search results and contextual information
        if state.local_insights or state.poi_information or state.route_context_data:
            # Prepare search data for LLM summarization
            search_data_for_summary = {
                "general_info": {
                    "summary": f"Route from {state.source} to {state.destination}",
                    "key_points": [],
                    "relevant_links": []
                },
                "raw_results": {
                    "local_insights": state.local_insights,
                    "poi_information": state.poi_information,
                    "route_context": state.route_context_data
                }
            }
            
            # Generate user-friendly summary using LLM if available
            user_friendly_summary = "No additional local information available."
            if llm_summarizer:
                try:
                    # Create a comprehensive query for the LLM
                    llm_query = f"travel from {state.source} to {state.destination} by {state.mode}"
                    
                    # Add context about what the user might want to know
                    context = f"User is planning a {state.mode} journey and wants practical, local information about the destination area."
                    
                    # Generate summary
                    summary_result = llm_summarizer.summarize_search_results(
                        search_data_for_summary, 
                        llm_query, 
                        context
                    )
                    
                    if summary_result["status"] == "success":
                        user_friendly_summary = summary_result["summary"]
                        print(f"✅ LLM Summary generated: {len(user_friendly_summary.split(chr(10)))} lines")
                    else:
                        print(f"⚠️  LLM Summary failed: {summary_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"⚠️  Error generating LLM summary: {str(e)}")
                    user_friendly_summary = "Local information available but summary generation failed."
            
            # Add ONLY the LLM-generated destination summary - nothing else
            response["destination_summary"] = user_friendly_summary
        
        # Add disruption information if any
        if state.current_disruptions:
            response["active_disruptions"] = [
                {
                    "disruption_id": d.disruption_id,
                    "location": d.location,
                    "type": d.type,
                    "severity": d.severity,
                    "description": d.description,
                    "timestamp": d.timestamp.isoformat()
                }
                for d in state.current_disruptions
            ]
        
        state.final_response = response
        state.current_step = "completed"
        state.agents_completed.append("response_compilation")
        
    except Exception as e:
        state.errors.append({
            "node": "response_compilation",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        
        # Create error response
        state.final_response = {
            "request_id": state.request_id,
            "status": "error",
            "error": "Failed to compile response",
            "details": state.errors
        }
    
    return state

def _format_route_for_response(route: Dict, state: TravelState, source: str) -> Dict:
    """
    Format a route into Google Maps API response structure
    """
    try:
        # Calculate duration and distance
        duration_minutes = route.get("duration", 0)
        distance_km = route.get("distance", 0)
        
        # Format duration text
        if duration_minutes < 60:
            duration_text = f"{duration_minutes} mins"
        else:
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            if minutes == 0:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''} {minutes} mins"
        
        # Format distance text
        if distance_km < 1:
            distance_text = f"{int(distance_km * 1000)} m"
        else:
            distance_text = f"{distance_km:.1f} km"
        
        # Calculate start and end times
        departure_time = state.departure_time or datetime.now()
        start_time = departure_time.strftime("%I:%M %p")
        
        end_time = departure_time + timedelta(minutes=duration_minutes)
        end_time_str = end_time.strftime("%I:%M %p")
        
        # Format steps
        formatted_steps = []
        steps = route.get("steps", [])
        
        for step in steps:
            formatted_step = {
                "html_instructions": step.get("html_instructions", ""),
                "distance": step.get("distance", {}).get("text", "0 m"),
                "duration": step.get("duration", {}).get("text", "0 mins"),
                "travel_mode": step.get("travel_mode", "UNKNOWN"),
                "transit_details": None
            }
            
            # Add transit details if available
            if step.get("transit_details"):
                transit_detail = step["transit_details"]
                line = transit_detail.get("line", {})
                
                formatted_step["transit_details"] = {
                    "arrival_stop": transit_detail.get("arrival_stop", {}).get("name", ""),
                    "departure_stop": transit_detail.get("departure_stop", {}).get("name", ""),
                    "line_name": line.get("name", ""),
                    "vehicle_type": line.get("vehicle", {}).get("type", ""),
                    "num_stops": transit_detail.get("num_stops", 0),
                    "departure_time": transit_detail.get("departure_time", {}).get("text", "")
                }
            
            # Add fare details if available
            if step.get("fare_details"):
                formatted_step["fare_details"] = step["fare_details"]
                
                # Add Uber alternative if available
                if step["fare_details"].get("uber_alternative"):
                    formatted_step["uber_alternative"] = step["fare_details"]["uber_alternative"]
            
            formatted_steps.append(formatted_step)
        
        # Build the formatted route
        formatted_route = {
            "route_id": route.get("route_id", f"route_{source}"),
            "origin": f"{state.source}, Sri Lanka",
            "destination": f"{state.destination}, Sri Lanka",
            "distance_text": distance_text,
            "duration_text": duration_text,
            "start_time": start_time,
            "end_time": end_time_str,
            "steps": formatted_steps,
            "estimated_cost": route.get("fare_estimate"),
            "cost_currency": "LKR",
            "route_source": source,
            "transit_modes": route.get("transit_modes", []),
            "transfers": route.get("transfers", 0),
            "walking_distance": route.get("walking_distance", 0),
            "polyline": route.get("polyline", ""),
            "mode_details": route.get("mode_details", {}),
            "step_fares": route.get("step_fares", []),  # Add step-level fare breakdown
            "is_recommended": False  # Will be set later
        }
        
        # Add last mile information if available
        last_mile_for_route = [
            lm for lm in state.last_mile_options 
            if lm["route_id"] == route.get("route_id")
        ]
        if last_mile_for_route:
            formatted_route["last_mile_option"] = last_mile_for_route[0]["option"]
        
        return formatted_route
        
    except Exception as e:
        print(f"Error formatting route: {str(e)}")
        # Return a basic formatted route
        return {
            "route_id": route.get("route_id", "unknown"),
            "origin": f"{state.source}, Sri Lanka",
            "destination": f"{state.destination}, Sri Lanka",
            "distance_text": "Unknown",
            "duration_text": "Unknown",
            "start_time": "Unknown",
            "end_time": "Unknown",
            "steps": [],
            "estimated_cost": route.get("fare_estimate"),
            "cost_currency": "LKR",
            "route_source": source,
            "error": str(e)
        }

# Conditional routing functions
def should_use_multi_agent(state: TravelState) -> str:
    """Determine if multi-agent processing is needed"""
    if state.mode == "transit":
        return "transit_processing"
    elif state.mode in ["driving", "two_wheeler", "uber"]:
        return "standard_processing"
    else:
        return "standard_processing"  # Default fallback

def multi_agent_complete_check(state: TravelState) -> str:
    """Check if all multi-agent nodes are complete"""
    required_agents = [
        "transit_route_aggregation",
        "fare_calculation", 
        "user_preference_analysis",
        "local_knowledge_agent"
    ]
    
    completed = set(state.agents_completed)
    if all(agent in completed for agent in required_agents):
        return "optimization"
    else:
        return "continue_processing"