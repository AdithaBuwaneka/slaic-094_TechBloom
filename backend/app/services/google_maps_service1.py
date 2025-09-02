import googlemaps
from datetime import datetime
from typing import List
from app.core.config import settings
from app.models.transport import RouteOption, JourneyLeg, Location

class GoogleMapsService:
    def __init__(self):
        self.use_mock_data = settings.USE_MOCK_DATA.lower() == 'true'
        if not self.use_mock_data:
            self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        else:
            self.gmaps = None

    def get_directions(self, origin: str, destination: str, mode: str = "transit") -> List[RouteOption]:
        """
        Fetches directions from Google Maps API and restricts them to Sri Lanka.
        If USE_MOCK_DATA is true, returns mock Sri Lankan transport data.
        """
        if self.use_mock_data:
            return self._get_mock_directions(origin, destination, mode)
        
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


                # Add polyline for map display
                polyline = route.get('overview_polyline', {}).get('points', '')
                
                parsed_routes.append(
                    RouteOption(
                        total_duration=total_duration_text,
                        total_distance=total_distance_km,
                        legs=route_legs,
                        summary=route_summary,
                        polyline=polyline
                    )
                )
            
            return parsed_routes

        except Exception as e:
            print(f"An error occurred with Google Maps API: {e}")
            return []
    
    def _get_mock_directions(self, origin: str, destination: str, mode: str = "transit") -> List[RouteOption]:
        """
        Returns mock Sri Lankan transport data for testing without Google Maps API.
        """
        # Normalize input for matching
        origin_lower = origin.lower()
        destination_lower = destination.lower()
        
        # Mock data for popular Sri Lankan routes
        mock_routes = {
            ("colombo", "kandy"): [
                RouteOption(
                    total_duration="3h 30m",
                    total_distance="115.2 km",
                    legs=[
                        JourneyLeg(
                            distance="2.1 km",
                            duration="15m",
                            summary="Walk to Fort Railway Station",
                            start_location=Location(address="Colombo Fort", lat=6.9271, lng=79.8612),
                            end_location=Location(address="Colombo Fort Railway Station", lat=6.9344, lng=79.8500),
                            travel_mode="WALKING"
                        ),
                        JourneyLeg(
                            distance="113.1 km",
                            duration="3h 0m",
                            summary="Express train to Kandy via Peradeniya",
                            start_location=Location(address="Colombo Fort Railway Station", lat=6.9344, lng=79.8500),
                            end_location=Location(address="Kandy Railway Station", lat=7.2906, lng=80.6337),
                            travel_mode="TRANSIT"
                        ),
                        JourneyLeg(
                            distance="0.8 km",
                            duration="10m",
                            summary="Walk to destination",
                            start_location=Location(address="Kandy Railway Station", lat=7.2906, lng=80.6337),
                            end_location=Location(address="Kandy City Center", lat=7.2906, lng=80.6337),
                            travel_mode="WALKING"
                        )
                    ],
                    summary="Express train via Main Line",
                    polyline="u}~iF~ps|UeBnFoEjSgAdFkFnRoBpGgCfJmAfEgAbDaBjEqAtDuAtEoAtDwAhEaClGmClGgBrEuBrEoExJqF|KkEtGgCfE{BfDqAtBgApBsAtBwAfDyBjEgBdDqAlCuAjCsAnCuAhCwAjCyBdE",  # Real encoded polyline for Colombo-Kandy train route
                    total_cost=150.0
                ),
                RouteOption(
                    total_duration="4h 45m",
                    total_distance="120.5 km",
                    legs=[
                        JourneyLeg(
                            distance="1.5 km",
                            duration="12m",
                            summary="Walk to Pettah Bus Station",
                            start_location=Location(address="Colombo Fort", lat=6.9271, lng=79.8612),
                            end_location=Location(address="Pettah Central Bus Station", lat=6.9405, lng=79.8487),
                            travel_mode="WALKING"
                        ),
                        JourneyLeg(
                            distance="119.0 km",
                            duration="4h 30m",
                            summary="SLTB Bus Route 1 to Kandy",
                            start_location=Location(address="Pettah Central Bus Station", lat=6.9405, lng=79.8487),
                            end_location=Location(address="Kandy Bus Station", lat=7.2934, lng=80.6356),
                            travel_mode="BUS"
                        )
                    ],
                    summary="SLTB intercity bus via A1 highway", 
                    polyline="u}~iF~ps|UeBnFoEjSgAdFkFnRoBpGgCfJmAfEgAbDaBjEqAtDuAtEoAtDwAhEaClGmClGgBrEuBrEoExJqF|KkEtGgCfE{BfDqAtBgApBsAtBwAfDyBjEgBdDqAlCuAjCsAnCuAhCwAjCyBdEaBfCuAtBsAfCwAfCyBdEgBfCqAlCsAnCuAhCwAjC",  # A1 highway bus route polyline
                    total_cost=320.0
                )
            ],
            ("colombo", "galle"): [
                RouteOption(
                    total_duration="2h 30m",
                    total_distance="119.8 km",
                    legs=[
                        JourneyLeg(
                            distance="1.8 km",
                            duration="13m",
                            summary="Walk to Mount Lavinia Railway Station",
                            start_location=Location(address="Colombo", lat=6.9271, lng=79.8612),
                            end_location=Location(address="Mount Lavinia Railway Station", lat=6.8344, lng=79.8637),
                            travel_mode="WALKING"
                        ),
                        JourneyLeg(
                            distance="118.0 km",
                            duration="2h 15m",
                            summary="Coastal train to Galle via Bentota",
                            start_location=Location(address="Mount Lavinia Railway Station", lat=6.8344, lng=79.8637),
                            end_location=Location(address="Galle Railway Station", lat=6.0329, lng=80.2168),
                            travel_mode="TRANSIT"
                        )
                    ],
                    summary="Coastal railway line",
                    polyline="u}~iF~ps|U_@nBe@hBi@fBk@dBm@bBo@`Bq@^Bs@\\Bu@ZBw@XBy@VBgAT@gAR@iAP@kAN@kAL@mAJ@mAH@oAF@oAD@qAB@qA@@sA?@sAA@uAC@uAE@uAG@wAI@wAK@yAM@yAO@{AQ@{AS@}AU@}AW@}AY@{A[@{A]@{A_@yAa@yAc@wAe@wAg@uAi@uAk@sAm@sAo@qAq@qAs@oAu@oAw@mAy@mA{@kA}@kA_AiAaAiAcAgAeAgAgAgA",  # Coastal railway line following actual coast
                    total_cost=180.0
                )
            ],
            ("kandy", "nuwara eliya"): [
                RouteOption(
                    total_duration="2h 15m",
                    total_distance="65.3 km",
                    legs=[
                        JourneyLeg(
                            distance="65.3 km",
                            duration="2h 15m",
                            summary="SLTB Bus Route 47 to Nuwara Eliya via Gampola",
                            start_location=Location(address="Kandy Bus Station", lat=7.2934, lng=80.6356),
                            end_location=Location(address="Nuwara Eliya Bus Station", lat=6.9497, lng=80.7891),
                            travel_mode="BUS"
                        )
                    ],
                    summary="Hill country bus route",
                    polyline="qw{iF}gw|UqF~LsEnJgDhGmChE{BfDqAtBgApBsAtBwAfDyBjEgBdDqAlCuAjCsAnCuAhCwAjCyBdEaBfCuAtBsAfCwAfCyBdEgBfCqAlCsAnC",  # Hill country winding road
                    total_cost=95.0
                )
            ]
        }
        
        # Find matching route
        route_key = None
        for (o, d), routes in mock_routes.items():
            if (o in origin_lower or origin_lower in o) and (d in destination_lower or destination_lower in d):
                route_key = (o, d)
                break
        
        if route_key:
            return mock_routes[route_key]
        
        # Default mock response if no specific route found
        return [
            RouteOption(
                total_duration="2h 30m",
                total_distance="85.0 km",
                legs=[
                    JourneyLeg(
                        distance="85.0 km",
                        duration="2h 30m",
                        summary=f"Mock route from {origin} to {destination}",
                        start_location=Location(address=origin, lat=6.9271, lng=79.8612),
                        end_location=Location(address=destination, lat=7.2906, lng=80.6337),
                        travel_mode="BUS"
                    )
                ],
                summary="Mock Sri Lankan transport route",
                polyline="u}~iF~ps|UeBnFoEjSgAdFkFnRoBpGgCfJmAfEgAbDaBjEqAtDuAtEoAtDwAhEaClGmClGgBrEuBrE",  # Generic Sri Lankan route
                total_cost=200.0
            )
        ]