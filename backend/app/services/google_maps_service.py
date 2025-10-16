import requests
import os
from dotenv import load_dotenv
from typing import List, Optional
import json

load_dotenv()

API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
# Updated to use Routes API v2
BASE_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

def get_optimized_route(origin: str, destination: str, mode: str, departure_time: int, transit_mode_preference: Optional[str] = None):
    """
    Fetches the complete, optimized route from the Google Routes API v2
    for a specified travel mode.
    """

    # Map travel modes to Routes API format
    travel_mode_mapping = {
        "driving": "DRIVE",
        "three_wheeler": "DRIVE",  # Map tuk-tuk to driving
        "motorcycle": "DRIVE",    # Map motorcycle to driving
        "transit": "TRANSIT",
        "walking": "WALK",
        "bicycling": "BICYCLE"
    }
    
    api_mode = travel_mode_mapping.get(mode, "DRIVE")

    # Routes API v2 uses JSON payload instead of query parameters
    request_payload = {
        "origin": {
            "address": f"{origin}, Sri Lanka"
        },
        "destination": {
            "address": f"{destination}, Sri Lanka"
        },
        "travelMode": api_mode,
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False
        },
        "languageCode": "en-US",
        "units": "IMPERIAL"
    }
    
    # Only add routing preference for non-transit modes
    if api_mode != "TRANSIT":
        request_payload["routingPreference"] = "TRAFFIC_AWARE"

    # Add departure time if provided
    if departure_time:
        from datetime import datetime
        # Convert timestamp to proper ISO format with 'Z' suffix
        if isinstance(departure_time, (int, float)):
            dt = datetime.fromtimestamp(departure_time)
            request_payload["departureTime"] = dt.isoformat() + "Z"
        else:
            request_payload["departureTime"] = f"{departure_time}Z" if not str(departure_time).endswith('Z') else str(departure_time)

    # Add transit preferences
    if api_mode == "TRANSIT" and transit_mode_preference:
        transit_modes = []
        if transit_mode_preference.lower() == "bus":
            transit_modes = ["BUS"]
        elif transit_mode_preference.lower() == "train":
            transit_modes = ["RAIL"]
        
        if transit_modes:
            request_payload["transitPreferences"] = {
                "allowedTravelModes": transit_modes
            }

    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline,routes.legs,routes.legs.steps,routes.legs.steps.navigationInstruction,routes.legs.steps.localizedValues,routes.legs.steps.transitDetails,routes.legs.steps.travelMode'
    }

    try:
        response = requests.post(BASE_URL, 
                               headers=headers, 
                               data=json.dumps(request_payload))
        response.raise_for_status()
        data = response.json()

        if 'routes' in data and len(data['routes']) > 0:
            route = data['routes'][0]
            leg = route['legs'][0] if 'legs' in route and len(route['legs']) > 0 else {}
            
            steps = []
            if 'steps' in leg:
                for step in leg['steps']:
                    step_data = {
                        "html_instructions": step.get('navigationInstruction', {}).get('instructions', 'Continue'),
                        "distance": step.get('localizedValues', {}).get('distance', {}).get('text', 'N/A'),
                        "duration": step.get('localizedValues', {}).get('staticDuration', {}).get('text', 'N/A'),
                        "travel_mode": step.get('travelMode', 'UNKNOWN'),
                        "transit_details": None
                    }
                    
                    # Parse transit details if available
                    if 'transitDetails' in step:
                        td = step['transitDetails']
                        step_data["transit_details"] = {
                            "arrival_stop": td.get('stopDetails', {}).get('arrivalStop', {}).get('name', 'N/A'),
                            "departure_stop": td.get('stopDetails', {}).get('departureStop', {}).get('name', 'N/A'),
                            "line_name": td.get('transitLine', {}).get('name', 'N/A'),
                            "vehicle_type": td.get('transitLine', {}).get('vehicle', {}).get('name', {}).get('text', 'N/A'),
                            "num_stops": td.get('stopCount', 0),
                            "departure_time": td.get('localizedValues', {}).get('departureTime', {}).get('text')
                        }
                    steps.append(step_data)

            # Calculate basic route info
            distance_meters = route.get('distanceMeters', 0)
            distance_km = distance_meters / 1000

            # Parse duration from "8432s" format to seconds as integer
            duration_str = route.get('duration', '0s')
            duration_seconds = int(duration_str.replace('s', '')) if duration_str.endswith('s') else 0

            # Format duration for display
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            if hours > 0:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''} {minutes} min{'s' if minutes != 1 else ''}"
            else:
                duration_text = f"{minutes} min{'s' if minutes != 1 else ''}"

            result = {
                "origin": f"{origin}, Sri Lanka",
                "destination": f"{destination}, Sri Lanka",
                "distance_text": f"{distance_km:.1f} km",
                "distance_meters": distance_meters,  # Raw numeric value
                "duration_text": duration_text,
                "duration_seconds": duration_seconds,  # Raw numeric value
                "start_time": None,
                "end_time": None,
                "steps": steps
            }
            return result, None
        else:
            error_message = f"No routes found for mode '{mode}' from {origin} to {destination}"
            return None, error_message

    except requests.exceptions.RequestException as e:
        print(f"Google Routes API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
                print(f"API Error Details: {error_msg}")
                return None, f"Google Routes API error: {error_msg}"
            except:
                pass
        return None, f"Google Routes API communication error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, f"Unexpected error processing route: {str(e)}"