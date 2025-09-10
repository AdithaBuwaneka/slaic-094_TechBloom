# Sri Lanka Transit Data Service for SLAIC 2025
# Mock implementation of Sri Lankan transit data sources as specified in the challenge requirements

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

class SriLankanTransitService:
    """
    Mock Sri Lankan Transit Data Service implementing the data sources specified in SLAIC 2025:
    - Sri Lanka Railways Location API
    - Inter-Provincial Bus Timetables (NTC)
    - Inter-Provincial Bus Route Maps (NTC) 
    - Inter-Provincial Bus Fares (NTC)
    - GTFS Standard compliance
    """
    
    def __init__(self):
        self.available = True
        print("Sri Lankan Transit Service initialized with mock data")
    
    def get_railway_realtime_data(self, route: str = None) -> Dict[str, Any]:
        """
        Mock Sri Lanka Railways Location API - Real-time train GPS data
        """
        try:
            # Mock train data for major routes
            trains = [
                {
                    "train_id": "train_001",
                    "name": "Podi Menike",
                    "route": "Colombo Fort - Kandy",
                    "current_location": {"lat": 7.2906, "lng": 80.6337},
                    "status": "on_time",
                    "next_station": "Peradeniya",
                    "delay_minutes": 0,
                    "estimated_arrival": "14:30",
                    "car_count": 8,
                    "occupancy": "medium"
                },
                {
                    "train_id": "train_002", 
                    "name": "Intercity Express",
                    "route": "Colombo Fort - Kandy",
                    "current_location": {"lat": 6.9271, "lng": 79.8612},
                    "status": "delayed",
                    "next_station": "Colombo Fort",
                    "delay_minutes": 15,
                    "estimated_arrival": "09:45",
                    "car_count": 6,
                    "occupancy": "high"
                },
                {
                    "train_id": "train_003",
                    "name": "Udarata Menike",
                    "route": "Colombo Fort - Badulla",
                    "current_location": {"lat": 7.0873, "lng": 80.2784},
                    "status": "on_time", 
                    "next_station": "Hatton",
                    "delay_minutes": 0,
                    "estimated_arrival": "16:15",
                    "car_count": 10,
                    "occupancy": "low"
                }
            ]
            
            if route:
                trains = [t for t in trains if route.lower() in t["route"].lower()]
            
            return {
                "status": "success",
                "data": trains,
                "timestamp": datetime.now().isoformat(),
                "source": "Sri Lanka Railways Location API"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_bus_timetables(self, route: str = None) -> Dict[str, Any]:
        """
        Mock Inter-Provincial Bus Timetables regulated by NTC
        """
        try:
            # Mock bus timetables for major inter-provincial routes
            timetables = [
                {
                    "route_id": "bus_route_001",
                    "route_name": "Colombo - Kandy",
                    "operator": "SLTB",
                    "bus_type": "Normal",
                    "departures": [
                        {"time": "06:00", "bus_number": "138-2156", "fare": 120},
                        {"time": "06:30", "bus_number": "138-2157", "fare": 120},
                        {"time": "07:00", "bus_number": "138-2158", "fare": 120},
                        {"time": "08:00", "bus_number": "138-2159", "fare": 120},
                        {"time": "09:00", "bus_number": "138-2160", "fare": 120}
                    ],
                    "duration_minutes": 180,
                    "frequency": "30 minutes"
                },
                {
                    "route_id": "bus_route_002",
                    "route_name": "Colombo - Galle",
                    "operator": "Private",
                    "bus_type": "Air Conditioned",
                    "departures": [
                        {"time": "05:30", "bus_number": "PA-1234", "fare": 200},
                        {"time": "06:15", "bus_number": "PA-1235", "fare": 200},
                        {"time": "07:00", "bus_number": "PA-1236", "fare": 200},
                        {"time": "08:00", "bus_number": "PA-1237", "fare": 200}
                    ],
                    "duration_minutes": 150,
                    "frequency": "45 minutes"
                },
                {
                    "route_id": "bus_route_003",
                    "route_name": "Colombo - Anuradhapura",
                    "operator": "SLTB",
                    "bus_type": "Semi-Luxury",
                    "departures": [
                        {"time": "06:30", "bus_number": "NC-5678", "fare": 300},
                        {"time": "08:00", "bus_number": "NC-5679", "fare": 300},
                        {"time": "10:00", "bus_number": "NC-5680", "fare": 300},
                        {"time": "14:00", "bus_number": "NC-5681", "fare": 300}
                    ],
                    "duration_minutes": 240,
                    "frequency": "2 hours"
                }
            ]
            
            if route:
                timetables = [t for t in timetables if route.lower() in t["route_name"].lower()]
            
            return {
                "status": "success",
                "data": timetables,
                "timestamp": datetime.now().isoformat(),
                "source": "NTC Inter-Provincial Bus Timetables"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_bus_route_maps(self, route_id: str = None) -> Dict[str, Any]:
        """
        Mock Inter-Provincial Bus Route Maps regulated by NTC
        """
        try:
            route_maps = [
                {
                    "route_id": "bus_route_001",
                    "route_name": "Colombo - Kandy",
                    "stops": [
                        {"stop_id": "COL001", "name": "Pettah Bus Stand", "lat": 6.9388, "lng": 79.8653},
                        {"stop_id": "COL002", "name": "Kiribathgoda", "lat": 6.9804, "lng": 79.9297},
                        {"stop_id": "COL003", "name": "Kadawatha", "lat": 7.0092, "lng": 79.9461},
                        {"stop_id": "KAN001", "name": "Peradeniya", "lat": 7.2599, "lng": 80.5977},
                        {"stop_id": "KAN002", "name": "Kandy Bus Stand", "lat": 7.2906, "lng": 80.6337}
                    ],
                    "distance_km": 115,
                    "estimated_duration": 180
                },
                {
                    "route_id": "bus_route_002", 
                    "route_name": "Colombo - Galle",
                    "stops": [
                        {"stop_id": "COL001", "name": "Pettah Bus Stand", "lat": 6.9388, "lng": 79.8653},
                        {"stop_id": "GAL001", "name": "Kalutara", "lat": 6.5821, "lng": 79.9593},
                        {"stop_id": "GAL002", "name": "Aluthgama", "lat": 6.4253, "lng": 79.9956},
                        {"stop_id": "GAL003", "name": "Hikkaduwa", "lat": 6.1421, "lng": 80.0992},
                        {"stop_id": "GAL004", "name": "Galle Bus Stand", "lat": 6.0535, "lng": 80.2210}
                    ],
                    "distance_km": 119,
                    "estimated_duration": 150
                }
            ]
            
            if route_id:
                route_maps = [r for r in route_maps if r["route_id"] == route_id]
            
            return {
                "status": "success",
                "data": route_maps,
                "timestamp": datetime.now().isoformat(),
                "source": "NTC Inter-Provincial Bus Route Maps"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_bus_fares(self, route: str = None, bus_type: str = None) -> Dict[str, Any]:
        """
        Mock Inter-Provincial Bus Fares regulated by NTC
        """
        try:
            fare_data = [
                {
                    "route": "Colombo - Kandy",
                    "bus_types": {
                        "normal": {
                            "base_fare": 120,
                            "fare_per_km": 1.0,
                            "student_discount": 0.5,
                            "senior_discount": 0.3
                        },
                        "semi_luxury": {
                            "base_fare": 180,
                            "fare_per_km": 1.5,
                            "student_discount": 0.3,
                            "senior_discount": 0.2
                        },
                        "air_conditioned": {
                            "base_fare": 250,
                            "fare_per_km": 2.0,
                            "student_discount": 0.2,
                            "senior_discount": 0.1
                        }
                    }
                },
                {
                    "route": "Colombo - Galle",
                    "bus_types": {
                        "normal": {
                            "base_fare": 150,
                            "fare_per_km": 1.2,
                            "student_discount": 0.5,
                            "senior_discount": 0.3
                        },
                        "air_conditioned": {
                            "base_fare": 200,
                            "fare_per_km": 1.8,
                            "student_discount": 0.2,
                            "senior_discount": 0.1
                        }
                    }
                },
                {
                    "route": "Colombo - Anuradhapura",
                    "bus_types": {
                        "normal": {
                            "base_fare": 200,
                            "fare_per_km": 1.5,
                            "student_discount": 0.5,
                            "senior_discount": 0.3
                        },
                        "semi_luxury": {
                            "base_fare": 300,
                            "fare_per_km": 2.0,
                            "student_discount": 0.3,
                            "senior_discount": 0.2
                        }
                    }
                }
            ]
            
            if route:
                fare_data = [f for f in fare_data if route.lower() in f["route"].lower()]
            
            return {
                "status": "success",
                "data": fare_data,
                "timestamp": datetime.now().isoformat(),
                "source": "NTC Inter-Provincial Bus Fares"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_gtfs_data(self, agency: str = None) -> Dict[str, Any]:
        """
        Mock GTFS Standard data for structuring transport schedules
        """
        try:
            gtfs_data = {
                "agency": [
                    {"agency_id": "SLTB", "agency_name": "Sri Lanka Transport Board", "agency_url": "http://sltb.lk"},
                    {"agency_id": "SLR", "agency_name": "Sri Lanka Railways", "agency_url": "http://railway.gov.lk"}
                ],
                "routes": [
                    {
                        "route_id": "bus_001",
                        "agency_id": "SLTB",
                        "route_short_name": "138",
                        "route_long_name": "Colombo - Kandy Express",
                        "route_type": 3  # Bus
                    },
                    {
                        "route_id": "train_001", 
                        "agency_id": "SLR",
                        "route_short_name": "PM",
                        "route_long_name": "Podi Menike",
                        "route_type": 2  # Rail
                    }
                ],
                "stops": [
                    {"stop_id": "COL_PETTAH", "stop_name": "Pettah Bus Stand", "stop_lat": 6.9388, "stop_lng": 79.8653},
                    {"stop_id": "COL_FORT", "stop_name": "Colombo Fort Railway", "stop_lat": 6.9344, "stop_lng": 79.8428},
                    {"stop_id": "KAN_BUS", "stop_name": "Kandy Bus Stand", "stop_lat": 7.2906, "stop_lng": 80.6337},
                    {"stop_id": "KAN_RAIL", "stop_name": "Kandy Railway Station", "stop_lat": 7.2935, "stop_lng": 80.6353}
                ],
                "stop_times": [
                    {"trip_id": "trip_001", "arrival_time": "06:00:00", "departure_time": "06:00:00", "stop_id": "COL_PETTAH", "stop_sequence": 1},
                    {"trip_id": "trip_001", "arrival_time": "09:00:00", "departure_time": "09:00:00", "stop_id": "KAN_BUS", "stop_sequence": 2}
                ]
            }
            
            if agency:
                gtfs_data["routes"] = [r for r in gtfs_data["routes"] if r["agency_id"] == agency]
            
            return {
                "status": "success",
                "data": gtfs_data,
                "timestamp": datetime.now().isoformat(),
                "source": "GTFS Standard Mock Data"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_live_disruptions(self) -> Dict[str, Any]:
        """
        Mock live disruption data for Sri Lankan transit
        """
        try:
            # Simulate random disruptions
            disruptions = []
            
            if random.random() < 0.3:  # 30% chance of disruption
                disruptions.append({
                    "disruption_id": "DISR_001",
                    "type": "construction", 
                    "route": "Colombo - Kandy",
                    "location": "Kadawatha Junction",
                    "severity": "medium",
                    "description": "Road construction causing 15-minute delays",
                    "estimated_delay_minutes": 15,
                    "alternative_routes": ["A001", "A003"],
                    "start_time": datetime.now().isoformat(),
                    "estimated_end": (datetime.now() + timedelta(hours=2)).isoformat()
                })
            
            return {
                "status": "success",
                "data": disruptions,
                "timestamp": datetime.now().isoformat(),
                "source": "Sri Lanka Transit Disruption Monitor"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Initialize global service instance
sri_lanka_transit_service = SriLankanTransitService()