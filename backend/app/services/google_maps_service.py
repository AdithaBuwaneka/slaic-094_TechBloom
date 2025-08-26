import requests
import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

def get_optimized_route(origin: str, destination: str, mode: str, departure_time: int, transit_mode_preference: Optional[str] = None):
    """
    Fetches the complete, optimized route from the Google Maps Directions API
    for a specified travel mode.
    """

    api_mode = mode
    if mode == "three_wheeler":
        api_mode = "driving" # Map tuk-tuk requests to the driving mode

    params = {
        'origin': f"{origin}, Sri Lanka",
        'destination': f"{destination}, Sri Lanka",
        'mode': api_mode, # Pass the selected travel mode
        'departure_time': departure_time,
        'key': API_KEY
    }
    # If the mode is transit and a preference is set, add it
    if api_mode == 'transit' and transit_mode_preference:
        params['transit_mode'] = transit_mode_preference # This tells Google to prefer train or bus

    # Google's 'motorcycle' mode is not available in all regions. 
    # The API will gracefully fall back to 'driving' if it's not supported.
    if mode == "motorcycle":
        params['mode'] = 'driving' # Fallback for now, but API might support it

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK':
            route = data['routes'][0]['legs'][0]
            
            steps = []
            for step in route['steps']:
                step_data = {
                    "html_instructions": step['html_instructions'],
                    "distance": step['distance']['text'],
                    "duration": step['duration']['text'],
                    "travel_mode": step['travel_mode'],
                    "transit_details": None
                }
                
                # If the step is public transit, parse the extra details
                if step['travel_mode'] == 'TRANSIT' and 'transit_details' in step:
                    td = step['transit_details']
                    step_data["transit_details"] = {
                        "arrival_stop": td['arrival_stop']['name'],
                        "departure_stop": td['departure_stop']['name'],
                        "line_name": td['line']['name'] if 'name' in td['line'] else td['line'].get('short_name', 'N/A'),
                        "vehicle_type": td['line']['vehicle']['name'],
                        "num_stops": td['num_stops'],
                        "departure_time": td.get('departure_time', {}).get('text') if 'departure_time' in td else None
                    }
                steps.append(step_data)

            result = {
                "origin": route['start_address'],
                "destination": route['end_address'],
                "distance_text": route['distance']['text'],
                "duration_text": route['duration']['text'],
                "start_time": route.get('departure_time', {}).get('text'),
                "end_time": route.get('arrival_time', {}).get('text'),
                "steps": steps
            }
            return result, None
        else:
            error_message = data.get('error_message', f"Could not find a route for mode '{mode}'. Status: {data['status']}")
            return None, error_message

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None, "An error occurred while communicating with the Google Maps API."