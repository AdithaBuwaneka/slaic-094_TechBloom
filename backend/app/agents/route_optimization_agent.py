from app.agents.base_agent import BaseAgent
from app.models.route_optimization import (
    RouteOptimizationRequest, OptimizedRoute, RouteAlternatives, 
    RouteSegment, TransferPoint, OptimizationCriteria, OptimizationMetrics
)
from app.models.transport_data import Location, TransportMode, RouteData
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import math
from datetime import datetime, timedelta
import random


class RouteOptimizationAgent(BaseAgent):
    """
    Route Optimization Agent - Multi-Modal Journey Planning
    
    Primary Functions:
    - Temporal feasibility analysis
    - Multi-modal combination optimization  
    - Walking distance and transfer time minimization
    - Reliability scoring based on historical performance
    - Door-to-door journey time estimation
    - Route ranking with weighted scoring
    - Alternative path generation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="route_optimization_agent",
            name="Route Optimization Agent", 
            priority_weight=0.8  # High priority for route planning
        )
        
        # Optimization parameters
        self.default_weights = {
            "time": 0.4,
            "cost": 0.3, 
            "comfort": 0.15,
            "reliability": 0.15
        }
        
        # Transport mode characteristics
        self.mode_characteristics = {
            TransportMode.TRAIN: {
                "avg_speed_kmh": 45,
                "comfort_score": 0.8,
                "reliability_score": 0.85,
                "carbon_factor_kg_km": 0.041,
                "boarding_time_min": 3
            },
            TransportMode.BUS: {
                "avg_speed_kmh": 25,
                "comfort_score": 0.6,
                "reliability_score": 0.7,
                "carbon_factor_kg_km": 0.089,
                "boarding_time_min": 2
            },
            TransportMode.WALKING: {
                "avg_speed_kmh": 5,
                "comfort_score": 0.5,
                "reliability_score": 1.0,
                "carbon_factor_kg_km": 0.0,
                "boarding_time_min": 0
            },
            TransportMode.TAXI: {
                "avg_speed_kmh": 35,
                "comfort_score": 0.9,
                "reliability_score": 0.8,
                "carbon_factor_kg_km": 0.171,
                "boarding_time_min": 5
            }
        }
        
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for route optimization requests"""
        
        request_type = payload.get("request_type", "")
        data = payload.get("data", {})
        
        if request_type == "optimize_route":
            return await self._optimize_route(data)
        elif request_type == "find_alternatives":
            return await self._find_route_alternatives(data)
        elif request_type == "analyze_feasibility":
            return await self._analyze_route_feasibility(data)
        elif request_type == "calculate_metrics":
            return await self._calculate_optimization_metrics(data)
        elif request_type == "estimate_journey_time":
            return await self._estimate_journey_time(data)
        else:
            return {
                "status": "unknown_request",
                "message": f"Unknown request type: {request_type}",
                "supported_requests": [
                    "optimize_route", "find_alternatives", "analyze_feasibility",
                    "calculate_metrics", "estimate_journey_time"
                ]
            }
            
    async def _optimize_route(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize route based on given criteria"""
        
        try:
            # Parse request
            req = RouteOptimizationRequest(**request_data)
            
            # Simulate route optimization processing
            await asyncio.sleep(0.3)  # Simulate complex calculations
            
            # Generate optimized routes
            routes = await self._generate_route_options(req)
            
            # Rank routes based on criteria
            ranked_routes = await self._rank_routes(routes, req)
            
            return {
                "status": "success",
                "optimized_routes": [route.dict() for route in ranked_routes[:5]],  # Top 5
                "best_route": ranked_routes[0].dict() if ranked_routes else None,
                "optimization_criteria": req.optimization_criteria,
                "total_routes_evaluated": len(routes),
                "processing_summary": {
                    "fastest_time_min": min([r.total_duration_minutes for r in routes]) if routes else 0,
                    "cheapest_cost": min([r.total_cost for r in routes]) if routes else 0,
                    "avg_reliability": sum([r.reliability_score for r in routes]) / len(routes) if routes else 0
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Route optimization failed: {str(e)}"
            }
            
    async def _find_route_alternatives(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find comprehensive route alternatives"""
        
        try:
            req = RouteOptimizationRequest(**request_data)
            
            # Generate all possible route combinations
            all_routes = await self._generate_comprehensive_routes(req)
            
            if not all_routes:
                return {
                    "status": "no_routes_found",
                    "message": "No feasible routes found for the given criteria"
                }
                
            # Categorize routes by optimization type
            alternatives = RouteAlternatives(
                request_id=f"route_alt_{datetime.utcnow().isoformat()}",
                origin=req.origin,
                destination=req.destination,
                all_routes=all_routes,
                routes_analyzed=len(all_routes),
                processing_time_seconds=0.5
            )
            
            # Find specialized routes
            alternatives.fastest_route = min(all_routes, key=lambda r: r.total_duration_minutes)
            alternatives.cheapest_route = min(all_routes, key=lambda r: r.total_cost)
            alternatives.most_comfortable_route = max(all_routes, key=lambda r: r.comfort_score)
            alternatives.most_reliable_route = max(all_routes, key=lambda r: r.reliability_score)
            alternatives.recommended_route = max(all_routes, key=lambda r: r.overall_score)
            
            return {
                "status": "success",
                "alternatives": alternatives.dict(),
                "summary": {
                    "total_alternatives": len(all_routes),
                    "time_range": f"{alternatives.fastest_route.total_duration_minutes}-{max(all_routes, key=lambda r: r.total_duration_minutes).total_duration_minutes} min",
                    "cost_range": f"Rs.{alternatives.cheapest_route.total_cost:.0f}-{max(all_routes, key=lambda r: r.total_cost).total_cost:.0f}",
                    "transport_modes": list(set([mode for route in all_routes for segment in route.segments for mode in [segment.transport_mode]]))
                }
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Alternative route generation failed: {str(e)}"
            }
            
    async def _generate_route_options(self, req: RouteOptimizationRequest) -> List[OptimizedRoute]:
        """Generate multiple route options"""
        
        routes = []
        
        # Generate different route combinations
        route_combinations = [
            # Direct routes
            {"modes": [TransportMode.BUS], "transfers": 0},
            {"modes": [TransportMode.TRAIN], "transfers": 0},
            
            # Multi-modal routes
            {"modes": [TransportMode.BUS, TransportMode.TRAIN], "transfers": 1},
            {"modes": [TransportMode.WALKING, TransportMode.BUS], "transfers": 1},
            {"modes": [TransportMode.TRAIN, TransportMode.WALKING], "transfers": 1},
            
            # Complex multi-modal
            {"modes": [TransportMode.WALKING, TransportMode.BUS, TransportMode.TRAIN], "transfers": 2},
        ]
        
        for i, combo in enumerate(route_combinations):
            if len(combo["modes"]) > req.max_transfers + 1:
                continue
                
            route = await self._generate_single_route(
                f"route_opt_{i+1}",
                req,
                combo["modes"],
                combo["transfers"]
            )
            if route:
                routes.append(route)
                
        return routes
        
    async def _generate_comprehensive_routes(self, req: RouteOptimizationRequest) -> List[OptimizedRoute]:
        """Generate comprehensive set of route alternatives"""
        
        # This would use the data from Data Aggregation Agent
        # For now, generating mock comprehensive routes
        
        routes = []
        base_distance = self._calculate_distance(req.origin, req.destination)
        
        # Generate various route scenarios
        scenarios = [
            {"name": "Express Bus", "modes": [TransportMode.BUS], "time_factor": 1.0, "cost_factor": 1.0},
            {"name": "Train Express", "modes": [TransportMode.TRAIN], "time_factor": 0.8, "cost_factor": 0.6},
            {"name": "Bus + Train", "modes": [TransportMode.BUS, TransportMode.TRAIN], "time_factor": 1.2, "cost_factor": 0.8},
            {"name": "Walk + Bus", "modes": [TransportMode.WALKING, TransportMode.BUS], "time_factor": 1.3, "cost_factor": 0.9},
            {"name": "Taxi Direct", "modes": [TransportMode.TAXI], "time_factor": 0.7, "cost_factor": 3.0},
            {"name": "Multi-modal", "modes": [TransportMode.WALKING, TransportMode.BUS, TransportMode.TRAIN], "time_factor": 1.4, "cost_factor": 0.7}
        ]
        
        for i, scenario in enumerate(scenarios):
            route = await self._generate_scenario_route(
                f"comprehensive_{i+1}",
                req,
                scenario,
                base_distance
            )
            if route:
                routes.append(route)
                
        return routes
        
    async def _generate_single_route(self, route_id: str, req: RouteOptimizationRequest, 
                                   modes: List[TransportMode], transfers: int) -> Optional[OptimizedRoute]:
        """Generate a single optimized route"""
        
        try:
            segments = []
            total_duration = 0
            total_cost = 0.0
            total_distance = 0.0
            current_time = req.departure_time or datetime.utcnow()
            
            # Calculate base distance
            base_distance = self._calculate_distance(req.origin, req.destination)
            segment_distance = base_distance / len(modes)
            
            for i, mode in enumerate(modes):
                characteristics = self.mode_characteristics[mode]
                
                # Calculate segment details
                duration = int(segment_distance / characteristics["avg_speed_kmh"] * 60)
                if mode == TransportMode.BUS:
                    fare = segment_distance * 3.5  # Rs per km
                elif mode == TransportMode.TRAIN:
                    fare = segment_distance * 2.0  # Rs per km  
                elif mode == TransportMode.TAXI:
                    fare = segment_distance * 150  # Rs per km
                else:
                    fare = 0.0
                    
                # Add boarding time and random delay
                duration += characteristics["boarding_time_min"]
                duration += random.randint(0, 15)  # Random delay
                
                segment = RouteSegment(
                    route_id=f"{route_id}_seg_{i+1}",
                    transport_mode=mode,
                    from_stop=f"Stop_{i}",
                    to_stop=f"Stop_{i+1}", 
                    departure_time=current_time,
                    arrival_time=current_time + timedelta(minutes=duration),
                    duration_minutes=duration,
                    distance_km=segment_distance,
                    fare=fare,
                    operator=f"{mode.value.title()} Operator",
                    reliability_score=characteristics["reliability_score"],
                    comfort_score=characteristics["comfort_score"],
                    occupancy_level=random.choice(["low", "medium", "high"])
                )
                
                segments.append(segment)
                total_duration += duration
                total_cost += fare
                total_distance += segment_distance
                current_time = segment.arrival_time
                
                # Add transfer time
                if i < len(modes) - 1:
                    transfer_time = random.randint(5, 15)
                    current_time += timedelta(minutes=transfer_time)
                    total_duration += transfer_time
                    
            # Calculate scores
            time_score = max(0.1, 1.0 - (total_duration - 60) / 180)  # Normalize around 60-240 min
            cost_score = max(0.1, 1.0 - (total_cost - 50) / 200)     # Normalize around 50-250 Rs
            comfort_score = sum([s.comfort_score for s in segments]) / len(segments)
            reliability_score = sum([s.reliability_score for s in segments]) / len(segments)
            
            # Calculate overall score using weights
            weights = req.criteria_weights or self.default_weights
            overall_score = (
                time_score * weights.get("time", 0.4) +
                cost_score * weights.get("cost", 0.3) +
                comfort_score * weights.get("comfort", 0.15) +
                reliability_score * weights.get("reliability", 0.15)
            )
            
            route = OptimizedRoute(
                route_id=route_id,
                total_duration_minutes=total_duration,
                total_cost=total_cost,
                total_distance_km=total_distance,
                segments=segments,
                time_score=time_score,
                cost_score=cost_score,
                comfort_score=comfort_score, 
                reliability_score=reliability_score,
                overall_score=overall_score,
                departure_time=segments[0].departure_time,
                arrival_time=segments[-1].arrival_time,
                number_of_transfers=transfers,
                total_walking_distance_meters=sum([int(s.distance_km * 1000) for s in segments if s.transport_mode == TransportMode.WALKING])
            )
            
            return route
            
        except Exception as e:
            print(f"Error generating route {route_id}: {e}")
            return None
            
    async def _generate_scenario_route(self, route_id: str, req: RouteOptimizationRequest,
                                     scenario: Dict[str, Any], base_distance: float) -> Optional[OptimizedRoute]:
        """Generate route for specific scenario"""
        
        try:
            modes = scenario["modes"]
            time_factor = scenario["time_factor"]
            cost_factor = scenario["cost_factor"]
            
            # Base calculations
            base_time = int(base_distance / 30 * 60)  # 30 kmh average
            base_cost = base_distance * 4.0  # Rs 4 per km average
            
            # Apply scenario factors
            total_duration = int(base_time * time_factor) + random.randint(-10, 20)
            total_cost = base_cost * cost_factor + random.uniform(-20, 50)
            
            # Create segments
            segments = []
            segment_time = total_duration // len(modes)
            segment_cost = total_cost / len(modes)
            segment_distance = base_distance / len(modes)
            
            current_time = req.departure_time or datetime.utcnow()
            
            for i, mode in enumerate(modes):
                characteristics = self.mode_characteristics[mode]
                
                segment = RouteSegment(
                    route_id=f"{route_id}_seg_{i+1}",
                    transport_mode=mode,
                    from_stop=f"Stop_{i}",
                    to_stop=f"Stop_{i+1}",
                    departure_time=current_time,
                    arrival_time=current_time + timedelta(minutes=segment_time),
                    duration_minutes=segment_time,
                    distance_km=segment_distance,
                    fare=max(0, segment_cost),
                    operator=f"{mode.value.title()} Service",
                    reliability_score=characteristics["reliability_score"] * random.uniform(0.8, 1.0),
                    comfort_score=characteristics["comfort_score"] * random.uniform(0.8, 1.0),
                    occupancy_level=random.choice(["low", "medium", "high"])
                )
                
                segments.append(segment)
                current_time = segment.arrival_time
                
                # Add transfer time if not last segment
                if i < len(modes) - 1:
                    transfer_time = random.randint(3, 12)
                    current_time += timedelta(minutes=transfer_time)
                    
            # Calculate comprehensive scores
            avg_reliability = sum([s.reliability_score for s in segments]) / len(segments)
            avg_comfort = sum([s.comfort_score for s in segments]) / len(segments)
            
            time_score = max(0.1, min(1.0, 1.5 - total_duration / 120))
            cost_score = max(0.1, min(1.0, 1.5 - total_cost / 150))
            
            overall_score = (time_score * 0.4 + cost_score * 0.3 + 
                           avg_comfort * 0.15 + avg_reliability * 0.15)
            
            route = OptimizedRoute(
                route_id=route_id,
                total_duration_minutes=total_duration,
                total_cost=max(0, total_cost),
                total_distance_km=base_distance,
                segments=segments,
                time_score=time_score,
                cost_score=cost_score,
                comfort_score=avg_comfort,
                reliability_score=avg_reliability,
                overall_score=overall_score,
                departure_time=segments[0].departure_time,
                arrival_time=segments[-1].arrival_time,
                number_of_transfers=len(modes) - 1,
                carbon_footprint_kg=sum([s.distance_km * self.mode_characteristics[s.transport_mode]["carbon_factor_kg_km"] for s in segments])
            )
            
            return route
            
        except Exception as e:
            print(f"Error generating scenario route {route_id}: {e}")
            return None
            
    async def _rank_routes(self, routes: List[OptimizedRoute], 
                          req: RouteOptimizationRequest) -> List[OptimizedRoute]:
        """Rank routes based on optimization criteria"""
        
        if not routes:
            return []
            
        # Sort by overall score (highest first)
        ranked = sorted(routes, key=lambda r: r.overall_score, reverse=True)
        
        # Apply additional filters
        filtered_routes = []
        for route in ranked:
            # Check constraints
            if req.budget_limit and route.total_cost > req.budget_limit:
                continue
            if req.max_journey_time_minutes and route.total_duration_minutes > req.max_journey_time_minutes:
                continue  
            if req.max_transfers < route.number_of_transfers:
                continue
                
            filtered_routes.append(route)
            
        return filtered_routes
        
    async def _analyze_route_feasibility(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feasibility of a route request"""
        
        try:
            req = RouteOptimizationRequest(**request_data)
            
            feasibility_issues = []
            alternative_suggestions = []
            
            # Distance check
            distance = self._calculate_distance(req.origin, req.destination)
            if distance > 500:  # 500km max
                feasibility_issues.append("Distance exceeds maximum travel range")
                alternative_suggestions.append("Consider flight options for long distances")
                
            # Time constraints check
            if req.departure_time and req.arrival_time:
                time_diff = (req.arrival_time - req.departure_time).total_seconds() / 60
                min_travel_time = distance / 60 * 60  # Assume 60kmh average
                if time_diff < min_travel_time:
                    feasibility_issues.append("Time constraint too restrictive")
                    alternative_suggestions.append("Allow more time or adjust departure/arrival times")
                    
            # Mode availability check
            if req.preferred_modes:
                for mode in req.preferred_modes:
                    if mode not in [TransportMode.BUS, TransportMode.TRAIN, TransportMode.WALKING]:
                        feasibility_issues.append(f"Limited availability for {mode.value}")
                        
            is_feasible = len(feasibility_issues) == 0
            
            return {
                "status": "success",
                "is_feasible": is_feasible,
                "feasibility_score": 1.0 - (len(feasibility_issues) * 0.2),
                "issues": feasibility_issues,
                "suggestions": alternative_suggestions,
                "estimated_journey_time_range": f"{int(distance/50*60)}-{int(distance/20*60)} minutes",
                "estimated_cost_range": f"Rs.{distance*2:.0f}-{distance*8:.0f}",
                "available_modes": ["bus", "train", "walking", "taxi"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Feasibility analysis failed: {str(e)}"
            }
            
    async def _estimate_journey_time(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate journey time for different scenarios"""
        
        try:
            origin = Location(**request_data.get("origin", {}))
            destination = Location(**request_data.get("destination", {}))
            modes = request_data.get("transport_modes", ["bus", "train"])
            
            distance = self._calculate_distance(origin, destination)
            
            estimates = {}
            for mode_str in modes:
                mode = TransportMode(mode_str)
                characteristics = self.mode_characteristics[mode]
                
                # Basic time calculation
                travel_time = distance / characteristics["avg_speed_kmh"] * 60
                total_time = travel_time + characteristics["boarding_time_min"]
                
                # Add variability
                min_time = int(total_time * 0.8)
                max_time = int(total_time * 1.3)
                avg_time = int(total_time)
                
                estimates[mode_str] = {
                    "min_minutes": min_time,
                    "avg_minutes": avg_time, 
                    "max_minutes": max_time,
                    "reliability_score": characteristics["reliability_score"]
                }
                
            return {
                "status": "success",
                "distance_km": distance,
                "time_estimates": estimates,
                "recommended_mode": min(estimates.items(), key=lambda x: x[1]["avg_minutes"])[0]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Journey time estimation failed: {str(e)}"
            }
            
    def _calculate_distance(self, origin: Location, destination: Location) -> float:
        """Calculate distance between two locations using Haversine formula"""
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(origin.latitude), math.radians(origin.longitude)
        lat2, lon2 = math.radians(destination.latitude), math.radians(destination.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
        
    async def _calculate_optimization_metrics(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimization performance metrics"""
        
        try:
            routes_data = request_data.get("routes", [])
            if not routes_data:
                return {"status": "error", "message": "No routes provided for metrics calculation"}
                
            routes = [OptimizedRoute(**route) for route in routes_data]
            
            metrics = OptimizationMetrics(
                avg_journey_time_minutes=sum([r.total_duration_minutes for r in routes]) / len(routes),
                min_journey_time_minutes=min([r.total_duration_minutes for r in routes]),
                max_journey_time_minutes=max([r.total_duration_minutes for r in routes]),
                avg_cost=sum([r.total_cost for r in routes]) / len(routes),
                min_cost=min([r.total_cost for r in routes]),
                max_cost=max([r.total_cost for r in routes]),
                avg_reliability_score=sum([r.reliability_score for r in routes]) / len(routes),
                on_time_probability=sum([r.reliability_score for r in routes]) / len(routes),
                avg_transfers=sum([r.number_of_transfers for r in routes]) / len(routes),
                max_walking_distance=max([r.total_walking_distance_meters for r in routes]),
                transport_modes_used=list(set([s.transport_mode for r in routes for s in r.segments])),
                operators_covered=list(set([s.operator for r in routes for s in r.segments])),
                route_diversity_score=min(1.0, len(routes) / 10),  # More routes = more diversity
                optimization_confidence=sum([r.overall_score for r in routes]) / len(routes)
            )
            
            return {
                "status": "success",
                "metrics": metrics.dict(),
                "summary": {
                    "total_routes_analyzed": len(routes),
                    "best_overall_score": max([r.overall_score for r in routes]),
                    "optimization_quality": "excellent" if metrics.optimization_confidence > 0.8 else "good" if metrics.optimization_confidence > 0.6 else "moderate"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Metrics calculation failed: {str(e)}"
            }