from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.models.travel_schema import TravelState
from app.services.tool_functions import *
from app.services.analysis_tools import *
import json
from datetime import datetime

# Initialize tools
google_maps_tool = GoogleMapsAPITool()
serper_tool = SerperWebSearchTool()
fare_tool = FareDatabaseTool()
preference_tool = UserPreferenceTool()
disruption_tool = DisruptionDatabaseTool()
route_comparison_tool = RouteComparisonTool()
last_mile_tool = LastMileOptimizerTool()
preference_learning_tool = PreferenceLearningTool()

def input_processing_node(state: TravelState) -> TravelState:
    """
    Process and validate user input, initialize preferences
    """
    print(f"Processing input for {state.mode} travel from {state.source} to {state.destination}")
    
    try:
        # Get user preferences
        pref_result = preference_tool.get_preferences(state.user_id)
        if pref_result["status"] == "success":
            state.current_user_preferences = pref_result["preferences"]
        
        # Set processing step
        state.current_step = "input_processed"
        state.agents_completed.append("input_processing")
        
        return state
    except Exception as e:
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
                        "mode_details": {"mode": state.mode}
                    })
                    print(f"Added supplementary route: {state.supplementary_routes[-1]['route_id']}")
            else:
                print("No routes returned from Google Maps API")
        else:
            print(f"Google Maps API failed: {route_result.get('error', 'Unknown error')}")
        
        print(f"Total routes in state: {len(state.primary_routes) + len(state.supplementary_routes)}")
        
        state.current_step = "standard_routes_completed"
        state.agents_completed.append("standard_route")
        
    except Exception as e:
        print(f"Error in standard_route_node: {str(e)}")
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
            departure_time=state.departure_time
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
                    "transit_modes": transit_modes,
                    "transfers": max(0, transfers - 1),
                    "walking_distance": walking_distance,
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
            
            # Get base transit fares
            for mode in route.get("transit_modes", []):
                fare_result = fare_tool._run("transit", state.source, state.destination, mode)
                if fare_result["status"] == "success" and fare_result["fares"]:
                    mode_fare = fare_result["fares"][0].get("base_fare", 5)
                    route_fare += mode_fare
            
            # Add transfer penalty
            transfers = route.get("transfers", 0)
            route_fare += transfers * 2  # $2 per transfer
            
            # Check if last mile is needed
            route_end_distance = 0.5  # Simplified - assume 500m from final destination
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
            
            route["fare_estimate"] = route_fare
            total_estimated_fare = max(total_estimated_fare, route_fare)
        
        state.total_fare_estimate = total_estimated_fare
        state.current_step = "fare_calculation_completed"
        state.agents_completed.append("fare_calculation")
        
    except Exception as e:
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
    
    try:
        # Search for information about the route area
        route_query = f"transportation {state.source} to {state.destination} local tips"
        search_result = serper_tool._run(route_query)
        
        if search_result["status"] == "success":
            state.local_insights["route_info"] = search_result["general_info"]
            state.local_insights["traffic_info"] = search_result["traffic_info"]
        
        # Search for POIs and attractions along the route
        poi_query = f"attractions points of interest between {state.source} {state.destination}"
        poi_result = serper_tool._run(poi_query)
        
        if poi_result["status"] == "success":
            state.poi_information.append({
                "type": "attractions",
                "data": poi_result["general_info"]
            })
        
        # Search for current conditions and events
        conditions_query = f"current conditions events {state.source} {state.destination} today"
        conditions_result = serper_tool._run(conditions_query)
        
        if conditions_result["status"] == "success":
            state.route_context_data.append({
                "type": "current_conditions",
                "data": conditions_result["general_info"],
                "timestamp": datetime.now().isoformat()
            })
        
        state.current_step = "local_knowledge_completed"
        state.agents_completed.append("local_knowledge_agent")
        
    except Exception as e:
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
            comparison_result = route_comparison_tool._run(
                routes=all_routes,
                user_preferences=state.current_user_preferences,
                weights=state.preference_weight_factors
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
    Compile final response with all route information
    """
    print("Compiling final response")
    
    try:
        # Build comprehensive response
        response = {
            "request_id": state.request_id,
            "query": {
                "source": state.source,
                "destination": state.destination,
                "mode": state.mode,
                "user_id": state.user_id
            },
            "recommended_routes": [],
            "metadata": {
                "processing_time": (datetime.now() - state.processing_start_time).total_seconds(),
                "agents_used": state.agents_completed,
                "disruptions_count": len(state.current_disruptions),
                "has_local_insights": bool(state.local_insights),
                "preference_applied": bool(state.preference_weight_factors)
            }
        }
        
        # Add route recommendations
        for recommendation in state.recommended_routes:
            route = recommendation["route"]
            score_breakdown = recommendation["breakdown"]
            
            route_info = {
                "route_id": route["route_id"],
                "summary": {
                    "duration_minutes": route["duration"],
                    "distance_km": route["distance"],
                    "estimated_fare": route.get("fare_estimate"),
                    "mode": route.get("category", "unknown")
                },
                "score": {
                    "overall": recommendation["score"]["total"],
                    "breakdown": score_breakdown
                },
                "details": {
                    "steps_count": len(route.get("steps", [])),
                    "mode_details": route.get("mode_details", {})
                }
            }
            
            # Add transit-specific information
            if route.get("transit_modes"):
                route_info["transit_info"] = {
                    "modes": route["transit_modes"],
                    "transfers": route.get("transfers", 0),
                    "walking_distance_km": route.get("walking_distance", 0)
                }
            
            # Add last mile information
            last_mile_for_route = [
                lm for lm in state.last_mile_options 
                if lm["route_id"] == route["route_id"]
            ]
            if last_mile_for_route:
                route_info["last_mile"] = last_mile_for_route[0]["option"]
            
            response["recommended_routes"].append(route_info)
        
        # Add contextual information
        if state.local_insights:
            response["local_insights"] = {
                "has_route_info": "route_info" in state.local_insights,
                "has_traffic_info": "traffic_info" in state.local_insights,
                "poi_count": len(state.poi_information)
            }
        
        # Add disruption information
        if state.current_disruptions:
            response["disruptions"] = [
                {
                    "type": d["type"],
                    "severity": d["severity"],
                    "location": d["location"],
                    "description": d["description"]
                }
                for d in state.current_disruptions
            ]
        
        # Add errors if any
        if state.errors:
            response["warnings"] = [
                {
                    "source": error["node"],
                    "message": error["error"]
                }
                for error in state.errors
            ]
        
        state.final_response = response
        state.current_step = "completed"
        state.agents_completed.append("response_compilation")
        
        # Update user preferences based on this interaction
        if state.current_user_preferences:
            # This would be called after user makes a selection
            # preference_tool.update_preferences(
            #     state.user_id, 
            #     state.current_user_preferences, 
            #     {"current_query": state.final_response}
            # )
            pass
        
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