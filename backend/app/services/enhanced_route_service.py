"""
Enhanced Route Service that provides supplementary routes and integrates with multiagent system.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo

from ..core.database import db
from ..services.google_maps_service import get_optimized_route
from ..services.multiagent_system import TransitMultiAgentSystem
from ..models.transit_data import TransitMode, TransitFare, LastMileOption
from ..models.enhanced_route import EnhancedRouteResponse, RouteSegment

class EnhancedRouteService:
    """Enhanced route service with supplementary routes and multiagent integration"""
    
    def __init__(self):
        self.multiagent_system = TransitMultiAgentSystem()
    
    async def get_enhanced_route(
        self,
        origin: str,
        destination: str,
        mode: str,
        transit_preference: Optional[str] = None,
        user_id: Optional[str] = None,
        include_supplementary: bool = True
    ) -> Dict[str, Any]:
        """
        Get enhanced route with supplementary options and multiagent analysis
        """
        
        try:
            # Get primary route
            primary_route, error = get_optimized_route(
                origin=origin,
                destination=destination,
                mode=mode,
                departure_time=int(datetime.now().timestamp()),
                transit_mode_preference=transit_preference
            )
            
            if error:
                return {"error": error, "success": False}
            
            # Initialize response
            response = {
                "primary_route": primary_route,
                "supplementary_routes": [],
                "multiagent_analysis": None,
                "fares": [],
                "last_mile_options": [],
                "success": True
            }
            
            # Get supplementary routes if requested
            if include_supplementary:
                supplementary_routes = await self._get_supplementary_routes(
                    origin, destination, mode, transit_preference
                )
                response["supplementary_routes"] = supplementary_routes
            
            # Get fare information
            if mode == "transit" or mode == "uber":
                fares = await self._get_route_fares(origin, destination, mode)
                response["fares"] = fares
            
            # Get last mile options for transit
            if mode == "transit":
                last_mile = await self._get_last_mile_options(origin, destination)
                response["last_mile_options"] = last_mile
            
            # Use multiagent system for transit mode
            if mode == "transit":
                multiagent_result = await self.multiagent_system.plan_route(
                    origin, destination, mode
                )
                response["multiagent_analysis"] = multiagent_result
            
            return response
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_supplementary_routes(
        self,
        origin: str,
        destination: str,
        mode: str,
        transit_preference: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get supplementary route options"""
        
        supplementary_routes = []
        
        try:
            # For transit mode, get alternative routes from database
            if mode == "transit":
                db_routes = await self._get_transit_routes_from_db(origin, destination)
                
                for route in db_routes[:3]:  # Limit to 3 alternatives
                    supplementary_routes.append({
                        "type": "database_route",
                        "route_id": route.get("route_id"),
                        "route_number": route.get("route_number"),
                        "operator": route.get("operator"),
                        "stops": route.get("stops", []),
                        "frequency": route.get("frequency"),
                        "estimated_duration": self._estimate_duration_from_stops(route.get("stops", [])),
                        "source": "database"
                    })
            
            # Get alternative modes if primary mode is driving
            elif mode == "driving":
                # Try walking route
                try:
                    walking_route, _ = get_optimized_route(
                        origin=origin,
                        destination=destination,
                        mode="walking",
                        departure_time=int(datetime.now().timestamp())
                    )
                    
                    if walking_route:
                        supplementary_routes.append({
                            "type": "alternative_mode",
                            "mode": "walking",
                            "route": walking_route,
                            "source": "google_maps"
                        })
                except:
                    pass
                
                # Try transit route
                try:
                    transit_route, _ = get_optimized_route(
                        origin=origin,
                        destination=destination,
                        mode="transit",
                        departure_time=int(datetime.now().timestamp()),
                        transit_mode_preference=transit_preference
                    )
                    
                    if transit_route:
                        supplementary_routes.append({
                            "type": "alternative_mode",
                            "mode": "transit",
                            "route": transit_route,
                            "source": "google_maps"
                        })
                except:
                    pass
            
            # For transit mode, also try different transit preferences
            elif mode == "transit":
                if transit_preference == "bus":
                    # Try train route
                    try:
                        train_route, _ = get_optimized_route(
                            origin=origin,
                            destination=destination,
                            mode="transit",
                            departure_time=int(datetime.now().timestamp()),
                            transit_mode_preference="train"
                        )
                        
                        if train_route:
                            supplementary_routes.append({
                                "type": "alternative_transit",
                                "mode": "train",
                                "route": train_route,
                                "source": "google_maps"
                            })
                    except:
                        pass
                
                elif transit_preference == "train":
                    # Try bus route
                    try:
                        bus_route, _ = get_optimized_route(
                            origin=origin,
                            destination=destination,
                            mode="transit",
                            departure_time=int(datetime.now().timestamp()),
                            transit_mode_preference="bus"
                        )
                        
                        if bus_route:
                            supplementary_routes.append({
                                "type": "alternative_transit",
                                "mode": "bus",
                                "route": bus_route,
                                "source": "google_maps"
                            })
                    except:
                        pass
            
        except Exception as e:
            print(f"Error getting supplementary routes: {e}")
        
        return supplementary_routes
    
    async def _get_transit_routes_from_db(
        self,
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """Get transit routes from database"""
        
        try:
            collection = db.database["transit_routes"]
            
            # Simple text search for now
            routes = await collection.find({
                "$or": [
                    {"origin": {"$regex": origin, "$options": "i"}},
                    {"destination": {"$regex": destination, "$options": "i"}}
                ]
            }).to_list(length=5)

            # Convert ObjectId to string for JSON serialization
            for route in routes:
                if "_id" in route:
                    route["_id"] = str(route["_id"])
        
            return routes
            
        except Exception as e:
            print(f"Error getting transit routes from DB: {e}")
            return []
    
    async def _get_route_fares(
        self,
        origin: str,
        destination: str,
        mode: str
    ) -> List[Dict[str, Any]]:
        """Get fare information for routes"""
        
        try:
            collection = db.database["transit_fares"]
            
            # Get fares for the route
            fares = await collection.find({
                "$or": [
                    {"origin": {"$regex": origin, "$options": "i"}},
                    {"destination": {"$regex": destination, "$options": "i"}}
                ]
            }).to_list(length=10)
            
            # Convert ObjectId to string for JSON serialization
            for fare in fares:
                if "_id" in fare:
                    fare["_id"] = str(fare["_id"])
            return fares
            
        except Exception as e:
            print(f"Error getting route fares: {e}")
            return []
    
    async def _get_last_mile_options(
        self,
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """Get last mile connectivity options"""
        
        try:
            collection = db.database["last_mile_options"]
            
            # Get last mile options
            options = await collection.find({
                "$or": [
                    {"origin": {"$regex": origin, "$options": "i"}},
                    {"destination": {"$regex": destination, "$options": "i"}}
                ]
            }).to_list(length=5)
            
            # Convert ObjectId to string for JSON serialization
            for option in options:
                if "_id" in option:
                    option["_id"] = str(option["_id"])
        
            return options
            
        except Exception as e:
            print(f"Error getting last mile options: {e}")
            return []
    
    def _estimate_duration_from_stops(self, stops: List[str]) -> int:
        """Estimate duration based on number of stops"""
        # Rough estimation: 2 minutes per stop + 5 minutes base
        return len(stops) * 2 + 5
    
    async def get_route_with_preferences(
        self,
        origin: str,
        destination: str,
        mode: str,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get route optimized for user preferences"""
        
        try:
            # Get enhanced route
            enhanced_route = await self.get_enhanced_route(
                origin=origin,
                destination=destination,
                mode=mode,
                user_id=user_id
            )
            
            if not enhanced_route.get("success"):
                return enhanced_route
            
            # Apply preference scoring
            scored_routes = await self._score_routes_by_preferences(
                enhanced_route, preferences
            )
            
            # Sort routes by preference score
            scored_routes.sort(key=lambda x: x.get("preference_score", 0), reverse=True)
            
            enhanced_route["preference_ranked_routes"] = scored_routes
            enhanced_route["user_preferences"] = preferences
            
            return enhanced_route
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _score_routes_by_preferences(
        self,
        enhanced_route: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score routes based on user preferences"""
        
        scored_routes = []
        
        try:
            # Score primary route
            primary_score = self._calculate_preference_score(
                enhanced_route["primary_route"], preferences
            )
            
            scored_routes.append({
                "route": enhanced_route["primary_route"],
                "type": "primary",
                "preference_score": primary_score
            })
            
            # Score supplementary routes
            for route in enhanced_route.get("supplementary_routes", []):
                score = self._calculate_preference_score(route, preferences)
                scored_routes.append({
                    "route": route,
                    "type": "supplementary",
                    "preference_score": score
                })
            
        except Exception as e:
            print(f"Error scoring routes: {e}")
        
        return scored_routes
    
    def _calculate_preference_score(
        self,
        route: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> float:
        """Calculate preference score for a route"""
        
        score = 0.5  # Default neutral score
        
        try:
            # Cost preference
            if "cost" in preferences:
                cost_pref = preferences["cost"]
                if "max_fare" in cost_pref:
                    # This is simplified - would need actual fare data
                    estimated_cost = 50  # Placeholder
                    if estimated_cost <= cost_pref["max_fare"]:
                        score += 0.2
                    else:
                        score -= 0.2
            
            # Time preference
            if "time" in preferences:
                time_pref = preferences["time"]
                if "max_duration" in time_pref:
                    # Extract duration from route
                    duration_text = route.get("duration_text", "0 min")
                    try:
                        duration = int(duration_text.split()[0])
                        if duration <= time_pref["max_duration"]:
                            score += 0.2
                        else:
                            score -= 0.2
                    except:
                        pass
            
            # Safety preference
            if "safety" in preferences:
                safety_pref = preferences["safety"]
                if safety_pref.get("avoid_night_travel", False):
                    current_hour = datetime.now(ZoneInfo("Asia/Colombo")).hour
                    if 6 <= current_hour <= 22:
                        score += 0.1
                    else:
                        score -= 0.1
            
            # Normalize score to 0-1 range
            score = max(0.0, min(1.0, score))
            
        except Exception as e:
            print(f"Error calculating preference score: {e}")
        
        return score
