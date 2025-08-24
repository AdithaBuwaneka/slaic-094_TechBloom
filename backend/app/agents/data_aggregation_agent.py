from app.agents.base_agent import BaseAgent
from app.models.transport_data import (
    RouteData, WeatherData, TrafficData, DataQualityMetrics, 
    AggregatedTransportData, Location, TransportMode, DataSource,
    ScheduleEntry, RoutePoint
)
from app.services.external_api_service import ExternalAPIService
from app.agents.improved_data_methods import ImprovedDataMethods
from app.core.config import settings
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random


class DataAggregationAgent(BaseAgent):
    """
    Data Aggregation Agent - Unified Real-time Data Collection
    
    Primary Functions:
    - Multi-source data integration
    - Real-time feed processing and normalization  
    - Historical data pattern analysis
    - Data quality assessment and filtering
    """
    
    def __init__(self):
        super().__init__(
            agent_id="data_aggregation_agent",
            name="Data Aggregation Agent",
            priority_weight=0.9  # High priority for data collection
        )
        
        # Cache for storing recent data
        self.data_cache = {}
        self.cache_ttl = 300  # 5 minutes TTL
        
        # Initialize external API service and improved data methods
        self.external_api_service = ExternalAPIService()
        self.improved_data_methods = ImprovedDataMethods(self.external_api_service)
        
        # Data source configurations (now using external API service)
        self.data_sources = {
            DataSource.RAILWAYS_API: {
                "api_id": "sri_lanka_railways",
                "enabled": True,
                "timeout": 5.0,
                "retry_count": 2
            },
            DataSource.BUS_API: {
                "api_id": "sltb", 
                "enabled": True,
                "timeout": 5.0,
                "retry_count": 2
            },
            DataSource.WEATHER_API: {
                "api_id": "openweather",
                "enabled": True,
                "timeout": 3.0,
                "retry_count": 1
            },
            DataSource.TRAFFIC_API: {
                "api_id": "google_traffic",
                "enabled": True,
                "timeout": 3.0,
                "retry_count": 1
            }
        }
        
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for data aggregation requests"""
        
        request_type = payload.get("request_type", "")
        data = payload.get("data", {})
        
        if request_type == "get_transport_data":
            return await self._aggregate_transport_data(data)
        elif request_type == "get_weather_data":
            return await self._get_weather_data(data)
        elif request_type == "get_traffic_data":
            return await self._get_traffic_data(data)
        elif request_type == "validate_data_sources":
            return await self._validate_data_sources()
        elif request_type == "get_route_schedules":
            return await self._get_route_schedules(data)
        else:
            return {
                "status": "unknown_request",
                "message": f"Unknown request type: {request_type}",
                "supported_requests": [
                    "get_transport_data", "get_weather_data", 
                    "get_traffic_data", "validate_data_sources",
                    "get_route_schedules"
                ]
            }
            
    async def _aggregate_transport_data(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate transport data from multiple sources"""
        
        query_id = query_data.get("query_id", f"query_{datetime.utcnow().isoformat()}")
        origin_data = query_data.get("origin", {})
        destination_data = query_data.get("destination", {})
        transport_modes = query_data.get("transport_modes", ["bus", "train"])
        
        # Parse locations
        try:
            origin = Location(**origin_data)
            destination = Location(**destination_data) if destination_data else None
        except Exception as e:
            return {
                "status": "error",
                "message": f"Invalid location data: {str(e)}",
                "query_id": query_id
            }
            
        # Check cache first
        cache_key = f"{origin.latitude},{origin.longitude}_{destination.latitude if destination else 'none'},{destination.longitude if destination else 'none'}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return {
                "status": "success",
                "data": cached_data,
                "source": "cache",
                "query_id": query_id
            }
            
        # Fetch data from multiple sources concurrently
        tasks = []
        
        if TransportMode.TRAIN in transport_modes:
            tasks.append(self._fetch_railway_data(origin, destination))
        if TransportMode.BUS in transport_modes:
            tasks.append(self._fetch_bus_data(origin, destination))
            
        # Also fetch supporting data
        tasks.append(self._fetch_weather_data(origin))
        tasks.append(self._fetch_traffic_data(origin, destination))
        
        # Execute all data fetching tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        routes = []
        weather = None
        traffic = []
        quality_metrics = []
        successful_sources = 0
        total_sources = len([t for t in tasks if not str(t).startswith("_fetch_weather") and not str(t).startswith("_fetch_traffic")])
        
        for result in results:
            if isinstance(result, Exception):
                continue
                
            if result.get("type") == "routes":
                routes.extend(result.get("data", []))
                successful_sources += 1
            elif result.get("type") == "weather":
                weather = result.get("data")
            elif result.get("type") == "traffic":
                traffic.extend(result.get("data", []))
                
            # Add quality metrics
            if "quality_metrics" in result:
                quality_metrics.extend(result["quality_metrics"])
                
        # Create aggregated response
        aggregated_data = AggregatedTransportData(
            query_id=query_id,
            origin=origin,
            destination=destination,
            transport_modes=transport_modes,
            routes=routes,
            weather=weather,
            traffic=traffic,
            quality_metrics=quality_metrics,
            total_sources=total_sources,
            successful_sources=successful_sources
        )
        
        # Cache the result
        self._cache_data(cache_key, aggregated_data.dict())
        
        return {
            "status": "success",
            "data": aggregated_data.dict(),
            "source": "live_aggregation",
            "query_id": query_id,
            "processing_summary": {
                "total_sources": total_sources,
                "successful_sources": successful_sources,
                "routes_found": len(routes),
                "weather_available": weather is not None,
                "traffic_data_points": len(traffic)
            }
        }
        
    async def _fetch_railway_data(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Fetch railway data - Uses improved data methods with smart mock or real APIs"""
        
        # Use improved data methods for better railway data
        return await self.improved_data_methods.fetch_railway_data(origin, destination)
        
    async def _fetch_bus_data(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Fetch bus data - Uses improved data methods with smart mock or real APIs"""
        
        # Use improved data methods for better bus data
        return await self.improved_data_methods.fetch_bus_data(origin, destination)
        
    async def _fetch_weather_data(self, location: Location) -> Dict[str, Any]:
        """Fetch weather data - Mock implementation"""
        
        await asyncio.sleep(0.1)
        
        mock_weather = {
            "location": location.dict(),
            "temperature_celsius": random.randint(24, 32),
            "humidity_percent": random.randint(60, 85),
            "rainfall_mm": random.uniform(0, 10) if random.random() < 0.3 else 0,
            "wind_speed_kmh": random.uniform(5, 20),
            "weather_condition": random.choice(["sunny", "cloudy", "partly_cloudy", "light_rain"]),
            "timestamp": datetime.utcnow()
        }
        
        return {
            "type": "weather",
            "data": mock_weather
        }
        
    async def _fetch_traffic_data(self, origin: Location, destination: Optional[Location]) -> Dict[str, Any]:
        """Fetch traffic data - Mock implementation"""
        
        await asyncio.sleep(0.1)
        
        mock_traffic = [
            {
                "location": origin.dict(),
                "traffic_level": random.choice(["light", "moderate", "heavy"]),
                "speed_kmh": random.uniform(20, 60),
                "incidents": [],
                "timestamp": datetime.utcnow()
            }
        ]
        
        return {
            "type": "traffic",
            "data": mock_traffic
        }
        
    async def _get_weather_data(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather data for specific location"""
        
        location_data = query_data.get("location", {})
        try:
            location = Location(**location_data)
            result = await self._fetch_weather_data(location)
            return {
                "status": "success",
                "data": result["data"]
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }
            
    async def _get_traffic_data(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get traffic data for route"""
        
        origin_data = query_data.get("origin", {})
        destination_data = query_data.get("destination", {})
        
        try:
            origin = Location(**origin_data)
            destination = Location(**destination_data) if destination_data else None
            result = await self._fetch_traffic_data(origin, destination)
            return {
                "status": "success",
                "data": result["data"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def _validate_data_sources(self) -> Dict[str, Any]:
        """Validate all configured data sources"""
        
        source_status = {}
        
        for source, config in self.data_sources.items():
            try:
                # Mock validation - in real implementation would ping the APIs
                await asyncio.sleep(0.05)
                source_status[source.value] = {
                    "status": "healthy" if config["enabled"] else "disabled",
                    "response_time_ms": random.uniform(50, 200),
                    "last_check": datetime.utcnow().isoformat(),
                    "url": config["url"]
                }
            except Exception as e:
                source_status[source.value] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                
        healthy_sources = len([s for s in source_status.values() if s["status"] == "healthy"])
        
        return {
            "status": "success",
            "summary": {
                "total_sources": len(self.data_sources),
                "healthy_sources": healthy_sources,
                "disabled_sources": len([s for s in source_status.values() if s["status"] == "disabled"]),
                "error_sources": len([s for s in source_status.values() if s["status"] == "error"])
            },
            "sources": source_status
        }
        
    async def _get_route_schedules(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get schedules for specific routes"""
        
        route_ids = query_data.get("route_ids", [])
        transport_mode = query_data.get("transport_mode", "bus")
        
        if not route_ids:
            return {
                "status": "error",
                "message": "No route IDs provided"
            }
            
        # Mock schedule data
        schedules = {}
        for route_id in route_ids:
            schedules[route_id] = {
                "route_id": route_id,
                "next_departures": [
                    {
                        "departure_time": (datetime.utcnow() + timedelta(minutes=random.randint(10, 60))).isoformat(),
                        "estimated_arrival": (datetime.utcnow() + timedelta(minutes=random.randint(70, 150))).isoformat(),
                        "delay_minutes": random.randint(0, 20),
                        "status": random.choice(["on_time", "delayed", "cancelled"])
                    }
                    for _ in range(3)
                ]
            }
            
        return {
            "status": "success",
            "data": schedules,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if still valid"""
        
        if cache_key in self.data_cache:
            cached_entry = self.data_cache[cache_key]
            if datetime.utcnow() - cached_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_entry["data"]
            else:
                # Remove expired entry
                del self.data_cache[cache_key]
        return None
        
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Store data in cache"""
        
        self.data_cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
        # Simple cache cleanup - remove old entries
        if len(self.data_cache) > 100:  # Max cache size
            oldest_key = min(self.data_cache.keys(), 
                           key=lambda k: self.data_cache[k]["timestamp"])
            del self.data_cache[oldest_key]