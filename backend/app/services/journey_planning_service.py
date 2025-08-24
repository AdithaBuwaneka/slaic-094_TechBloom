from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

from app.models.journey_planning import (
    JourneyPlanRequest, JourneyPlanResponse, Journey, JourneyLeg, 
    TransferDetails, BookingRequest, BookingResponse, TripManagement,
    MultiStopJourneyRequest, JourneySearchFilters, JourneyAnalytics,
    JourneyType, TravelTime, JourneyPriority, BookingStatus
)
from app.models.transport_data import Location, TransportMode, TransportOperator
from app.agents.agent_manager import AgentManager


class JourneyPlanningService:
    def __init__(self):
        self.agent_manager = AgentManager()
        
        # Cache for frequent routes
        self.route_cache = {}
        self.cache_duration_minutes = 30
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0

    async def plan_journey(self, request: JourneyPlanRequest) -> JourneyPlanResponse:
        """Plan a comprehensive journey using all available agents"""
        start_time = datetime.utcnow()
        
        try:
            # Increment request counter
            self.request_count += 1
            
            # Step 1: Get user preferences if user_id provided
            user_preferences = None
            if request.user_id:
                user_preferences = await self._get_user_preferences(request.user_id)
            
            # Step 2: Get route optimization options
            route_options = await self._get_optimized_routes(request)
            
            # Step 3: Apply personalization
            if user_preferences:
                route_options = await self._apply_personalization(route_options, user_preferences, request)
            
            # Step 4: Calculate fares for each route
            route_options = await self._calculate_fares(route_options, request)
            
            # Step 5: Check accessibility requirements
            if request.accessibility_requirements or request.requires_wheelchair_access:
                route_options = await self._filter_accessibility(route_options, request)
            
            # Step 6: Check for disruptions
            route_options = await self._check_disruptions(route_options)
            
            # Step 7: Get local knowledge insights
            local_insights = await self._get_local_insights(request)
            
            # Step 8: Rank and select best routes
            ranked_routes = await self._rank_routes(route_options, request)
            
            # Step 9: Convert to Journey objects
            journeys = await self._convert_to_journeys(ranked_routes, request)
            
            # Step 10: Select recommended journey and alternatives
            recommended_journey = journeys[0] if journeys else None
            alternative_journeys = journeys[1:request.max_alternatives] if len(journeys) > 1 else []
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.total_processing_time += processing_time
            
            return JourneyPlanResponse(
                success=True,
                message="Journey plan generated successfully",
                processing_time_ms=int(processing_time),
                recommended_journey=recommended_journey,
                alternative_journeys=alternative_journeys,
                total_journeys_found=len(journeys),
                original_request=request,
                personalization_applied=user_preferences is not None,
                data_sources_used=["route_optimization", "fare_optimization", "accessibility", "disruption_management"],
                real_time_coverage=0.85,
                travel_tips=local_insights.get("travel_tips", []),
                local_insights=local_insights.get("cultural_insights", [])
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return JourneyPlanResponse(
                success=False,
                message=f"Journey planning failed: {str(e)}",
                processing_time_ms=int(processing_time),
                original_request=request,
                total_journeys_found=0,
                journey_warnings=[f"Error occurred during planning: {str(e)}"]
            )

    async def plan_multi_stop_journey(self, request: MultiStopJourneyRequest) -> JourneyPlanResponse:
        """Plan multi-stop journey with waypoint optimization"""
        try:
            waypoints = request.waypoints
            
            # Optimize waypoint order if requested
            if request.optimize_order and len(waypoints) > 3:
                waypoints = await self._optimize_waypoint_order(waypoints)
            
            # Plan journey for each segment
            journey_segments = []
            total_duration = 0
            
            for i in range(len(waypoints) - 1):
                # Handle both Pydantic model and dict for travel_preferences
                if hasattr(request.travel_preferences, 'model_dump'):
                    prefs_dict = request.travel_preferences.model_dump(exclude={'origin', 'destination', 'journey_type'})
                else:
                    prefs_dict = {k: v for k, v in request.travel_preferences.items() 
                                 if k not in ['origin', 'destination', 'journey_type']}
                
                segment_request = JourneyPlanRequest(
                    origin=waypoints[i],
                    destination=waypoints[i + 1],
                    journey_type=JourneyType.ONE_WAY,
                    **prefs_dict
                )
                
                segment_response = await self.plan_journey(segment_request)
                if segment_response.success and segment_response.recommended_journey:
                    journey_segments.append(segment_response.recommended_journey)
                    total_duration += segment_response.recommended_journey.total_duration_minutes
                else:
                    # Create a JourneyPlanRequest for the original_request field
                    if hasattr(request.travel_preferences, 'model_dump'):
                        fallback_request = request.travel_preferences
                    else:
                        fallback_request = JourneyPlanRequest(**request.travel_preferences)
                    
                    return JourneyPlanResponse(
                        success=False,
                        message=f"Failed to plan segment from {waypoints[i].name} to {waypoints[i+1].name}",
                        original_request=fallback_request,
                        total_journeys_found=0
                    )
            
            # Combine segments into a single journey
            combined_journey = await self._combine_journey_segments(journey_segments, total_duration)
            
            # Create a JourneyPlanRequest for the original_request field
            if hasattr(request.travel_preferences, 'model_dump'):
                original_request = request.travel_preferences
            else:
                original_request = JourneyPlanRequest(**request.travel_preferences)
            
            return JourneyPlanResponse(
                success=True,
                message="Multi-stop journey planned successfully",
                recommended_journey=combined_journey,
                total_journeys_found=1,
                original_request=original_request,
                system_notices=[f"Multi-stop journey with {len(waypoints)} waypoints"]
            )
            
        except Exception as e:
            # Create a JourneyPlanRequest for the original_request field
            try:
                if hasattr(request.travel_preferences, 'model_dump'):
                    original_request = request.travel_preferences
                else:
                    original_request = JourneyPlanRequest(**request.travel_preferences)
            except Exception:
                # If we can't create the original request, use a minimal fallback
                original_request = JourneyPlanRequest(
                    origin=Location(latitude=0, longitude=0, name="Unknown"),
                    destination=Location(latitude=0, longitude=0, name="Unknown")
                )
            
            return JourneyPlanResponse(
                success=False,
                message=f"Multi-stop journey planning failed: {str(e)}",
                original_request=original_request,
                total_journeys_found=0
            )

    async def book_journey(self, booking_request: BookingRequest) -> BookingResponse:
        """Book a journey for the user"""
        try:
            # Simulate booking process
            journey = await self._get_journey_by_id(booking_request.journey_id)
            if not journey:
                return BookingResponse(
                    success=False,
                    message="Journey not found",
                    booking_status="failed",
                    journey=None,
                    passenger_details={},
                    total_fare=0.0
                )
            
            # Check availability
            availability_check = await self._check_journey_availability(journey)
            if not availability_check:
                return BookingResponse(
                    success=False,
                    message="Journey no longer available",
                    booking_status="failed",
                    journey=journey,
                    passenger_details={},
                    total_fare=journey.total_fare
                )
            
            # Calculate total fare with passenger types
            total_fare = await self._calculate_booking_fare(journey, booking_request)
            
            # Generate booking confirmation
            confirmation_number = f"STC{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            qr_code_url = f"https://api.qr-server.com/v1/create-qr-code/?data={confirmation_number}&size=200x200"
            
            return BookingResponse(
                success=True,
                message="Journey booked successfully",
                booking_status="confirmed",
                journey=journey,
                passenger_details={
                    "passenger_count": booking_request.passenger_count,
                    "passenger_types": booking_request.passenger_types,
                    "contact_email": booking_request.contact_email
                },
                total_fare=total_fare,
                confirmation_number=confirmation_number,
                qr_code_url=qr_code_url,
                booking_reference=f"REF-{confirmation_number}",
                cancellation_policy="Free cancellation up to 2 hours before departure",
                check_in_requirements=["Present QR code", "Valid ID required"],
                booking_expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
        except Exception as e:
            return BookingResponse(
                success=False,
                message=f"Booking failed: {str(e)}",
                booking_status="failed",
                journey=None,
                passenger_details={},
                total_fare=0.0
            )

    async def manage_trip(self, trip_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """Manage active trips (start, update, complete, cancel)"""
        try:
            trip = await self._get_trip_by_id(trip_id)
            if not trip:
                return {"success": False, "message": "Trip not found"}
            
            if action == "get_details":
                return {
                    "success": True,
                    "message": "Trip details retrieved",
                    "trip": trip.model_dump()
                }
            
            elif action == "start":
                trip.status = "active"
                trip.started_at = datetime.utcnow()
                return {
                    "success": True,
                    "message": "Trip started",
                    "trip": trip.model_dump(),
                    "next_leg": trip.journey.legs[0].model_dump() if trip.journey.legs else None
                }
            
            elif action == "update_location":
                current_location = kwargs.get("current_location")
                # Update trip progress based on location
                return {
                    "success": True,
                    "message": "Location updated",
                    "trip_status": trip.status,
                    "estimated_arrival": trip.journey.arrival_time.isoformat()
                }
            
            elif action == "complete":
                trip.status = "completed"
                trip.completed_at = datetime.utcnow()
                return {
                    "success": True,
                    "message": "Trip completed",
                    "trip": trip.model_dump(),
                    "feedback_prompt": "How was your journey?"
                }
            
            elif action == "cancel":
                trip.status = "cancelled"
                return {
                    "success": True,
                    "message": "Trip cancelled",
                    "cancellation_policy": "Refund processed within 3-5 business days"
                }
            
            else:
                return {"success": False, "message": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "message": f"Trip management failed: {str(e)}"}

    async def search_journeys(self, filters: JourneySearchFilters) -> List[Journey]:
        """Search journeys with advanced filters"""
        try:
            # Simulate journey search with filters
            sample_journeys = await self._generate_sample_journeys()
            
            # Apply filters
            filtered_journeys = []
            for journey in sample_journeys:
                if self._journey_matches_filters(journey, filters):
                    filtered_journeys.append(journey)
            
            return filtered_journeys[:10]  # Limit to 10 results
            
        except Exception as e:
            return []

    async def get_journey_analytics(self, user_id: Optional[str] = None, 
                                   days_back: int = 30) -> JourneyAnalytics:
        """Get journey analytics and patterns"""
        try:
            analysis_start = datetime.utcnow() - timedelta(days=days_back)
            analysis_end = datetime.utcnow()
            
            # Generate sample analytics
            analytics = JourneyAnalytics(
                total_journeys_analyzed=847,
                average_duration_minutes=45.3,
                average_cost=125.50,
                average_transfers=1.2,
                popular_origins=[
                    ("Colombo Fort", 156),
                    ("Kandy", 98),
                    ("Galle", 76)
                ],
                popular_destinations=[
                    ("Kandy", 134),
                    ("Galle", 89),
                    ("Negombo", 67)
                ],
                popular_routes=[
                    ("Colombo-Kandy Express", 89),
                    ("Galle-Colombo Coastal", 76),
                    ("Kandy-Ella Scenic", 45)
                ],
                mode_usage_stats={
                    "bus": 356,
                    "train": 289,
                    "taxi": 145,
                    "walking": 57
                },
                peak_hours=[7, 8, 9, 17, 18, 19],
                peak_days=["Monday", "Friday"],
                average_rating=4.2,
                completion_rate=0.87,
                analysis_start=analysis_start,
                analysis_end=analysis_end
            )
            
            return analytics
            
        except Exception as e:
            return JourneyAnalytics(
                total_journeys_analyzed=0,
                average_duration_minutes=0.0,
                average_cost=0.0,
                average_transfers=0.0,
                analysis_start=datetime.utcnow() - timedelta(days=days_back),
                analysis_end=datetime.utcnow()
            )

    # Helper methods
    async def _get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences from personalization agent"""
        try:
            result = await self.agent_manager.orchestrate_request(
                request_type="get_preferences",
                payload={"user_id": user_id},
                timeout=3.0
            )
            return result if result else None
        except:
            return None

    async def _get_optimized_routes(self, request: JourneyPlanRequest) -> List[Dict[str, Any]]:
        """Get optimized routes from route optimization agent"""
        try:
            result = await self.agent_manager.orchestrate_request(
                request_type="optimize_route",
                payload={
                    "origin": request.origin.model_dump(),
                    "destination": request.destination.model_dump(),
                    "departure_time": request.departure_time.isoformat() if request.departure_time else None,
                    "preferences": {
                        "max_transfers": request.max_transfers,
                        "max_walking_distance": request.max_walking_distance_km,
                        "preferred_modes": [mode.value for mode in request.preferred_modes],
                        "excluded_modes": [mode.value for mode in request.excluded_modes]
                    }
                },
                timeout=5.0
            )
            routes = result.get("routes", []) if result else []
            
            # If no routes from agent, create sample routes for demo
            if not routes:
                routes = await self._generate_sample_routes(request)
            
            return routes
        except:
            # Fallback to sample routes
            return await self._generate_sample_routes(request)

    async def _apply_personalization(self, routes: List[Dict[str, Any]], 
                                   preferences: Dict[str, Any], 
                                   request: JourneyPlanRequest) -> List[Dict[str, Any]]:
        """Apply personalization to route options"""
        try:
            result = await self.agent_manager.orchestrate_request(
                request_type="generate_recommendations",
                payload={
                    "user_preferences": preferences,
                    "context": {
                        "journey_type": request.journey_type.value,
                        "time_of_day": datetime.utcnow().hour,
                        "routes": routes
                    }
                },
                timeout=3.0
            )
            return result.get("personalized_routes", routes) if result else routes
        except:
            return routes

    async def _calculate_fares(self, routes: List[Dict[str, Any]], 
                             request: JourneyPlanRequest) -> List[Dict[str, Any]]:
        """Calculate fares for route options"""
        try:
            for route in routes:
                fare_result = await self.agent_manager.orchestrate_request(
                    request_type="calculate_fare",
                    payload={
                        "route": route,
                        "passenger_types": {"adult": 1},
                        "apply_discounts": request.apply_discounts
                    },
                    timeout=3.0
                )
                if fare_result:
                    route["fare_info"] = fare_result
            return routes
        except:
            return routes

    async def _filter_accessibility(self, routes: List[Dict[str, Any]], 
                                  request: JourneyPlanRequest) -> List[Dict[str, Any]]:
        """Filter routes based on accessibility requirements"""
        try:
            accessible_routes = []
            for route in routes:
                accessibility_result = await self.agent_manager.orchestrate_request(
                    request_type="assess_route_accessibility",
                    payload={
                        "route": route,
                        "requirements": [req.value for req in request.accessibility_requirements],
                        "wheelchair_access": request.requires_wheelchair_access
                    },
                    timeout=3.0
                )
                if accessibility_result and accessibility_result.get("is_accessible", False):
                    route["accessibility_info"] = accessibility_result
                    accessible_routes.append(route)
            return accessible_routes
        except:
            return routes

    async def _check_disruptions(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for disruptions affecting routes"""
        try:
            for route in routes:
                disruption_result = await self.agent_manager.orchestrate_request(
                    request_type="check_route_disruptions",
                    payload={"route": route},
                    timeout=2.0
                )
                if disruption_result:
                    route["disruptions"] = disruption_result.get("disruptions", [])
            return routes
        except:
            return routes

    async def _get_local_insights(self, request: JourneyPlanRequest) -> Dict[str, Any]:
        """Get local knowledge insights"""
        try:
            result = await self.agent_manager.orchestrate_request(
                request_type="get_location_insights",
                payload={
                    "origin": request.origin.model_dump(),
                    "destination": request.destination.model_dump()
                },
                timeout=3.0
            )
            return result if result else {}
        except:
            return {}

    async def _rank_routes(self, routes: List[Dict[str, Any]], 
                         request: JourneyPlanRequest) -> List[Dict[str, Any]]:
        """Rank routes based on priorities"""
        def calculate_score(route):
            score = 0.0
            
            for priority in request.priorities:
                if priority == JourneyPriority.FASTEST:
                    # Lower duration = higher score
                    duration = route.get("duration_minutes", 999)
                    score += max(0, 10 - (duration / 60)) * 0.3
                
                elif priority == JourneyPriority.CHEAPEST:
                    # Lower cost = higher score
                    cost = route.get("fare_info", {}).get("total_fare", 1000)
                    score += max(0, 10 - (cost / 100)) * 0.3
                
                elif priority == JourneyPriority.MOST_COMFORTABLE:
                    score += route.get("comfort_score", 5.0) * 0.2
                
                elif priority == JourneyPriority.MOST_ACCESSIBLE:
                    if route.get("accessibility_info", {}).get("is_accessible", False):
                        score += 2.0
                
                elif priority == JourneyPriority.BALANCED:
                    score += route.get("overall_score", 5.0) * 0.2
            
            return score
        
        # Sort routes by score (descending)
        return sorted(routes, key=calculate_score, reverse=True)

    async def _convert_to_journeys(self, routes: List[Dict[str, Any]], 
                                 request: JourneyPlanRequest) -> List[Journey]:
        """Convert route data to Journey objects"""
        journeys = []
        
        for route_data in routes:
            try:
                # Create journey legs
                legs = []
                for leg_data in route_data.get("segments", []):
                    leg = JourneyLeg(
                        transport_mode=TransportMode(leg_data.get("transport_mode", "bus")),
                        operator=TransportOperator(
                            operator_id=leg_data.get("operator_id", "unknown"),
                            name=leg_data.get("operator_name", "Unknown Operator"),
                            type=leg_data.get("operator_type", "bus")
                        ),
                        route_name=leg_data.get("route_name", "Unknown Route"),
                        departure_location=Location(**leg_data.get("departure_location", request.origin.model_dump())),
                        arrival_location=Location(**leg_data.get("arrival_location", request.destination.model_dump())),
                        departure_time=datetime.fromisoformat(leg_data.get("departure_time", datetime.utcnow().isoformat())),
                        arrival_time=datetime.fromisoformat(leg_data.get("arrival_time", (datetime.utcnow() + timedelta(hours=1)).isoformat())),
                        duration_minutes=leg_data.get("duration_minutes", 60),
                        distance_km=leg_data.get("distance_km", 10.0),
                        fare_breakdown=leg_data.get("fare_info")
                    )
                    legs.append(leg)
                
                # Create journey
                journey = Journey(
                    origin=request.origin,
                    destination=request.destination,
                    legs=legs,
                    departure_time=legs[0].departure_time if legs else datetime.utcnow(),
                    arrival_time=legs[-1].arrival_time if legs else datetime.utcnow() + timedelta(hours=1),
                    total_duration_minutes=route_data.get("duration_minutes", 60),
                    total_distance_km=route_data.get("distance_km", 10.0),
                    total_fare=route_data.get("fare_info", {}).get("total_fare", 50.0),
                    comfort_score=route_data.get("comfort_score", 7.0),
                    reliability_score=route_data.get("reliability_score", 8.0),
                    accessibility_score=route_data.get("accessibility_score", 6.0),
                    environmental_score=route_data.get("environmental_score", 7.5),
                    overall_score=route_data.get("overall_score", 7.0),
                    is_wheelchair_accessible=route_data.get("accessibility_info", {}).get("is_accessible", False),
                    active_disruptions=route_data.get("disruptions", []),
                    is_real_time=True,
                    confidence_level=0.85
                )
                
                journeys.append(journey)
                
            except Exception as e:
                # Skip invalid route data
                continue
        
        return journeys

    async def _optimize_waypoint_order(self, waypoints: List[Location]) -> List[Location]:
        """Optimize the order of waypoints for multi-stop journey"""
        # Simple optimization - keep origin and destination, optimize middle points
        if len(waypoints) <= 3:
            return waypoints
        
        origin = waypoints[0]
        destination = waypoints[-1]
        middle_points = waypoints[1:-1]
        
        # For now, return original order (could implement TSP algorithm)
        return [origin] + middle_points + [destination]

    async def _combine_journey_segments(self, segments: List[Journey], 
                                      total_duration: int) -> Journey:
        """Combine multiple journey segments into one"""
        if not segments:
            return None
        
        # Combine all legs from all segments
        all_legs = []
        all_transfers = []
        
        for i, segment in enumerate(segments):
            all_legs.extend(segment.legs)
            all_transfers.extend(segment.transfers)
            
            # Add transfer between segments (except for last segment)
            if i < len(segments) - 1:
                transfer = TransferDetails(
                    location=segment.destination,
                    stop_name=f"Transfer at {segment.destination.name}",
                    arrival_time=segment.arrival_time,
                    departure_time=segments[i + 1].departure_time,
                    transfer_duration_minutes=10,
                    walking_distance_meters=100,
                    walking_time_minutes=2
                )
                all_transfers.append(transfer)
        
        # Create combined journey
        combined_journey = Journey(
            journey_type=JourneyType.MULTI_STOP,
            origin=segments[0].origin,
            destination=segments[-1].destination,
            legs=all_legs,
            transfers=all_transfers,
            departure_time=segments[0].departure_time,
            arrival_time=segments[-1].arrival_time,
            total_duration_minutes=total_duration,
            total_distance_km=sum(s.total_distance_km for s in segments),
            total_fare=sum(s.total_fare for s in segments),
            comfort_score=sum(s.comfort_score for s in segments) / len(segments),
            reliability_score=sum(s.reliability_score for s in segments) / len(segments),
            accessibility_score=min(s.accessibility_score for s in segments),
            environmental_score=sum(s.environmental_score for s in segments) / len(segments),
            overall_score=sum(s.overall_score for s in segments) / len(segments),
            journey_tags=["multi_stop"]
        )
        
        return combined_journey

    async def _get_journey_by_id(self, journey_id: str) -> Optional[Journey]:
        """Get journey by ID (simulate database lookup)"""
        # For demo purposes, return a sample journey with complete legs
        from app.models.journey_planning import JourneyLeg
        
        # Create a sample journey leg
        departure_time = datetime.utcnow() + timedelta(hours=1)
        arrival_time = datetime.utcnow() + timedelta(hours=4)
        
        sample_leg = JourneyLeg(
            transport_mode=TransportMode.TRAIN,
            operator=TransportOperator(
                operator_id="slr_001",
                name="Sri Lanka Railways",
                type="train"
            ),
            route_name="Main Line Express",
            departure_location=Location(latitude=6.9344, longitude=79.8428, name="Colombo Fort"),
            arrival_location=Location(latitude=7.2906, longitude=80.6337, name="Kandy"),
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration_minutes=180,
            distance_km=115.0,
            fare_breakdown={"base_fare": 250.0, "currency": "LKR"}
        )
        
        return Journey(
            journey_id=journey_id,
            origin=Location(latitude=6.9344, longitude=79.8428, name="Colombo Fort"),
            destination=Location(latitude=7.2906, longitude=80.6337, name="Kandy"),
            legs=[sample_leg],
            departure_time=departure_time,
            arrival_time=arrival_time,
            total_duration_minutes=180,
            total_distance_km=115.0,
            total_fare=250.0,
            comfort_score=8.0,
            reliability_score=8.5,
            accessibility_score=7.0,
            environmental_score=9.0,
            overall_score=8.5
        )

    async def _check_journey_availability(self, journey: Journey) -> bool:
        """Check if journey is still available for booking"""
        # Simple availability check
        return journey.departure_time > datetime.utcnow() + timedelta(minutes=30)

    async def _calculate_booking_fare(self, journey: Journey, 
                                    booking_request: BookingRequest) -> float:
        """Calculate total fare for booking"""
        base_fare = journey.total_fare
        total_fare = 0.0
        
        # Apply passenger type multipliers
        for passenger_type, count in booking_request.passenger_types.items():
            if passenger_type == "adult":
                total_fare += base_fare * count
            elif passenger_type == "child":
                total_fare += base_fare * 0.5 * count
            elif passenger_type == "senior":
                total_fare += base_fare * 0.7 * count
            elif passenger_type == "student":
                total_fare += base_fare * 0.8 * count
        
        # If no passenger types specified, default to adult fare
        if not booking_request.passenger_types:
            total_fare = base_fare * booking_request.passenger_count
        
        return total_fare

    async def _get_trip_by_id(self, trip_id: str) -> Optional[TripManagement]:
        """Get trip by ID (simulate database lookup)"""
        # For demo purposes, return a sample trip
        journey = await self._get_journey_by_id("sample_journey_123")
        return TripManagement(
            trip_id=trip_id,
            user_id="user_123",
            journey=journey,
            status="planned",
            user_rating=4.0  # Add required field with valid value
        )

    async def _generate_sample_routes(self, request: JourneyPlanRequest) -> List[Dict[str, Any]]:
        """Generate sample route data for demo purposes"""
        routes = []
        
        # Route 1: Direct bus route
        route1 = {
            "route_id": f"route_{request.origin.name}_{request.destination.name}_bus",
            "transport_modes": ["bus"],
            "total_duration_minutes": 120,
            "total_distance_km": 85.0,
            "total_fare": 150.0,
            "segments": [
                {
                    "transport_mode": "bus",
                    "operator_id": "sltb_001",
                    "operator_name": "SLTB",
                    "operator_type": "bus",
                    "route_name": f"{request.origin.name}-{request.destination.name} Express",
                    "departure_location": request.origin.model_dump(),
                    "arrival_location": request.destination.model_dump(),
                    "departure_time": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
                    "arrival_time": (datetime.utcnow() + timedelta(minutes=150)).isoformat(),
                    "duration_minutes": 120,
                    "distance_km": 85.0,
                    "fare_info": {"base_fare": 150.0, "currency": "LKR"}
                }
            ],
            "reliability_score": 0.85,
            "comfort_score": 0.7,
            "environmental_score": 0.8
        }
        routes.append(route1)
        
        # Route 2: Train route
        route2 = {
            "route_id": f"route_{request.origin.name}_{request.destination.name}_train",
            "transport_modes": ["train"],
            "total_duration_minutes": 180,
            "total_distance_km": 115.0,
            "total_fare": 200.0,
            "segments": [
                {
                    "transport_mode": "train",
                    "operator_id": "slr_001",
                    "operator_name": "Sri Lanka Railways",
                    "operator_type": "train",
                    "route_name": f"{request.origin.name}-{request.destination.name} Main Line",
                    "departure_location": request.origin.model_dump(),
                    "arrival_location": request.destination.model_dump(),
                    "departure_time": (datetime.utcnow() + timedelta(minutes=45)).isoformat(),
                    "arrival_time": (datetime.utcnow() + timedelta(minutes=225)).isoformat(),
                    "duration_minutes": 180,
                    "distance_km": 115.0,
                    "fare_info": {"base_fare": 200.0, "currency": "LKR"}
                }
            ],
            "reliability_score": 0.7,
            "comfort_score": 0.9,
            "environmental_score": 0.9
        }
        routes.append(route2)
        
        return routes

    async def _generate_sample_journeys(self) -> List[Journey]:
        """Generate sample journeys for search"""
        sample_journeys = [
            Journey(
                origin=Location(name="Colombo", latitude=6.9271, longitude=79.8612),
                destination=Location(name="Kandy", latitude=7.2906, longitude=80.6337),
                departure_time=datetime.utcnow() + timedelta(hours=2),
                arrival_time=datetime.utcnow() + timedelta(hours=5),
                total_duration_minutes=180,
                total_distance_km=115.0,
                total_fare=250.0,
                comfort_score=8.0,
                reliability_score=9.0,
                overall_score=8.5
            ),
            Journey(
                origin=Location(name="Colombo", latitude=6.9271, longitude=79.8612),
                destination=Location(name="Galle", latitude=6.0535, longitude=80.2210),
                departure_time=datetime.utcnow() + timedelta(hours=1),
                arrival_time=datetime.utcnow() + timedelta(hours=3),
                total_duration_minutes=120,
                total_distance_km=120.0,
                total_fare=180.0,
                comfort_score=7.5,
                reliability_score=8.5,
                overall_score=8.0
            )
        ]
        return sample_journeys

    def _journey_matches_filters(self, journey: Journey, 
                               filters: JourneySearchFilters) -> bool:
        """Check if journey matches search filters"""
        # Time filters
        if filters.departure_time_range:
            start, end = filters.departure_time_range
            if not (start <= journey.departure_time <= end):
                return False
        
        # Cost filters
        if filters.min_fare and journey.total_fare < filters.min_fare:
            return False
        if filters.max_fare and journey.total_fare > filters.max_fare:
            return False
        
        # Duration filters
        if filters.max_duration_hours:
            max_duration_minutes = filters.max_duration_hours * 60
            if journey.total_duration_minutes > max_duration_minutes:
                return False
        
        # Quality filters
        if filters.min_comfort_score and journey.comfort_score < filters.min_comfort_score:
            return False
        if filters.min_reliability_score and journey.reliability_score < filters.min_reliability_score:
            return False
        
        # Accessibility filters
        if filters.wheelchair_accessible_only and not journey.is_wheelchair_accessible:
            return False
        
        return True