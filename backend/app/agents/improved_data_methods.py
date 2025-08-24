"""
Improved data methods for Smart Transit Companion
Provides intelligent mock data and real API integration
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from app.models.transport_data import (
    Location, TransportMode, DataSource, ScheduleEntry, RoutePoint
)
from app.core.config import settings


class ImprovedDataMethods:
    """Enhanced data fetching methods with smart mock data generation"""
    
    def __init__(self, external_api_service=None):
        self.external_api_service = external_api_service
        
    async def fetch_railway_data(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Fetch railway data - Uses external API service or intelligent mock data"""
        
        try:
            if settings.USE_MOCK_DATA:
                # Intelligent mock data based on actual Sri Lankan railway routes
                return await self._generate_smart_railway_mock(origin, destination)
            else:
                # Real API call via external service
                if self.external_api_service:
                    params = {
                        "origin_lat": origin.latitude,
                        "origin_lng": origin.longitude,
                        "origin_name": origin.name or "Origin"
                    }
                    
                    if destination:
                        params.update({
                            "dest_lat": destination.latitude,
                            "dest_lng": destination.longitude, 
                            "dest_name": destination.name or "Destination"
                        })
                    
                    response = await self.external_api_service.make_api_request(
                        "sri_lanka_railways",
                        "routes/search",
                        params
                    )
                    
                    if response.success:
                        return self._process_railway_api_response(response.data, origin, destination)
                    else:
                        # Fallback to mock data if API fails
                        return await self._generate_smart_railway_mock(origin, destination)
                else:
                    # No API service, use mock data
                    return await self._generate_smart_railway_mock(origin, destination)
                    
        except Exception as e:
            # Fallback to mock data on error
            return await self._generate_smart_railway_mock(origin, destination)

    async def fetch_bus_data(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Fetch bus data - Uses external API service or intelligent mock data"""
        
        try:
            if settings.USE_MOCK_DATA:
                # Intelligent mock data based on actual Sri Lankan bus routes
                return await self._generate_smart_bus_mock(origin, destination)
            else:
                # Real API call via external service
                if self.external_api_service:
                    params = {
                        "from_lat": origin.latitude,
                        "from_lng": origin.longitude,
                        "from_name": origin.name or "Origin"
                    }
                    
                    if destination:
                        params.update({
                            "to_lat": destination.latitude,
                            "to_lng": destination.longitude,
                            "to_name": destination.name or "Destination" 
                        })
                    
                    response = await self.external_api_service.make_api_request(
                        "sltb",
                        "schedules/search",
                        params
                    )
                    
                    if response.success:
                        return self._process_bus_api_response(response.data, origin, destination)
                    else:
                        # Fallback to mock data if API fails
                        return await self._generate_smart_bus_mock(origin, destination)
                else:
                    # No API service, use mock data
                    return await self._generate_smart_bus_mock(origin, destination)
                    
        except Exception as e:
            # Fallback to mock data on error
            return await self._generate_smart_bus_mock(origin, destination)

    async def _generate_smart_railway_mock(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Generate intelligent mock railway data based on actual Sri Lankan routes"""
        
        # Simulate realistic API delay
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Smart route generation based on Sri Lankan railway network
        routes = []
        
        # Major railway stations in Sri Lanka with real coordinates
        major_stations = {
            "Colombo Fort": {"lat": 6.9344, "lng": 79.8428, "province": "Western"},
            "Kandy": {"lat": 7.2906, "lng": 80.6337, "province": "Central"},
            "Galle": {"lat": 6.0329, "lng": 80.2168, "province": "Southern"},
            "Jaffna": {"lat": 9.6615, "lng": 80.0255, "province": "Northern"},
            "Batticaloa": {"lat": 7.7102, "lng": 81.6924, "province": "Eastern"},
            "Badulla": {"lat": 6.9934, "lng": 81.0550, "province": "Uva"},
            "Anuradhapura": {"lat": 8.3114, "lng": 80.4037, "province": "North Central"},
            "Matara": {"lat": 5.9485, "lng": 80.5353, "province": "Southern"}
        }
        
        # Railway line templates based on actual Sri Lankan railway network
        route_templates = [
            {
                "route_name": "Main Line Express",
                "operator": "Sri Lanka Railways",
                "line": "Main Line",
                "service_type": "Express",
                "stations": ["Colombo Fort", "Kandy", "Badulla"],
                "fare_per_km": 2.5
            },
            {
                "route_name": "Coastal Line Service", 
                "operator": "Sri Lanka Railways",
                "line": "Coastal Line",
                "service_type": "Regular",
                "stations": ["Colombo Fort", "Galle", "Matara"],
                "fare_per_km": 2.0
            },
            {
                "route_name": "Northern Line Express",
                "operator": "Sri Lanka Railways", 
                "line": "Northern Line",
                "service_type": "Express",
                "stations": ["Colombo Fort", "Anuradhapura", "Jaffna"],
                "fare_per_km": 3.0
            },
            {
                "route_name": "Puttalam Line Service",
                "operator": "Sri Lanka Railways",
                "line": "Puttalam Line", 
                "service_type": "Regular",
                "stations": ["Colombo Fort", "Negombo", "Puttalam"],
                "fare_per_km": 1.8
            }
        ]
        
        # Generate realistic routes based on origin location
        selected_templates = random.sample(route_templates, min(3, len(route_templates)))
        
        for i, template in enumerate(selected_templates):
            route_id = f"railway_{str(i+1).zfill(3)}"
            
            # Calculate realistic distance (approximate)
            if destination:
                distance = self._calculate_distance(origin, destination)
            else:
                distance = random.uniform(50, 300)
            
            # Generate realistic schedule based on time of day and distance
            now = datetime.utcnow()
            departure_times = []
            
            # Express trains run less frequently but faster
            if template["service_type"] == "Express":
                intervals = [2, 6, 12, 18]  # Hours
                travel_time_factor = 0.7
            else:
                intervals = [1, 3, 6, 9, 12]  # Hours  
                travel_time_factor = 1.0
                
            for hour_offset in intervals:
                departure_time = now + timedelta(hours=hour_offset)
                
                # Calculate travel time based on distance and service type
                base_travel_time = distance / 60 * travel_time_factor  # Assume 60km/h average
                travel_time_minutes = int(base_travel_time * 60 + random.uniform(-30, 60))
                
                arrival_time = departure_time + timedelta(minutes=travel_time_minutes)
                
                departure_times.append({
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "stop_id": f"STA{str(i+1).zfill(3)}",
                    "stop_name": origin.name or f"{template['line']} Station",
                    "sequence": 0,
                    "delay_minutes": random.randint(0, 45),  # Realistic Sri Lankan railway delays
                    "status": random.choice(["scheduled", "delayed", "on_time", "cancelled"]),
                    "platform": random.randint(1, 4),
                    "coach_composition": f"{random.randint(6, 12)} coaches"
                })
            
            # Calculate realistic fare
            base_fare = distance * template["fare_per_km"]
            fare = round(base_fare + random.uniform(-20, 50), 2)
            
            route = {
                "route_id": route_id,
                "route_name": template["route_name"],
                "transport_mode": TransportMode.TRAIN,
                "operator": template["operator"],
                "service_type": template["service_type"],
                "line_name": template["line"],
                "route_points": [
                    {
                        "location": {"latitude": origin.latitude, "longitude": origin.longitude},
                        "stop_name": origin.name or f"{template['line']} Origin Station",
                        "stop_id": f"STA{str(i+1).zfill(3)}",
                        "sequence": 0,
                        "platform": random.randint(1, 4),
                        "facilities": random.sample(["Ticket Counter", "Waiting Room", "Restroom", "Snack Bar", "ATM"], k=3)
                    }
                ],
                "schedule": departure_times,
                "fare": max(25.0, fare),  # Minimum fare of Rs. 25
                "distance_km": round(distance, 1),
                "average_duration_minutes": int(distance / 60 * travel_time_factor * 60),
                "last_updated": datetime.utcnow(),
                "data_source": DataSource.RAILWAYS_API,
                "reliability_score": round(random.uniform(0.75, 0.95), 2),
                "facilities": random.sample([
                    "Air Conditioning", "Reserved Seating", "Dining Car", 
                    "Observation Car", "WiFi", "Power Outlets"
                ], k=random.randint(2, 4)),
                "class_types": ["Third Class", "Second Class", "First Class", "Observation Saloon"],
                "booking_advance_days": random.randint(30, 60),
                "cancellation_policy": "Full refund 24 hours before departure"
            }
            routes.append(route)
        
        return {
            "type": "routes",
            "data": routes,
            "metadata": {
                "source": DataSource.RAILWAYS_API,
                "freshness_minutes": 2,
                "completeness_score": 0.9,
                "accuracy_score": 0.85,
                "reliability_score": 0.85,
                "last_validated": datetime.utcnow(),
                "data_mode": "smart_mock",
                "region": "Sri Lanka",
                "network_coverage": "Major railway lines"
            }
        }

    async def _generate_smart_bus_mock(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Generate intelligent mock bus data based on actual Sri Lankan routes"""
        
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        routes = []
        
        # Common Sri Lankan bus operators and route types
        operators = [
            {
                "name": "SLTB", 
                "route_type": "Inter-Provincial",
                "service_classes": ["Normal", "Semi-Luxury"],
                "fare_per_km": 4.0,
                "reliability": 0.75
            },
            {
                "name": "Private Bus (CTB)",
                "route_type": "Provincial", 
                "service_classes": ["Normal", "Semi-Luxury"],
                "fare_per_km": 5.0,
                "reliability": 0.70
            },
            {
                "name": "Luxury Express",
                "route_type": "Express",
                "service_classes": ["Air-Conditioned", "Super Luxury"],
                "fare_per_km": 8.0,
                "reliability": 0.85
            }
        ]
        
        # Generate routes for different operators
        for i, operator in enumerate(operators):
            route_id = f"bus_{str(100 + i)}"
            
            # Calculate distance
            if destination:
                distance = self._calculate_distance(origin, destination)
            else:
                distance = random.uniform(20, 200)
            
            # Generate realistic schedules - buses run more frequently than trains
            now = datetime.utcnow()
            departure_times = []
            
            # Different frequency based on route type
            if operator["route_type"] == "Express":
                intervals = [30, 60, 120, 180, 300]  # Minutes
            else:
                intervals = [15, 30, 45, 60, 90, 120]  # Minutes
                
            for minute_offset in intervals:
                departure_time = now + timedelta(minutes=minute_offset)
                
                # Bus travel time calculation (slower than trains)
                average_speed = 45 if operator["route_type"] == "Express" else 35  # km/h
                travel_duration = (distance / average_speed) * 60  # minutes
                travel_duration += random.uniform(-15, 30)  # Traffic variation
                
                arrival_time = departure_time + timedelta(minutes=travel_duration)
                
                departure_times.append({
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "stop_id": f"BS{str(i+1).zfill(3)}",
                    "stop_name": origin.name or f"{operator['name']} Bus Stop",
                    "sequence": 0,
                    "delay_minutes": random.randint(0, 30),  # Realistic bus delays
                    "status": random.choice(["scheduled", "delayed", "departed", "on_time"]),
                    "bay_number": random.randint(1, 8),
                    "bus_number": f"{operator['name'][:2]}-{random.randint(1000, 9999)}"
                })
            
            # Calculate fare
            service_class = random.choice(operator["service_classes"])
            base_fare = distance * operator["fare_per_km"]
            
            # Adjust fare based on service class
            if "Luxury" in service_class or "AC" in service_class:
                fare_multiplier = 1.5
            elif "Semi-Luxury" in service_class:
                fare_multiplier = 1.2
            else:
                fare_multiplier = 1.0
                
            fare = round(base_fare * fare_multiplier, 2)
            
            route = {
                "route_id": route_id,
                "route_name": f"{origin.name or 'Origin'} - {destination.name if destination else 'Express'}",
                "transport_mode": TransportMode.BUS,
                "operator": operator["name"],
                "route_type": operator["route_type"],
                "service_class": service_class,
                "route_points": [
                    {
                        "location": {"latitude": origin.latitude, "longitude": origin.longitude},
                        "stop_name": origin.name or f"{operator['name']} Bus Stop",
                        "stop_id": f"BS{str(i+1).zfill(3)}",
                        "sequence": 0,
                        "bay_number": random.randint(1, 8),
                        "stop_facilities": random.sample([
                            "Shelter", "Seating", "Restroom", "Snack Bar", 
                            "ATM", "Information Desk", "Parking"
                        ], k=random.randint(2, 4))
                    }
                ],
                "schedule": departure_times,
                "fare": max(30.0, fare),  # Minimum bus fare Rs. 30
                "distance_km": round(distance, 1),
                "duration_minutes": int(travel_duration),
                "last_updated": datetime.utcnow(),
                "data_source": DataSource.BUS_API,
                "reliability_score": operator["reliability"],
                "vehicle_features": self._get_vehicle_features(service_class),
                "capacity": random.randint(45, 55),
                "accessibility": random.choice([True, False]),
                "booking_required": operator["route_type"] == "Express",
                "payment_methods": ["Cash", "Smart Card", "Mobile Payment"]
            }
            routes.append(route)
        
        return {
            "type": "routes",
            "data": routes,
            "metadata": {
                "source": DataSource.BUS_API,
                "freshness_minutes": 1,
                "completeness_score": 0.8,
                "accuracy_score": 0.75,
                "reliability_score": 0.75,
                "last_validated": datetime.utcnow(),
                "data_mode": "smart_mock",
                "region": "Sri Lanka",
                "network_coverage": "Inter and Intra-provincial routes"
            }
        }

    def _get_vehicle_features(self, service_class: str) -> List[str]:
        """Get realistic vehicle features based on service class"""
        base_features = ["GPS Tracking", "First Aid Kit"]
        
        if "Luxury" in service_class or "AC" in service_class:
            return base_features + ["Air Conditioning", "WiFi", "USB Charging", 
                                   "Reclining Seats", "Entertainment System", "Snack Service"]
        elif "Semi-Luxury" in service_class:
            return base_features + ["Air Conditioning", "USB Charging", "Comfortable Seating"]
        else:
            return base_features + ["Basic Seating", "Windows"]

    def _calculate_distance(self, origin: Location, destination: Location) -> float:
        """Calculate approximate distance between two points (simplified)"""
        import math
        
        # Simple haversine distance calculation
        lat1, lon1 = math.radians(origin.latitude), math.radians(origin.longitude)
        lat2, lon2 = math.radians(destination.latitude), math.radians(destination.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return r * c

    def _process_railway_api_response(self, api_data: Dict[str, Any], origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Process real railway API response into standardized format"""
        routes = []
        
        for route_data in api_data.get("routes", []):
            # Convert API response to our standard format
            route = {
                "route_id": route_data.get("id", f"api_route_{random.randint(1000, 9999)}"),
                "route_name": route_data.get("name", "Railway Service"),
                "transport_mode": TransportMode.TRAIN,
                "operator": route_data.get("operator", "Sri Lanka Railways"),
                "service_type": route_data.get("service_type", "Regular"),
                "fare": route_data.get("fare", 0),
                "distance_km": route_data.get("distance", 0),
                "duration_minutes": route_data.get("duration", 0),
                "last_updated": datetime.utcnow(),
                "data_source": DataSource.RAILWAYS_API
            }
            routes.append(route)
        
        return {
            "type": "routes", 
            "data": routes,
            "metadata": {
                "source": DataSource.RAILWAYS_API,
                "data_mode": "real_api",
                "last_validated": datetime.utcnow()
            }
        }

    def _process_bus_api_response(self, api_data: Dict[str, Any], origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Process real bus API response into standardized format"""
        routes = []
        
        for route_data in api_data.get("schedules", []):
            # Convert API response to our standard format
            route = {
                "route_id": route_data.get("route_id", f"api_bus_{random.randint(1000, 9999)}"),
                "route_name": route_data.get("route_name", "Bus Service"),
                "transport_mode": TransportMode.BUS,
                "operator": route_data.get("operator", "SLTB"),
                "route_type": route_data.get("route_type", "Regular"),
                "fare": route_data.get("fare", 0),
                "distance_km": route_data.get("distance", 0),
                "duration_minutes": route_data.get("duration", 0),
                "last_updated": datetime.utcnow(),
                "data_source": DataSource.BUS_API
            }
            routes.append(route)
        
        return {
            "type": "routes",
            "data": routes,
            "metadata": {
                "source": DataSource.BUS_API,
                "data_mode": "real_api", 
                "last_validated": datetime.utcnow()
            }
        }