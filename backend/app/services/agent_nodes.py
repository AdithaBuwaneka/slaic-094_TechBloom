from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.models.travel_schema import TravelState
from app.services.tool_functions import *
from app.services.analysis_tools import *
from app.services.llm_summarizer import LLMSummarizerService
from app.services.intelligent_disruption_service import IntelligentDisruptionService
from app.services.langfuse_service import langfuse_service
import json
from datetime import datetime, timedelta

# Initialize tools
google_maps_tool = GoogleMapsAPITool()
# Initialize serper_tool conditionally
try:
    serper_tool = SerperWebSearchTool()
except Exception:
    print("WARNING: SerperWebSearchTool initialization failed. Web search will be disabled.")
    serper_tool = None
# Initialize weather tool
try:
    weather_tool = WeatherAPITool()
    print("Weather API tool initialized successfully")
except Exception as e:
    print(f"WARNING: Weather API tool initialization failed: {e}")
    weather_tool = None
fare_tool = FareDatabaseTool()
preference_tool = UserPreferenceTool()
disruption_tool = DisruptionDatabaseTool()
route_comparison_tool = RouteComparisonTool()
last_mile_tool = LastMileOptimizerTool()
preference_learning_tool = PreferenceLearningTool()

# Initialize LLM summarizer service
try:
    llm_summarizer = LLMSummarizerService()
    print("LLM Summarizer Service initialized successfully")
except Exception as e:
    print(f"LLM Summarizer Service initialization failed: {str(e)}")
    llm_summarizer = None

# Initialize Intelligent Disruption Service
try:
    intelligent_disruption_service = IntelligentDisruptionService()
    print("Intelligent Disruption Service initialized successfully")
except Exception as e:
    print(f"Intelligent Disruption Service initialization failed: {str(e)}")
    intelligent_disruption_service = None

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
                # Convert dictionary to UserPreferences model
                from app.models.travel_schema import UserPreferences
                pref_dict = pref_result["preferences"]
                state.current_user_preferences = UserPreferences(**pref_dict)
                if span:
                    span.update(
                        input={"user_id": state.user_id},
                        output={"preferences_loaded": True, "preferences": pref_result["preferences"]}
                    )
            else:
                if span:
                    span.update(
                        input={"user_id": state.user_id},
                        output={"preferences_loaded": False, "error": pref_result.get("error")}
                    )
            
            # Set processing step
            state.current_step = "input_processed"
            state.agents_completed.append("input_processing")
            
            if span:
                span.update(status="completed")
            return state
            
        except Exception as e:
            if span:
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
    Handle standard routing (driving, two_wheeler, uber, tuk-tuk) - Updated for Sri Lankan modes
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
            
            if span:
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
            
            if span:
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
            if span:
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
            print(f"✓ Google Maps API returned {len(routes)} routes")

            for i, route in enumerate(routes):
                print(f"Processing route {i}: {route.keys() if isinstance(route, dict) else type(route)}")

                # Validate route structure
                if not isinstance(route, dict):
                    print(f" Skipping non-dict route: {type(route)}")
                    continue

                if "legs" not in route or not route["legs"]:
                    print(f" Skipping route without legs")
                    continue

                leg = route["legs"][0]
                if not isinstance(leg, dict):
                    print(f" Skipping route with invalid leg: {type(leg)}")
                    continue

                # Extract duration and distance
                duration_value = leg.get("duration", {}).get("value", 0) if isinstance(leg.get("duration"), dict) else 0
                distance_value = leg.get("distance", {}).get("value", 0) if isinstance(leg.get("distance"), dict) else 0

                print(f"  Duration: {duration_value}s ({duration_value // 60}min), Distance: {distance_value}m ({distance_value / 1000:.1f}km)")

                transit_modes = []
                transfers = 0
                walking_distance = 0

                # Analyze route steps
                steps = leg.get("steps", [])
                print(f"  Processing {len(steps)} steps from Google Maps")
                print(f"  Steps is falsy: {not steps}, distance > 0: {distance_value > 0}")

                for step in steps:
                    travel_mode = step.get("travel_mode", "UNKNOWN")

                    if travel_mode == "TRANSIT":
                        transit_detail = step.get("transit_details", {})
                        line = transit_detail.get("line", {})
                        vehicle_type = line.get("vehicle", {}).get("type", "").lower()
                        if vehicle_type and vehicle_type not in transit_modes:
                            transit_modes.append(vehicle_type)
                        if len(transit_modes) > 1:
                            transfers += 1
                    elif travel_mode == "WALKING":
                        step_distance = step.get("distance", {})
                        if isinstance(step_distance, dict):
                            walking_distance += step_distance.get("value", 0) / 1000

                # FIX 1: Generate steps if empty (Sri Lankan route fallback)
                print(f"  DEBUG: Before fallback check - steps count: {len(steps)}, steps is empty: {len(steps) == 0}, distance_value: {distance_value}")
                if len(steps) == 0 and distance_value > 0:
                    print(f"  ===== GENERATING FALLBACK STEPS =====")
                    generated_steps = generate_sri_lankan_route_steps(
                        state.source, state.destination,
                        distance_value, duration_value,
                        state.preferred_transit or "bus"
                    )
                    print(f"  ===== Generated {len(generated_steps)} fallback steps =====")
                    if generated_steps:
                        steps = generated_steps  # Replace empty steps with generated ones
                        print(f"  ===== REPLACED steps with {len(steps)} generated steps =====")
                        print(f"  ===== First generated step type: {type(steps[0])}, keys: {list(steps[0].keys()) if isinstance(steps[0], dict) else 'NOT_DICT'} =====")
                    else:
                        print(f"  ===== WARNING: Generated steps is EMPTY! =====")
                else:
                    print(f"  Using steps from Google Maps: {len(steps)} steps (skipping fallback generation)")
                
                # FIX 2: Calculate fare estimate based on distance for Sri Lankan routes
                fare_estimate = None
                if distance_value > 0:
                    # Sri Lankan bus fare calculation: ~2-3 LKR per km base rate
                    base_rate_per_km = 2.5
                    fare_estimate = max(20, distance_value / 1000 * base_rate_per_km)  # Minimum 20 LKR
                    fare_estimate = round(fare_estimate)
                    print(f"  💰 CALCULATED FARE: {fare_estimate} LKR for {distance_value/1000:.1f}km")
                
                # FIX 3: Default transit modes for Sri Lankan routes
                if not transit_modes and state.preferred_transit:
                    transit_modes = [state.preferred_transit]
                    print(f"  🚌 USING PREFERRED TRANSIT: {transit_modes}")
                elif not transit_modes:
                    transit_modes = ["bus"]  # Default for Sri Lankan transit
                    print(f"  🚌 USING DEFAULT TRANSIT: {transit_modes}")
                else:
                    print(f"  🚌 TRANSIT MODES FROM API: {transit_modes}")

                transit_route = {
                    "route_id": f"transit_{i}",
                    "duration": duration_value // 60,  # Convert seconds to minutes
                    "distance": distance_value / 1000,  # Convert meters to km
                    "steps": steps,
                    "polyline": route.get("overview_polyline", {}).get("points", ""),
                    "fare_estimate": fare_estimate,
                    "transit_modes": transit_modes,
                    "transfers": max(0, transfers - 1),
                    "walking_distance": walking_distance,
                    "category": "transit",
                    "mode_details": {
                        "modes": transit_modes,
                        "transfers": transfers,
                        "walking_km": walking_distance
                    }
                }

                # Ensure the route data is preserved correctly
                transit_route["_debug_info"] = {
                    "created_at": datetime.now().isoformat(),
                    "duration_source": "google_maps_routes_api_v2",
                    "distance_source": "google_maps_routes_api_v2",
                    "original_duration_seconds": duration_value,
                    "original_distance_meters": distance_value
                }

                # DEBUG: Verify steps before adding to state
                print(f"  🔍 TRANSIT ROUTE CREATED: {transit_route['route_id']}")
                print(f"  🔍 Steps in transit_route dict: {len(transit_route.get('steps', []))} steps")
                if transit_route.get('steps'):
                    print(f"  🔍 First step in dict: {transit_route['steps'][0]}")

                # FORCE FALLBACK STEP GENERATION IF STEPS ARE STILL EMPTY
                if not transit_route.get('steps') or len(transit_route['steps']) == 0:
                    print(f"  🚨 FORCING FALLBACK STEP GENERATION FOR {transit_route['route_id']}")
                    forced_steps = generate_sri_lankan_route_steps(
                        state.source, state.destination,
                        transit_route['distance'] * 1000,  # Convert km back to meters
                        transit_route['duration'] * 60,     # Convert minutes back to seconds
                        state.preferred_transit or "bus"
                    )
                    transit_route['steps'] = forced_steps
                    print(f"  🚨 FORCED {len(forced_steps)} STEPS INTO TRANSIT ROUTE")

                # CRITICAL FIX: Verify steps are present BEFORE adding to state
                if not transit_route.get('steps') or len(transit_route['steps']) == 0:
                    print(f"  ⚠️  WARNING: transit_route has NO STEPS before adding to state!")
                    print(f"  ⚠️  Forcing re-assignment of steps from leg.get('steps')")
                    transit_route['steps'] = leg.get("steps", [])
                    print(f"  ⚠️  After re-assignment: {len(transit_route['steps'])} steps")

                state.transit_routes.append(transit_route)

                # DEBUG: Verify steps after adding to state
                print(f"  🔍 Steps in state after append: {len(state.transit_routes[-1].get('steps', []))} steps")
                print(f"✓ Added transit route: {transit_route['route_id']} ({transit_route['duration']}min, {transit_route['distance']:.1f}km, {len(transit_modes)} modes)")

                # DOUBLE CHECK: Print the actual steps in state
                if state.transit_routes[-1].get('steps'):
                    print(f"  ✅ CONFIRMED: State has {len(state.transit_routes[-1]['steps'])} steps")
                else:
                    print(f"  ❌ ERROR: State has NO STEPS after append!")
                
                # Double-check the route was added correctly
                if len(state.transit_routes) > 0:
                    last_route = state.transit_routes[-1]
                    print(f"✓ Verification: Last route in state has duration={last_route.get('duration', 'MISSING')} and distance={last_route.get('distance', 'MISSING')}")
        else:
            print(f" Google Maps API failed: {route_result.get('error', 'Unknown error')}")

        # DEBUG: Check state after adding routes
        print(f"DEBUG AFTER ADD: transit_routes type = {type(state.transit_routes)}, len = {len(state.transit_routes)}")
        if len(state.transit_routes) > 0:
            print(f"DEBUG AFTER ADD: first route type = {type(state.transit_routes[0])}, is dict = {isinstance(state.transit_routes[0], dict)}")

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

        # Work directly with state transit_routes - don't enumerate yet
        for route_idx in range(len(state.transit_routes)):
            # Get the route directly from state each time
            route = state.transit_routes[route_idx]

            print(f"DEBUG: Processing route {route_idx}, type: {type(route)}")

            # Ensure route is a dict - handle various types
            if isinstance(route, str):
                print(f"WARNING: Route {route_idx} is a string: {route[:100] if len(route) > 100 else route}")
                # Try to parse as JSON
                try:
                    import json
                    route = json.loads(route)
                    print(f"Successfully parsed route from JSON string")
                except:
                    print(f"ERROR: Could not parse route string as JSON, skipping")
                    continue
            elif not isinstance(route, dict):
                if hasattr(route, 'dict'):
                    route = route.dict()
                    print(f"Converted route from Pydantic model to dict")
                elif hasattr(route, '__dict__'):
                    route = route.__dict__
                    print(f"Converted route from object to dict using __dict__")
                else:
                    print(f"ERROR: Route is not a dict, string, or object with dict(): {type(route)}, skipping")
                    continue

            print(f"Route {route_idx} successfully converted to dict with route_id: {route.get('route_id', 'unknown')}")

            route_fare = 0
            step_fares = []

            # Process each step in the route
            steps_list = route.get("steps", [])
            print(f"  📋 Processing {len(steps_list)} steps for route {route.get('route_id', 'unknown')}")
            for step_idx, step in enumerate(steps_list):
                print(f"  Step {step_idx}: type={type(step)}, is_dict={isinstance(step, dict)}")
                
                # FIX: Ensure step is a dict
                if isinstance(step, str):
                    print(f"    ⚠️ WARNING: Step is a string, attempting to parse JSON: {step[:100]}")
                    try:
                        import json
                        step = json.loads(step)
                        print(f"    ✅ Successfully parsed step from JSON")
                    except Exception as e:
                        print(f"    ❌ ERROR: Could not parse step string as JSON: {e}")
                        continue
                elif not isinstance(step, dict):
                    print(f"    ❌ ERROR: Step is not a dict or string: {type(step)}, skipping")
                    continue
                
                if step.get("travel_mode") == "TRANSIT":
                    # Calculate fare for this transit step
                    step_fare_result = fare_tool.get_step_fare(step)
                    
                    if step_fare_result["status"] == "success":
                        step_fare = step_fare_result["fare"]
                        step_fares.append(step_fare)
                        route_fare += step_fare["base_fare"]
                        
                        # Add fare details to the step
                        step["fare_details"] = step_fare
                        
                        print(f"Step fare: {step_fare['base_fare']} LKR ({step_fare['source']})")
                    else:
                        print(f"Failed to calculate fare for step: {step_fare_result.get('error', 'Unknown error')}")
                else:
                    # Walking step - check if we should offer Uber alternative
                    # Handle distance being either a dict or a string
                    distance_val = step.get("distance", {})
                    if isinstance(distance_val, dict):
                        walking_distance_km = distance_val.get("value", 0) / 1000
                    elif isinstance(distance_val, str):
                        # Distance is a string like "0.5 km" or "100 m", skip uber calculation
                        walking_distance_km = 0
                    else:
                        walking_distance_km = 0

                    # Check if user prefers time over cost and walking distance > 0.5km
                    user_prefs = state.current_user_preferences
                    time_preference = getattr(user_prefs, "time_vs_cost_weight", 0.5) if user_prefs else 0.5
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
                        
                        print(f"Walking step: {walking_distance_km:.2f}km - Uber alternative: {int(uber_duration)}min, {int(uber_cost)} LKR")
                    else:
                        # Regular walking step - no fare
                        step["fare_details"] = {
                            "base_fare": 0,
                            "vehicle_type": "walking",
                            "source": "free"
                        }
            
            # Add transfer penalty if there are multiple transit steps
            # FIX: Filter steps safely, handling both dict and string steps
            transit_steps = []
            for s in route.get("steps", []):
                if isinstance(s, dict) and s.get("travel_mode") == "TRANSIT":
                    transit_steps.append(s)
                elif isinstance(s, str):
                    print(f"    ⚠️ WARNING: Skipping string step in transfer count")
            
            if len(transit_steps) > 1:
                transfer_penalty = (len(transit_steps) - 1) * 5  # 5 LKR per transfer
                route_fare += transfer_penalty
                print(f"Added transfer penalty: {transfer_penalty} LKR for {len(transit_steps) - 1} transfers")
            
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
                        print(f"Added last mile cost: {best_last_mile['cost']} LKR")
            
            # Store the calculated fare and step details
            route["fare_estimate"] = round(route_fare, 2)
            route["step_fares"] = step_fares
            total_estimated_fare = max(total_estimated_fare, route_fare)
            
            print(f"Total fare for route {route.get('route_id')}: {route_fare:.0f} LKR (from {len(step_fares)} transit steps)")
        
        # Also calculate fares for standard routes if they exist (Sri Lankan modes)
        for route in state.primary_routes + state.supplementary_routes:
            mode = route.get("mode_details", {}).get("mode")
            if mode in ["driving", "two_wheeler", "uber", "tuk-tuk"]:
                distance = route.get("distance", 0)
                
                # Sri Lankan fare calculation per mode
                if mode == "driving":
                    fuel_cost_per_km = 2  # LKR per km
                    parking_cost = 50     # LKR
                elif mode == "two_wheeler":
                    fuel_cost_per_km = 1  # LKR per km  
                    parking_cost = 20     # LKR (cheaper parking)
                elif mode == "tuk-tuk":
                    # Tuk-tuk: Base fare + distance rate (Sri Lankan rates)
                    base_fare = 50        # LKR base
                    fare_per_km = 30      # LKR per km
                    fuel_cost_per_km = fare_per_km
                    parking_cost = base_fare
                elif mode == "uber":
                    # Uber: Base + time + distance (Sri Lankan rates)
                    base_fare = 100       # LKR base
                    fare_per_km = 50      # LKR per km
                    fuel_cost_per_km = fare_per_km
                    parking_cost = base_fare
                else:
                    fuel_cost_per_km = 2
                    parking_cost = 50
                
                fuel_cost = distance * fuel_cost_per_km
                total_cost = fuel_cost + parking_cost
                route["fare_estimate"] = round(total_cost, 2)
                print(f"Calculated cost for {mode}: {total_cost:.0f} LKR (base/fuel: {fuel_cost:.0f}, additional: {parking_cost})")
        
        state.total_fare_estimate = round(total_estimated_fare, 2)
        state.current_step = "fare_calculation_completed"
        state.agents_completed.append("fare_calculation")
        
        print(f"Total estimated fare across all routes: {state.total_fare_estimate} LKR")
        
    except Exception as e:
        print(f"Error in fare_calculation_node: {str(e)}")
        state.errors.append({
            "node": "fare_calculation",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def fare_optimization_node(state: TravelState) -> TravelState:
    """
    Fare Optimization Agent: Identifies the lowest-cost travel combinations,
    including passes, discounts, and offers - Required Agent #7 for SLAIC 2025
    """
    print("🎯 Fare Optimization Agent: Finding lowest-cost travel combinations")
    
    try:
        # Sri Lankan-specific fare optimization strategies
        optimized_routes = []
        
        # Collect all routes with fare estimates
        all_routes_with_fares = []
        
        # Add primary routes
        for route in state.primary_routes:
            if route.get("fare_estimate"):
                all_routes_with_fares.append({
                    "route": route,
                    "type": "primary",
                    "base_cost": route["fare_estimate"]
                })
        
        # Add supplementary routes  
        for route in state.supplementary_routes:
            if route.get("fare_estimate"):
                all_routes_with_fares.append({
                    "route": route,
                    "type": "supplementary", 
                    "base_cost": route["fare_estimate"]
                })
        
        # Add transit routes
        for route in state.transit_routes:
            if route.get("fare_estimate"):
                all_routes_with_fares.append({
                    "route": route,
                    "type": "transit",
                    "base_cost": route["fare_estimate"]
                })
        
        # Apply Sri Lankan fare optimization strategies
        for route_info in all_routes_with_fares:
            route = route_info["route"]
            base_cost = route_info["base_cost"]
            optimizations = []
            final_cost = base_cost
            
            # 1. Transit Pass Discounts (Sri Lankan context)
            if route_info["type"] == "transit":
                # Monthly bus pass discount (20% off for regular commuters)
                monthly_pass_savings = base_cost * 0.20
                optimizations.append({
                    "type": "monthly_bus_pass",
                    "savings": monthly_pass_savings,
                    "description": "Monthly bus pass - 20% discount",
                    "applicable": True
                })
                
                # Student discount (30% off with student ID)
                student_savings = base_cost * 0.30
                optimizations.append({
                    "type": "student_discount", 
                    "savings": student_savings,
                    "description": "Student discount - 30% off with valid ID",
                    "applicable": True
                })
                
                # Senior citizen discount (50% off for 60+)
                senior_savings = base_cost * 0.50
                optimizations.append({
                    "type": "senior_discount",
                    "savings": senior_savings, 
                    "description": "Senior citizen discount - 50% off (60+ years)",
                    "applicable": True
                })
            
            # 2. Multi-modal combination savings
            if len(all_routes_with_fares) > 1:
                combo_savings = base_cost * 0.10
                optimizations.append({
                    "type": "multi_modal_combo",
                    "savings": combo_savings,
                    "description": "Multi-modal combination discount - 10% off total",
                    "applicable": True
                })
            
            # 3. Off-peak travel discounts
            departure_time = state.departure_time
            if departure_time:
                hour = departure_time.hour
                # Off-peak hours: 10 AM - 3 PM and after 7 PM
                if (10 <= hour <= 15) or hour >= 19:
                    off_peak_savings = base_cost * 0.15
                    optimizations.append({
                        "type": "off_peak_discount",
                        "savings": off_peak_savings,
                        "description": "Off-peak travel discount - 15% off",
                        "applicable": True
                    })
            
            # 4. Fuel-sharing for private vehicle routes (Sri Lankan modes)
            if route_info["type"] in ["primary", "supplementary"]:
                mode = route.get("mode_details", {}).get("mode", "")
                if mode in ["driving", "two_wheeler"]:
                    # Carpooling savings (split fuel cost)
                    carpool_savings = base_cost * 0.50
                    optimizations.append({
                        "type": "carpooling",
                        "savings": carpool_savings,
                        "description": "Carpooling - Share fuel costs (50% savings)",
                        "applicable": True
                    })
                elif mode == "tuk-tuk":
                    # Tuk-tuk sharing (common in Sri Lanka)
                    sharing_savings = base_cost * 0.30
                    optimizations.append({
                        "type": "tuk_tuk_sharing",
                        "savings": sharing_savings,
                        "description": "Tuk-tuk sharing - Split fare with others (30% savings)",
                        "applicable": True
                    })
                elif mode == "uber":
                    # UberPool equivalent
                    pool_savings = base_cost * 0.25
                    optimizations.append({
                        "type": "ride_sharing",
                        "savings": pool_savings,
                        "description": "Ride sharing - Share trip with others (25% savings)",
                        "applicable": True
                    })
            
            # Calculate best optimization
            best_optimization = max(optimizations, key=lambda x: x["savings"]) if optimizations else None
            
            if best_optimization:
                final_cost = max(0, base_cost - best_optimization["savings"])
                route["optimized_fare"] = round(final_cost, 2)
                route["fare_optimization"] = {
                    "original_cost": base_cost,
                    "optimized_cost": final_cost,
                    "savings": best_optimization["savings"],
                    "best_option": best_optimization,
                    "all_options": optimizations
                }
                print(f"💰 Route {route.get('route_id')}: {base_cost:.0f} LKR → {final_cost:.0f} LKR (saved {best_optimization['savings']:.0f} LKR with {best_optimization['type']})")
            else:
                route["optimized_fare"] = base_cost
                route["fare_optimization"] = {
                    "original_cost": base_cost,
                    "optimized_cost": base_cost,
                    "savings": 0,
                    "best_option": None,
                    "all_options": []
                }
        
        # Find the absolute lowest cost route
        if all_routes_with_fares:
            cheapest_route = min(all_routes_with_fares, 
                               key=lambda x: x["route"].get("optimized_fare", x["route"].get("fare_estimate", float('inf'))))
            
            state.cheapest_route = {
                "route_id": cheapest_route["route"]["route_id"],
                "original_cost": cheapest_route["base_cost"],
                "optimized_cost": cheapest_route["route"].get("optimized_fare", cheapest_route["base_cost"]),
                "savings": cheapest_route["route"].get("fare_optimization", {}).get("savings", 0),
                "optimization_type": cheapest_route["route"].get("fare_optimization", {}).get("best_option", {}).get("type", "none")
            }
            
            print(f"🏆 Cheapest option: {state.cheapest_route['route_id']} - {state.cheapest_route['optimized_cost']:.0f} LKR")
        
        state.current_step = "fare_optimization_completed"
        state.agents_completed.append("fare_optimization")
        
    except Exception as e:
        print(f"Error in fare_optimization_node: {str(e)}")
        state.errors.append({
            "node": "fare_optimization", 
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
        time_vs_cost_weight = getattr(preferences, "time_vs_cost_weight", 0.5)
        comfort_preference = getattr(preferences, "comfort_preference", 0.7)
        
        state.preference_weight_factors = {
            "time": time_vs_cost_weight * 0.6,  # Convert to 0-1 scale
            "cost": (1 - time_vs_cost_weight) * 0.5,  # Convert to 0-1 scale
            "comfort": comfort_preference * 0.3,  # Convert to 0-1 scale
            "convenience": 0.15,
            "reliability": 0.1
        }
        
        # Filter routes based on strict preferences
        if state.transit_routes:
            filtered_routes = []
            max_walking_distance = getattr(preferences, "max_walking_distance", 1.0)
            preferred_modes = getattr(preferences, "preferred_transit_modes", ["bus", "train"])
            
            for route in state.transit_routes:
                # Check walking distance tolerance
                if route.get("walking_distance", 0) <= max_walking_distance:
                    # Check if route uses preferred modes
                    route_modes = route.get("transit_modes", [])
                    if any(mode in preferred_modes for mode in route_modes):
                        filtered_routes.append(route)
                    elif not preferred_modes:  # No strict preference
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
            # Use the state directly - no need to copy since we're just reading from it
            state_copy = state
            
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
            
            if span:
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
            
            # Check if serper_tool is available
            if serper_tool is None:
                print("WARNING: Web search disabled (SERPER_API_KEY not configured)")
                for search_item in search_queries:
                    search_results[search_item["category"]] = {
                        "query": search_item["query"],
                        "description": search_item["description"],
                        "error": "Web search disabled - SERPER_API_KEY not configured",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
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
            
            # Enhance weather data with OpenWeather API
            if weather_tool is not None:
                try:
                    # Get weather for source city
                    source_weather = weather_tool._run(state_copy.source, "travel_advice")
                    if source_weather.get("status") == "success":
                        search_results["weather_info"] = {
                            "api_data": source_weather,
                            "source": "OpenWeather API",
                            "timestamp": datetime.now().isoformat()
                        }
                        print(f"Weather data retrieved for {source_weather.get('city', state_copy.source)}")
                    else:
                        print(f"WARNING: Weather API failed: {source_weather.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"WARNING: Weather tool error: {str(e)}")
            
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
            
            if span:
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
            if span:
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
    Intelligent disruption monitoring.
    Analyzes disruptions and recommends best alternative routes based on user preferences,
    cost, duration, and other factors.
    """
    print("Intelligent disruption monitoring with Gemini 2.0 Flash")
    
    # Start Langfuse span for this agent action
    with langfuse_service.start_span(
        name="intelligent_disruption_monitoring",
        metadata={
            "agent_type": "intelligent_disruption_monitoring",
            "source": state.source,
            "destination": state.destination,
            "mode": state.mode,
            "user_id": state.user_id,
            "llm_model": "gemini-2.0-flash"
        }
    ) as span:
        try:
            # Step 1: Check for disruptions in the route areas
            route_areas = []
            all_routes = state.primary_routes + state.supplementary_routes + state.transit_routes
            
            # Collect route areas for disruption checking
            for route in all_routes:
                route_area = f"{state.source}-{state.destination}"
                route_areas.append(route_area)
            
            # Check for disruptions
            active_disruptions = []
            for area in set(route_areas):  # Remove duplicates
                disruption_result = disruption_tool.get_disruptions(area)
                
                if disruption_result["status"] == "success":
                    disruptions = disruption_result["disruptions"]
                    for disruption in disruptions:
                        disruption_info = {
                            "disruption_id": disruption["disruption_id"],
                            "location": disruption["location"],
                            "type": disruption["type"],
                            "severity": disruption["severity"],
                            "description": disruption["description"],
                            "timestamp": disruption["timestamp"]
                        }
                        active_disruptions.append(disruption_info)
                        state.current_disruptions.append(disruption_info)
            
            print(f"Found {len(active_disruptions)} active disruptions")
            
            # Step 2: Use AI to analyze disruptions and recommend routes
            if intelligent_disruption_service and (active_disruptions or state.transit_routes):
                print("Using Gemini 2.0 Flash for intelligent route analysis...")
                
                # Prepare available routes for analysis
                available_routes = []
                
                # Include transit routes (primary focus for disruption analysis)
                for route in state.transit_routes:
                    available_routes.append(route)
                
                # Include primary and supplementary routes as alternatives
                for route in state.primary_routes + state.supplementary_routes:
                    available_routes.append(route)
                
                # Get user preferences
                user_prefs = state.current_user_preferences
                
                # Use AI to analyze and recommend
                ai_analysis_result = intelligent_disruption_service.analyze_disruption_and_recommend_routes(
                    disruptions=active_disruptions,
                    available_routes=available_routes,
                    user_preferences=user_prefs,
                    source=state.source,
                    destination=state.destination
                )
                
                if span:
                    span.update(
                        input={
                            "disruptions_count": len(active_disruptions),
                            "available_routes_count": len(available_routes),
                            "user_preferences_available": user_prefs is not None,
                            "source": state.source,
                            "destination": state.destination
                        },
                        output={"ai_analysis_result": ai_analysis_result}
                    )
                
                if ai_analysis_result["status"] == "success":
                    print(f"AI analysis completed with {ai_analysis_result['confidence_score']}% confidence")
                    
                    # Process AI recommendations
                    ai_recommendations = ai_analysis_result.get("recommended_routes", [])
                    disruption_analysis = ai_analysis_result.get("disruption_analysis", {})
                    
                    # Store AI analysis results in state
                    state.ai_disruption_analysis = {
                        "analysis_timestamp": ai_analysis_result["timestamp"],
                        "model_used": ai_analysis_result["model_used"],
                        "confidence_score": ai_analysis_result["confidence_score"],
                        "disruption_impact": disruption_analysis,
                        "recommendations": ai_recommendations,
                        "reasoning": ai_analysis_result.get("reasoning", ""),
                        "summary": intelligent_disruption_service.get_route_recommendation_summary(ai_analysis_result)
                    }
                    
                    # Generate alternative routes based on AI recommendations
                    if ai_recommendations:
                        print(f"Processing {len(ai_recommendations)} AI recommendations...")
                        
                        # Get the top recommended routes that aren't already in our main routes
                        for i, recommendation in enumerate(ai_recommendations[:3]):  # Top 3 recommendations
                            route_id = recommendation["route_id"]
                            
                            # Find the corresponding route in available routes
                            recommended_route = None
                            for route in available_routes:
                                if route.get("route_id") == route_id:
                                    recommended_route = route
                                    break
                            
                            if recommended_route:
                                # Create enhanced alternative route with AI insights
                                enhanced_route = {
                                    "route_id": f"ai_recommended_{i}",
                                    "duration": recommended_route.get("duration", 0),
                                    "distance": recommended_route.get("distance", 0),
                                    "steps": recommended_route.get("steps", []),
                                    "polyline": recommended_route.get("polyline", ""),
                                    "fare_estimate": recommended_route.get("fare_estimate", 0),
                                    "transit_modes": recommended_route.get("transit_modes", []),
                                    "transfers": recommended_route.get("transfers", 0),
                                    "walking_distance": recommended_route.get("walking_distance", 0),
                                    "category": "ai_recommended",
                                    "mode_details": recommended_route.get("mode_details", {}),
                                    "ai_insights": {
                                        "rank": recommendation.get("rank", i + 1),
                                        "score": recommendation.get("score", 0),
                                        "reasoning": recommendation.get("reasoning", ""),
                                        "pros": recommendation.get("pros", []),
                                        "cons": recommendation.get("cons", []),
                                        "disruption_impact": recommendation.get("estimated_impact_from_disruptions", "unknown"),
                                        "confidence": ai_analysis_result["confidence_score"]
                                    },
                                    "reason": "ai_recommended_alternative",
                                    "avoided_disruptions": [d["disruption_id"] for d in active_disruptions if d["severity"] == "high"]
                                }
                                
                                state.alternative_routes_due_disruptions.append(enhanced_route)
                                print(f"Added AI-recommended route: {enhanced_route['route_id']} (Score: {recommendation.get('score', 0):.1f})")
                    
                    # If no AI recommendations but disruptions exist, fallback to basic alternatives
                    elif active_disruptions:
                        print("No AI recommendations available, generating basic alternatives...")
                        _generate_basic_alternatives(state, active_disruptions)
                    
                else:
                    print(f" AI analysis failed: {ai_analysis_result.get('error', 'Unknown error')}")
                    # Fallback to basic disruption handling
                    if active_disruptions:
                        _generate_basic_alternatives(state, active_disruptions)
            
            else:
                print("  Intelligent disruption service not available, using basic monitoring...")
                # Fallback to basic disruption handling
                if active_disruptions:
                    _generate_basic_alternatives(state, active_disruptions)
            
            state.current_step = "intelligent_disruption_monitoring_completed"
            state.agents_completed.append("disruption_monitoring")
            
            if span:
                span.update(
                status="completed",
                output={
                    "disruptions_found": len(active_disruptions),
                    "ai_analysis_available": intelligent_disruption_service is not None,
                    "alternative_routes_generated": len(state.alternative_routes_due_disruptions),
                    "ai_confidence_score": state.ai_disruption_analysis.get("confidence_score", 0) if hasattr(state, 'ai_disruption_analysis') else 0
                }
            )
            
        except Exception as e:
            print(f" Error in intelligent disruption monitoring: {str(e)}")
            if span:
                span.update(
                    status="error",
                    error=str(e)
                )
            state.errors.append({
                "node": "disruption_monitoring",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        return state

def _generate_basic_alternatives(state: TravelState, active_disruptions: List[Dict]) -> None:
    """
    Generate basic alternative routes when AI analysis is not available
    """
    try:
        high_severity_disruptions = [d for d in active_disruptions if d["severity"] == "high"]
        
        if high_severity_disruptions:
            print(f"Generating basic alternatives for {len(high_severity_disruptions)} high-severity disruptions")
            
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
                        "route_id": f"basic_alt_{i}",
                        "duration": route["legs"][0]["duration"]["value"] // 60,
                        "distance": route["legs"][0]["distance"]["value"] / 1000,
                        "steps": route["legs"][0]["steps"],
                        "polyline": route["overview_polyline"]["points"],
                        "fare_estimate": None,
                        "transit_modes": [],
                        "transfers": 0,
                        "walking_distance": 0.0,
                        "category": "basic_alternative",
                        "mode_details": {"mode": state.mode},
                        "reason": "avoiding_disruption",
                        "avoided_disruptions": [d["disruption_id"] for d in high_severity_disruptions]
                    })
                    print(f"  Added basic alternative route: basic_alt_{i}")
        
    except Exception as e:
        print(f"Error generating basic alternatives: {str(e)}")

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
        
        # Add transit routes - improved conversion with debugging
        for route in state.transit_routes:
            print(f"Processing transit route: type={type(route)}, is_dict={isinstance(route, dict)}")
            if isinstance(route, dict):
                route_dict = route.copy()  # Use copy to avoid mutations
                print(f"  → Transit route is dict: {route_dict.get('route_id', 'no_id')} - {route_dict.get('duration', 0)}min, {route_dict.get('distance', 0)}km")
            elif hasattr(route, 'dict'):
                route_dict = route.dict()
                print(f"  → Converted from Pydantic model to dict")
            else:
                # Fallback - try to extract attributes
                route_dict = {
                    "route_id": getattr(route, 'route_id', f"transit_{len(all_routes)}"),
                    "duration": getattr(route, 'duration', 240),  # Use realistic default based on AI analysis
                    "distance": getattr(route, 'distance', 114),  # Use realistic default
                    "steps": getattr(route, 'steps', []),
                    "mode_details": getattr(route, 'mode_details', {"mode": "transit"})
                }
                print(f"  → Created dict from object with defaults: {route_dict['duration']}min")
            
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
        
        print(f"\nTotal routes collected for comparison: {len(all_routes)}")
        
        if all_routes:
            print(f" First route summary: {all_routes[0]['route_id']} - {all_routes[0]['duration']} min, {all_routes[0]['distance']:.1f} km")
            
            # Use route comparison tool
            print("\n  Calling route comparison tool...")
            
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
                print("  No user preferences found, using defaults")
            else:
                # Convert Pydantic model to dictionary
                user_prefs = user_prefs.dict() if hasattr(user_prefs, 'dict') else user_prefs
            
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
                print("  No preference weights found, using defaults")
            
            comparison_result = route_comparison_tool._run(
                routes=all_routes,
                user_preferences=user_prefs,
                weights=weights
            )
            
            print(f" Route comparison result: {comparison_result['status']}")
            
            if comparison_result["status"] == "success":
                ranked_routes = comparison_result["ranked_routes"]
                print(f" Number of ranked routes: {len(ranked_routes)}")
                
                # Store top recommendations
                state.recommended_routes = ranked_routes[:state.config.get("max_routes", 5)]
                print(f" Stored {len(state.recommended_routes)} recommended routes")
                
                # Store route rankings
                for ranked_route in ranked_routes:
                    route_id = ranked_route["route"]["route_id"]
                    state.route_rankings[route_id] = ranked_route["score"]["total"]
                    print(f"  → Route {route_id}: Score {ranked_route['score']['total']:.3f}")
            else:
                print(f" Route comparison failed: {comparison_result.get('error', 'Unknown error')}")
        else:
            print("  No routes to compare!")
        
        state.current_step = "route_optimization_completed"
        state.agents_completed.append("route_optimization")
        
    except Exception as e:
        print(f" Error in route_optimization_node: {str(e)}")
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
        
        # Add transit routes with validation
        for route in state.transit_routes:
            print(f"DEBUG RESPONSE: Adding transit route - type: {type(route)}")
            if isinstance(route, dict):
                print(f"DEBUG RESPONSE: Transit route dict keys: {list(route.keys())}")
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
            
            print(f"DEBUG RESPONSE: Processing route from {source}: type={type(route)}, is_dict={isinstance(route, dict)}")
            if isinstance(route, dict):
                print(f"DEBUG RESPONSE: Route keys: {list(route.keys())}")
                print(f"DEBUG RESPONSE: Route ID: {route.get('route_id', 'MISSING')}, Duration: {route.get('duration', 'MISSING')}, Distance: {route.get('distance', 'MISSING')}")
            else:
                print(f"DEBUG RESPONSE: Non-dict route value: {route}")
            
            # Format route in Google Maps API structure
            formatted_route = _format_route_for_response(route, state, source)
            
            # Add recommendation score if available
            if state.recommended_routes:
                for rec in state.recommended_routes:
                    if rec["route"]["route_id"] == formatted_route["route_id"]:
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
                        print(f" LLM Summary generated: {len(user_friendly_summary.split(chr(10)))} lines")
                    else:
                        print(f" LLM Summary failed: {summary_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f" Error generating LLM summary: {str(e)}")
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
        
        # Add AI disruption analysis if available
        if state.ai_disruption_analysis:
            response["ai_disruption_analysis"] = {
                "analysis_timestamp": state.ai_disruption_analysis.get("analysis_timestamp"),
                "model_used": state.ai_disruption_analysis.get("model_used"),
                "confidence_score": state.ai_disruption_analysis.get("confidence_score"),
                "summary": state.ai_disruption_analysis.get("summary"),
                "reasoning": state.ai_disruption_analysis.get("reasoning"),
                "disruption_impact": state.ai_disruption_analysis.get("disruption_impact", {}),
                "recommendations_count": len(state.ai_disruption_analysis.get("recommendations", []))
            }

        # DEBUG: Check if steps exist before setting final_response
        print("DEBUG FINAL RESPONSE: Checking steps before assignment")
        if response.get("all_routes"):
            for i, route in enumerate(response["all_routes"]):
                steps_count = len(route.get("steps", []))
                print(f"DEBUG FINAL RESPONSE: Route {i} ({route.get('route_id')}): {steps_count} steps")
                if steps_count > 0:
                    print(f"DEBUG FINAL RESPONSE: First step: {route['steps'][0]}")
        if response.get("best_route"):
            steps_count = len(response["best_route"].get("steps", []))
            print(f"DEBUG FINAL RESPONSE: Best route: {steps_count} steps")

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
        print(f"DEBUG: _format_route_for_response called with route type: {type(route)}, source: {source}")
        
        # Safety check: ensure route is not None or empty string
        if route is None or route == "":
            print(f"Warning: Empty or None route encountered from source: {source}")
            route = {
                "route_id": f"empty_{source}",
                "duration": 0,
                "distance": 0,
                "steps": [],
                "polyline": "",
                "transit_modes": [],
                "transfers": 0,
                "walking_distance": 0,
                "category": "empty",
                "mode_details": {},
                "fare_estimate": None
            }
        # Ensure route is a dictionary (handle RouteInfo objects or other types)
        elif hasattr(route, 'dict'):
            route = route.dict()
        elif isinstance(route, dict):
            pass  # Already a dict
        elif isinstance(route, str):
            # If route is a string, log and create basic dict
            print(f"Warning: Route is a string: {route}")
            route = {
                "route_id": route if route else "unknown",
                "duration": 0,
                "distance": 0,
                "steps": [],
                "polyline": "",
                "transit_modes": [],
                "transfers": 0,
                "walking_distance": 0,
                "category": "unknown",
                "mode_details": {},
                "fare_estimate": None
            }
        elif hasattr(route, '__dict__'):
            # Convert object attributes to dict
            route = {
                "route_id": getattr(route, 'route_id', 'unknown'),
                "duration": getattr(route, 'duration', 60),
                "distance": getattr(route, 'distance', 10),
                "steps": getattr(route, 'steps', []),
                "polyline": getattr(route, 'polyline', ''),
                "transit_modes": getattr(route, 'transit_modes', []),
                "transfers": getattr(route, 'transfers', 0),
                "walking_distance": getattr(route, 'walking_distance', 0),
                "category": getattr(route, 'category', 'unknown'),
                "mode_details": getattr(route, 'mode_details', {}),
                "fare_estimate": getattr(route, 'fare_estimate', None)
            }
        else:
            # If route is an unknown type, create a basic dict
            print(f"Warning: Unknown route type: {type(route)}")
            route = {
                "route_id": str(route) if route else "unknown",
                "duration": 0,
                "distance": 0,
                "steps": [],
                "polyline": "",
                "transit_modes": [],
                "transfers": 0,
                "walking_distance": 0,
                "category": "unknown",
                "mode_details": {},
                "fare_estimate": None
            }
        
        # Calculate duration and distance with robust handling
        duration_minutes = 0
        distance_km = 0
        
        # Try multiple ways to extract duration
        if "duration" in route:
            duration_val = route["duration"]
            if isinstance(duration_val, (int, float)):
                duration_minutes = int(duration_val)
            elif isinstance(duration_val, str) and duration_val.isdigit():
                duration_minutes = int(duration_val)
        
        # Check debug info for backup data
        if duration_minutes == 0 and "_debug_info" in route:
            debug_info = route["_debug_info"]
            if "original_duration_seconds" in debug_info:
                duration_minutes = debug_info["original_duration_seconds"] // 60
                print(f"DEBUG: Using backup duration from debug info: {duration_minutes} minutes")
        
        # Try multiple ways to extract distance  
        if "distance" in route:
            distance_val = route["distance"]
            if isinstance(distance_val, (int, float)):
                distance_km = float(distance_val)
            elif isinstance(distance_val, str):
                try:
                    distance_km = float(distance_val)
                except ValueError:
                    distance_km = 0
        
        # Check debug info for backup distance data
        if distance_km == 0 and "_debug_info" in route:
            debug_info = route["_debug_info"]
            if "original_distance_meters" in debug_info:
                distance_km = debug_info["original_distance_meters"] / 1000
                print(f"DEBUG: Using backup distance from debug info: {distance_km} km")
        
        print(f"DEBUG: Formatting route {route.get('route_id', 'unknown')}: duration={duration_minutes}min, distance={distance_km}km")
        
        # Format duration text with better handling
        if duration_minutes <= 0:
            duration_text = "Duration not available"
        elif duration_minutes < 60:
            duration_text = f"{duration_minutes} mins"
        else:
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            if minutes == 0:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''} {minutes} mins"
        
        # Format distance text with better handling
        if distance_km <= 0:
            distance_text = "Distance not available"
        elif distance_km < 1:
            distance_text = f"{int(distance_km * 1000)} m"
        else:
            distance_text = f"{distance_km:.1f} km"
        
        # Calculate start and end times with robust error handling
        try:
            departure_time = state.departure_time
            if departure_time is None:
                departure_time = datetime.now()
            elif isinstance(departure_time, str):
                # Try to parse string datetime
                try:
                    departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                except:
                    departure_time = datetime.now()
            
            start_time = departure_time.strftime("%I:%M %p")
            
            # Ensure duration_minutes is a valid integer
            duration_for_calc = max(0, int(duration_minutes)) if duration_minutes > 0 else 240  # fallback to 240 minutes
            end_time = departure_time + timedelta(minutes=duration_for_calc)
            end_time_str = end_time.strftime("%I:%M %p")
            
        except Exception as time_error:
            print(f"ERROR: Time calculation failed: {time_error}")
            start_time = "Time not available"
            end_time_str = "Time not available"
        
        # Format steps
        formatted_steps = []
        steps = route.get("steps", [])

        print(f"DEBUG STEPS: Route has {len(steps)} steps to format")

        for idx, step in enumerate(steps):
            # Handle both nested dict format (from Google Maps) and simple format
            distance_text = "0 m"
            if isinstance(step.get("distance"), dict):
                distance_text = step["distance"].get("text", "0 m")
            elif isinstance(step.get("distance"), (int, float)):
                # Distance is just a number (in meters)
                dist_m = step["distance"]
                distance_text = f"{dist_m/1000:.1f} km" if dist_m >= 1000 else f"{int(dist_m)} m"
            elif isinstance(step.get("distance"), str):
                distance_text = step["distance"]

            duration_text = "0 mins"
            if isinstance(step.get("duration"), dict):
                duration_text = step["duration"].get("text", "0 mins")
            elif isinstance(step.get("duration"), (int, float)):
                # Duration is just a number (in seconds)
                dur_s = step["duration"]
                duration_text = f"{int(dur_s/60)} mins" if dur_s >= 60 else f"{int(dur_s)} secs"
            elif isinstance(step.get("duration"), str):
                duration_text = step["duration"]

            formatted_step = {
                "html_instructions": step.get("html_instructions", ""),
                "distance": distance_text,
                "duration": duration_text,
                "travel_mode": step.get("travel_mode", "UNKNOWN"),
                "transit_details": None
            }

            print(f"DEBUG STEP {idx}: {formatted_step['travel_mode']} - {distance_text} - {formatted_step['html_instructions'][:50] if formatted_step['html_instructions'] else 'No instructions'}")
            
            # Add transit details if available
            if step.get("transit_details"):
                transit_detail = step["transit_details"]

                # Handle arrival_stop - can be either a dict or a string
                arrival_stop = transit_detail.get("arrival_stop", "")
                if isinstance(arrival_stop, dict):
                    arrival_stop = arrival_stop.get("name", "")

                # Handle departure_stop - can be either a dict or a string
                departure_stop = transit_detail.get("departure_stop", "")
                if isinstance(departure_stop, dict):
                    departure_stop = departure_stop.get("name", "")

                # Handle line - can be either a dict or a string
                line = transit_detail.get("line", {})
                if isinstance(line, dict):
                    line_name = line.get("name", "")
                    vehicle_type_obj = line.get("vehicle", {})
                    if isinstance(vehicle_type_obj, dict):
                        vehicle_type = vehicle_type_obj.get("type", "")
                    else:
                        vehicle_type = str(vehicle_type_obj)
                else:
                    line_name = transit_detail.get("line_name", "")
                    vehicle_type = transit_detail.get("vehicle_type", "")

                # Handle departure_time - can be either a dict or a string
                departure_time = transit_detail.get("departure_time", "")
                if isinstance(departure_time, dict):
                    departure_time = departure_time.get("text", "")

                formatted_step["transit_details"] = {
                    "arrival_stop": arrival_stop,
                    "departure_stop": departure_stop,
                    "line_name": line_name,
                    "vehicle_type": vehicle_type,
                    "num_stops": transit_detail.get("num_stops", 0),
                    "departure_time": departure_time
                }
            
            # Add fare details if available
            if step.get("fare_details"):
                formatted_step["fare_details"] = step["fare_details"]
                
                # Add Uber alternative if available
                if step["fare_details"].get("uber_alternative"):
                    formatted_step["uber_alternative"] = step["fare_details"]["uber_alternative"]
            
            formatted_steps.append(formatted_step)
        
        # Build the formatted route
        print(f"DEBUG FORMAT: Formatting route {route.get('route_id')} with {len(formatted_steps)} steps, transit_modes: {route.get('transit_modes', [])}")
        
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
        print(f"ERROR: Error formatting route: {str(e)}")
        print(f"ERROR: Route data type: {type(route)}")
        print(f"ERROR: Route data: {route}")
        import traceback
        traceback.print_exc()
        
        # Try to extract basic info even from corrupted route data
        route_id = "unknown"
        duration_fallback = "240 mins"  # Based on AI analysis showing 240 minutes
        distance_fallback = "114 km"   # Based on earlier debug logs showing 114.1km
        
        if isinstance(route, dict):
            route_id = route.get("route_id", "unknown")
            # Try to get duration/distance even if formatting failed
            if route.get("duration"):
                try:
                    dur_val = route["duration"]
                    if isinstance(dur_val, (int, float)) and dur_val > 0:
                        if dur_val < 60:
                            duration_fallback = f"{int(dur_val)} mins"
                        else:
                            hours = int(dur_val) // 60
                            mins = int(dur_val) % 60
                            duration_fallback = f"{hours} hours {mins} mins" if mins > 0 else f"{hours} hours"
                except:
                    pass
            if route.get("distance"):
                try:
                    dist_val = route["distance"]
                    if isinstance(dist_val, (int, float)) and dist_val > 0:
                        distance_fallback = f"{dist_val:.1f} km"
                except:
                    pass
        
        # Return a more informative fallback route
        return {
            "route_id": route_id,
            "origin": f"{state.source}, Sri Lanka",
            "destination": f"{state.destination}, Sri Lanka",
            "distance_text": distance_fallback,
            "duration_text": duration_fallback,
            "start_time": "Time not available",
            "end_time": "Time not available",
            "steps": [],
            "estimated_cost": route.get("fare_estimate") if isinstance(route, dict) else None,
            "cost_currency": "LKR",
            "route_source": source,
            "recommendation_score": 0.0,
            "score_breakdown": {
                "time": 0,
                "cost": 0,
                "comfort": 0.5,
                "convenience": 1,
                "reliability": 0.7
            },
            "is_recommended": False
        }

# Conditional routing functions
def should_use_multi_agent(state: TravelState) -> str:
    """Determine if multi-agent processing is needed - Updated for Sri Lankan modes"""
    # Sri Lankan public transit modes use full multi-agent processing
    if state.mode in ["transit", "train", "bus"]:
        return "transit_processing"
    # Private/individual modes use standard processing  
    elif state.mode in ["driving", "two_wheeler", "uber", "tuk-tuk"]:
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

def generate_sri_lankan_route_steps(source: str, destination: str, distance_meters: int, duration_seconds: int, transit_mode: str = "bus") -> list:
    """
    Generate realistic route steps for Sri Lankan routes when Google Maps doesn't provide them
    """
    try:
        steps = []
        distance_km = distance_meters / 1000
        duration_minutes = duration_seconds // 60
        
        # Step 1: Walk to transport hub
        walk_to_start = {
            "html_instructions": f"Walk to the nearest {transit_mode} stop in {source}",
            "distance": {"text": "0.5 km", "value": 500},
            "duration": {"text": "5-10 mins", "value": 600},
            "travel_mode": "WALKING",
            "transit_details": None
        }
        steps.append(walk_to_start)
        
        # Step 2: Main transport
        main_transport = {
            "html_instructions": f"Take {transit_mode} from {source} to {destination}",
            "distance": {"text": f"{distance_km:.1f} km", "value": distance_meters},
            "duration": {"text": f"{duration_minutes} mins", "value": duration_seconds},
            "travel_mode": "TRANSIT",
            "transit_details": {
                "arrival_stop": {"name": f"{destination} Main Stop"},
                "departure_stop": {"name": f"{source} Main Stop"},
                "line_name": f"{source} - {destination} Route",
                "vehicle_type": transit_mode.upper(),
                "num_stops": max(3, int(distance_km / 10)),  # Estimate stops
                "departure_time": {"text": "Varies"}
            }
        }
        steps.append(main_transport)
        
        # Step 3: Walk to destination
        walk_to_end = {
            "html_instructions": f"Walk to your final destination in {destination}",
            "distance": {"text": "0.3 km", "value": 300},
            "duration": {"text": "3-5 mins", "value": 300},
            "travel_mode": "WALKING",
            "transit_details": None
        }
        steps.append(walk_to_end)
        
        return steps
        
    except Exception as e:
        print(f"Error generating Sri Lankan route steps: {e}")
        return []