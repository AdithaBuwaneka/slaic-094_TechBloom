import googlemaps
from datetime import datetime
from typing import List
from app.core.config import settings
from app.models.transport import RouteOption, JourneyLeg, Location

class GoogleMapsService:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def get_directions(self, origin: str, destination: str, mode: str = "transit") -> List[RouteOption]:
        """
        Fetches directions from Google Maps API and restricts them to Sri Lanka.
        """
        try:
            directions_result = self.gmaps.directions(
                origin,
                destination,
                mode=mode,
                departure_time=datetime.now(),
                # Bias results to Sri Lanka using region ccTLD
                region="lk"
            )

            if not directions_result:
                return []

            parsed_routes: List[RouteOption] = []
            for route in directions_result:
                route_legs: List[JourneyLeg] = []
                total_distance_meters = 0
                total_duration_seconds = 0
                
                # The main route summary (e.g., "Via A4")
                route_summary = route.get('summary', '')

                for leg in route['legs']:
                    total_distance_meters += leg['distance']['value']
                    total_duration_seconds += leg['duration']['value']

                    # Each 'leg' can have multiple 'steps' (e.g., walk to station, take train)
                    for step in leg['steps']:
                        journey_leg = JourneyLeg(
                            distance=step['distance']['text'],
                            duration=step['duration']['text'],
                            summary=step['html_instructions'],
                            start_location=Location(
                                address="", # API doesn't provide address for each step
                                lat=step['start_location']['lat'],
                                lng=step['start_location']['lng']
                            ),
                            end_location=Location(
                                address="", # API doesn't provide address for each step
                                lat=step['end_location']['lat'],
                                lng=step['end_location']['lng']
                            ),
                            travel_mode=step['travel_mode']
                        )
                        route_legs.append(journey_leg)

                # Convert total distance and duration to text
                total_distance_km = f"{total_distance_meters / 1000:.1f} km"
                total_duration_text = f"{total_duration_seconds // 3600}h {(total_duration_seconds % 3600) // 60}m"


                parsed_routes.append(
                    RouteOption(
                        total_duration=total_duration_text,
                        total_distance=total_distance_km,
                        legs=route_legs,
                        summary=route_summary
                    )
                )
            
            return parsed_routes

        except Exception as e:
            print(f"An error occurred with Google Maps API: {e}")
            return []