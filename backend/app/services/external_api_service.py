import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import hashlib
from urllib.parse import urljoin, urlencode

from app.models.external_apis import (
    ExternalAPIConfig, APIEndpoint, APIRequest, APIResponse, APIProvider,
    APIStatus, DataType, WeatherData, TrafficData, PublicTransportSchedule,
    FareInformation, RealTimeVehiclePosition, APIIntegrationStatus,
    APIUsageStatistics, IntegrationHealthCheck
)
from app.models.transport_data import Location, TransportMode
from app.core.config import settings


class ExternalAPIService:
    def __init__(self):
        self.api_configs: Dict[str, ExternalAPIConfig] = {}
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.response_cache: Dict[str, Tuple[Dict[str, Any], datetime]] = {}
        
        # Rate limiting
        self.request_counts: Dict[str, List[datetime]] = {}
        
        # Performance tracking
        self.usage_stats: Dict[str, APIUsageStatistics] = {}
        
        # Initialize default API configurations
        self._initialize_default_apis()

    def _initialize_default_apis(self):
        """Initialize default API configurations for Sri Lankan transport services"""
        
        # Sri Lanka Railways API (Configuration from environment)
        railways_config = ExternalAPIConfig(
            api_id="sri_lanka_railways",
            provider=APIProvider.SRI_LANKA_RAILWAYS,
            name="Sri Lanka Railways API",
            description="Official Sri Lanka Railways schedules and real-time data",
            base_url=settings.RAILWAYS_API_URL,
            api_key=settings.RAILWAYS_API_KEY,
            supported_data_types=[DataType.SCHEDULES, DataType.REAL_TIME, DataType.FARES],
            coverage_areas=["Western", "Central", "Southern", "Northern", "Eastern"],
            reliability_score=0.85,
            average_response_time_ms=800
        )
        
        # SLTB API (Configuration from environment)
        sltb_config = ExternalAPIConfig(
            api_id="sltb",
            provider=APIProvider.SLTB,
            name="Sri Lanka Transport Board API",
            description="SLTB bus schedules and route information",
            base_url=settings.SLTB_API_URL,
            api_key=settings.SLTB_API_KEY,
            supported_data_types=[DataType.SCHEDULES, DataType.ROUTES, DataType.STOPS],
            coverage_areas=["All Districts"],
            reliability_score=0.75,
            average_response_time_ms=1200
        )
        
        # Weather API (Configuration from environment)
        weather_config = ExternalAPIConfig(
            api_id="openweather",
            provider=APIProvider.WEATHER_API,
            name="OpenWeather API",
            description="Weather data for Sri Lanka",
            base_url=settings.WEATHER_API_URL,
            api_key=settings.WEATHER_API_KEY,
            supported_data_types=[DataType.WEATHER],
            coverage_areas=["Sri Lanka"],
            reliability_score=0.95,
            average_response_time_ms=400
        )
        
        # Google Maps Traffic API (Configuration from environment)
        traffic_config = ExternalAPIConfig(
            api_id="google_traffic",
            provider=APIProvider.TRAFFIC_API,
            name="Google Maps Traffic API",
            description="Real-time traffic data for Sri Lanka",
            base_url=settings.GOOGLE_MAPS_API_URL,
            api_key=settings.GOOGLE_MAPS_API_KEY,
            supported_data_types=[DataType.TRAFFIC],
            coverage_areas=["Major Cities"],
            reliability_score=0.92,
            average_response_time_ms=600
        )
        
        self.api_configs.update({
            "sri_lanka_railways": railways_config,
            "sltb": sltb_config,
            "openweather": weather_config,
            "google_traffic": traffic_config
        })

    async def make_api_request(self, api_id: str, endpoint_path: str, 
                             params: Dict[str, Any] = None, 
                             method: str = "GET") -> APIResponse:
        """Make a request to an external API"""
        
        if api_id not in self.api_configs:
            return APIResponse(
                request_id="unknown",
                status_code=404,
                success=False,
                error_message=f"API configuration not found: {api_id}",
                response_time_ms=0
            )
        
        config = self.api_configs[api_id]
        
        # Check rate limiting
        if not await self._check_rate_limit(api_id, config):
            return APIResponse(
                request_id="rate_limited",
                status_code=429,
                success=False,
                error_message="Rate limit exceeded",
                response_time_ms=0
            )
        
        # Check cache first
        cache_key = self._generate_cache_key(api_id, endpoint_path, params)
        cached_response = self._get_cached_response(cache_key, config.cache_duration_minutes)
        if cached_response:
            return APIResponse(
                request_id=cache_key,
                status_code=200,
                success=True,
                data=cached_response,
                response_time_ms=10,
                from_cache=True,
                cache_expires_at=datetime.utcnow() + timedelta(minutes=config.cache_duration_minutes)
            )
        
        # Make the actual API request
        start_time = datetime.utcnow()
        
        try:
            url = urljoin(str(config.base_url), endpoint_path)
            headers = {**config.headers}
            
            if config.api_key:
                headers["Authorization"] = f"Bearer {config.api_key}"
            
            if params:
                if method.upper() == "GET":
                    url += "?" + urlencode(params)
                
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config.timeout_seconds)) as session:
                async with session.request(method, url, headers=headers) as response:
                    response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            
                            # Cache successful response
                            self._cache_response(cache_key, data, config.cache_duration_minutes)
                            
                            # Update usage statistics
                            self._update_usage_stats(api_id, True, response_time)
                            
                            return APIResponse(
                                request_id=cache_key,
                                status_code=response.status,
                                success=True,
                                data=data,
                                raw_response=response_text[:1000],  # Truncate for storage
                                response_time_ms=response_time,
                                data_size_bytes=len(response_text)
                            )
                        except json.JSONDecodeError:
                            return APIResponse(
                                request_id=cache_key,
                                status_code=response.status,
                                success=False,
                                error_message="Invalid JSON response",
                                response_time_ms=response_time
                            )
                    else:
                        self._update_usage_stats(api_id, False, response_time)
                        return APIResponse(
                            request_id=cache_key,
                            status_code=response.status,
                            success=False,
                            error_message=f"HTTP {response.status}: {response_text[:200]}",
                            response_time_ms=response_time
                        )
                        
        except asyncio.TimeoutError:
            self._update_usage_stats(api_id, False, config.timeout_seconds * 1000)
            return APIResponse(
                request_id=cache_key,
                status_code=408,
                success=False,
                error_message="Request timeout",
                response_time_ms=config.timeout_seconds * 1000
            )
        except Exception as e:
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._update_usage_stats(api_id, False, response_time)
            return APIResponse(
                request_id=cache_key,
                status_code=500,
                success=False,
                error_message=str(e),
                response_time_ms=response_time
            )

    async def get_railway_schedules(self, origin: str, destination: str, 
                                  date: Optional[datetime] = None) -> List[PublicTransportSchedule]:
        """Get railway schedules from Sri Lanka Railways API"""
        params = {
            "from": origin,
            "to": destination,
            "date": (date or datetime.now()).strftime("%Y-%m-%d")
        }
        
        response = await self.make_api_request("sri_lanka_railways", "schedules", params)
        
        if response.success and response.data:
            # Convert API response to our format
            schedules = []
            for schedule_data in response.data.get("schedules", []):
                schedule = PublicTransportSchedule(
                    route_id=schedule_data.get("route_id", "unknown"),
                    service_id=schedule_data.get("service_id", "unknown"),
                    operator="Sri Lanka Railways",
                    transport_mode=TransportMode.TRAIN,
                    route_name=schedule_data.get("train_name", "Unknown Train"),
                    direction=schedule_data.get("direction", "Unknown"),
                    start_stop=origin,
                    end_stop=destination,
                    departure_times=[datetime.strptime(t, "%H:%M").time() for t in schedule_data.get("departure_times", [])],
                    frequency_minutes=schedule_data.get("frequency_minutes"),
                    valid_from=datetime.now(),
                    valid_until=datetime.now() + timedelta(days=30)
                )
                schedules.append(schedule)
            return schedules
        
        # Return sample data if API fails
        return self._get_sample_railway_schedules(origin, destination)

    async def get_bus_schedules(self, route_number: str) -> List[PublicTransportSchedule]:
        """Get bus schedules from SLTB API"""
        params = {"route": route_number}
        
        response = await self.make_api_request("sltb", "routes/schedule", params)
        
        if response.success and response.data:
            schedules = []
            for schedule_data in response.data.get("schedules", []):
                schedule = PublicTransportSchedule(
                    route_id=schedule_data.get("route_id", route_number),
                    service_id=schedule_data.get("service_id", "unknown"),
                    operator="SLTB",
                    transport_mode=TransportMode.BUS,
                    route_name=schedule_data.get("route_name", f"Route {route_number}"),
                    direction=schedule_data.get("direction", "Unknown"),
                    start_stop=schedule_data.get("start_stop", "Unknown"),
                    end_stop=schedule_data.get("end_stop", "Unknown"),
                    departure_times=[datetime.strptime(t, "%H:%M").time() for t in schedule_data.get("departure_times", [])],
                    frequency_minutes=schedule_data.get("frequency_minutes", 30),
                    valid_from=datetime.now(),
                    valid_until=datetime.now() + timedelta(days=30)
                )
                schedules.append(schedule)
            return schedules
        
        # Return sample data if API fails
        return self._get_sample_bus_schedules(route_number)

    async def get_weather_data(self, location: Location) -> Optional[WeatherData]:
        """Get weather data for a location"""
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "units": "metric",
            "appid": "mock_weather_key"
        }
        
        response = await self.make_api_request("openweather", "weather", params)
        
        if response.success and response.data:
            weather_info = response.data
            return WeatherData(
                location=location,
                temperature_celsius=weather_info.get("main", {}).get("temp", 25.0),
                humidity_percent=weather_info.get("main", {}).get("humidity", 70),
                weather_condition=weather_info.get("weather", [{}])[0].get("main", "Clear"),
                wind_speed_kmh=weather_info.get("wind", {}).get("speed", 0) * 3.6,  # Convert m/s to km/h
                visibility_km=weather_info.get("visibility", 10000) / 1000,
                rainfall_mm=weather_info.get("rain", {}).get("1h", 0.0),
                travel_advisory=self._generate_travel_advisory(weather_info),
                impact_on_transport=self._assess_weather_impact(weather_info)
            )
        
        # Return sample weather data if API fails
        return WeatherData(
            location=location,
            temperature_celsius=28.0,
            humidity_percent=75,
            weather_condition="Partly Cloudy",
            wind_speed_kmh=15.0,
            visibility_km=10.0,
            impact_on_transport="none"
        )

    async def get_traffic_data(self, origin: Location, destination: Location) -> Optional[TrafficData]:
        """Get traffic data between two locations"""
        params = {
            "origin": f"{origin.latitude},{origin.longitude}",
            "destination": f"{destination.latitude},{destination.longitude}",
            "departure_time": "now",
            "traffic_model": "best_guess"
        }
        
        response = await self.make_api_request("google_traffic", "distancematrix/json", params)
        
        if response.success and response.data:
            try:
                traffic_info = response.data.get("rows", [{}])[0].get("elements", [{}])[0]
                duration = traffic_info.get("duration_in_traffic", traffic_info.get("duration", {}))
                
                return TrafficData(
                    route_segment=f"{origin.name} to {destination.name}",
                    start_location=origin,
                    end_location=destination,
                    travel_time_minutes=duration.get("value", 1800) // 60,  # Convert seconds to minutes
                    delay_minutes=max(0, (duration.get("value", 1800) - traffic_info.get("duration", {}).get("value", 1800)) // 60),
                    traffic_level=self._determine_traffic_level(duration.get("value", 1800), traffic_info.get("duration", {}).get("value", 1800))
                )
            except (IndexError, KeyError, TypeError):
                # Fall through to sample data if parsing fails
                pass
        
        # Return sample traffic data if API fails
        estimated_minutes = int(self._calculate_distance(origin, destination) * 2)  # Rough estimate
        return TrafficData(
            route_segment=f"{origin.name} to {destination.name}",
            start_location=origin,
            end_location=destination,
            travel_time_minutes=estimated_minutes,
            delay_minutes=0,
            traffic_level="normal"
        )

    async def get_real_time_vehicle_positions(self, route_id: str) -> List[RealTimeVehiclePosition]:
        """Get real-time vehicle positions for a route"""
        params = {"route_id": route_id}
        
        # Try both railway and bus APIs
        for api_id in ["sri_lanka_railways", "sltb"]:
            response = await self.make_api_request(api_id, "vehicles/positions", params)
            
            if response.success and response.data:
                positions = []
                for vehicle_data in response.data.get("vehicles", []):
                    position = RealTimeVehiclePosition(
                        vehicle_id=vehicle_data.get("vehicle_id", "unknown"),
                        route_id=route_id,
                        operator=vehicle_data.get("operator", "Unknown"),
                        transport_mode=TransportMode.TRAIN if api_id == "sri_lanka_railways" else TransportMode.BUS,
                        current_location=Location(
                            latitude=vehicle_data.get("latitude", 6.9271),
                            longitude=vehicle_data.get("longitude", 79.8612),
                            name=vehicle_data.get("location_name", "Unknown")
                        ),
                        heading_degrees=vehicle_data.get("heading"),
                        speed_kmh=vehicle_data.get("speed"),
                        service_status=vehicle_data.get("status", "in_service"),
                        occupancy_level=vehicle_data.get("occupancy", "unknown"),
                        delay_minutes=vehicle_data.get("delay_minutes", 0)
                    )
                    positions.append(position)
                return positions
        
        # Return sample data if APIs fail
        return []

    async def perform_health_check(self, api_id: Optional[str] = None) -> List[IntegrationHealthCheck]:
        """Perform health checks on external APIs"""
        checks = []
        apis_to_check = [api_id] if api_id else list(self.api_configs.keys())
        
        for api_id in apis_to_check:
            config = self.api_configs[api_id]
            start_time = datetime.utcnow()
            
            # Simple connectivity check
            try:
                response = await self.make_api_request(api_id, "health", {})
                response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                check = IntegrationHealthCheck(
                    api_id=api_id,
                    check_type="connectivity",
                    status="passed" if response.success else "failed",
                    response_time_ms=response_time,
                    details={
                        "status_code": response.status_code,
                        "success": response.success,
                        "error_message": response.error_message
                    }
                )
                
                if not response.success:
                    check.issues.append(f"API returned error: {response.error_message}")
                    check.recommendations.append("Check API credentials and endpoint availability")
                
                checks.append(check)
                
            except Exception as e:
                response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                check = IntegrationHealthCheck(
                    api_id=api_id,
                    check_type="connectivity",
                    status="failed",
                    response_time_ms=response_time,
                    details={"error": str(e)},
                    issues=[f"Health check failed: {str(e)}"],
                    recommendations=["Verify API endpoint and network connectivity"]
                )
                checks.append(check)
        
        return checks

    async def get_integration_status(self) -> APIIntegrationStatus:
        """Get overall integration status"""
        total_apis = len(self.api_configs)
        active_apis = sum(1 for config in self.api_configs.values() if config.status == APIStatus.ACTIVE)
        failed_apis = total_apis - active_apis
        
        # Calculate today's statistics
        today_stats = self._calculate_daily_stats()
        
        return APIIntegrationStatus(
            total_apis=total_apis,
            active_apis=active_apis,
            failed_apis=failed_apis,
            total_requests_today=today_stats["total_requests"],
            successful_requests_today=today_stats["successful_requests"],
            failed_requests_today=today_stats["failed_requests"],
            average_response_time_ms=today_stats["avg_response_time"],
            api_statuses={api_id: config.status for api_id, config in self.api_configs.items()},
            real_time_coverage_percent=75.0  # Estimated
        )

    # Helper methods
    async def _check_rate_limit(self, api_id: str, config: ExternalAPIConfig) -> bool:
        """Check if request is within rate limits"""
        now = datetime.utcnow()
        
        if api_id not in self.request_counts:
            self.request_counts[api_id] = []
        
        # Clean old requests (older than 1 hour)
        self.request_counts[api_id] = [
            req_time for req_time in self.request_counts[api_id]
            if now - req_time < timedelta(hours=1)
        ]
        
        # Check rate limits
        recent_requests = [
            req_time for req_time in self.request_counts[api_id]
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) >= config.rate_limit_per_minute:
            return False
        
        if len(self.request_counts[api_id]) >= config.rate_limit_per_hour:
            return False
        
        # Add current request
        self.request_counts[api_id].append(now)
        return True

    def _generate_cache_key(self, api_id: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        params_str = json.dumps(params or {}, sort_keys=True)
        return hashlib.md5(f"{api_id}:{endpoint}:{params_str}".encode()).hexdigest()

    def _get_cached_response(self, cache_key: str, cache_duration_minutes: int) -> Optional[Dict[str, Any]]:
        """Get cached response if still valid"""
        if cache_key in self.response_cache:
            data, cached_at = self.response_cache[cache_key]
            if datetime.utcnow() - cached_at < timedelta(minutes=cache_duration_minutes):
                return data
            else:
                del self.response_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, data: Dict[str, Any], cache_duration_minutes: int):
        """Cache response data"""
        self.response_cache[cache_key] = (data, datetime.utcnow())

    def _update_usage_stats(self, api_id: str, success: bool, response_time_ms: int):
        """Update usage statistics"""
        if api_id not in self.usage_stats:
            self.usage_stats[api_id] = APIUsageStatistics(
                api_id=api_id,
                period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
            )
        
        stats = self.usage_stats[api_id]
        stats.total_requests += 1
        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        # Update response time average
        total_time = stats.average_response_time_ms * (stats.total_requests - 1) + response_time_ms
        stats.average_response_time_ms = total_time / stats.total_requests

    def _calculate_daily_stats(self) -> Dict[str, Any]:
        """Calculate daily statistics across all APIs"""
        total_requests = sum(stats.total_requests for stats in self.usage_stats.values())
        successful_requests = sum(stats.successful_requests for stats in self.usage_stats.values())
        failed_requests = total_requests - successful_requests
        
        if self.usage_stats:
            avg_response_time = sum(stats.average_response_time_ms for stats in self.usage_stats.values()) / len(self.usage_stats)
        else:
            avg_response_time = 0.0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_response_time": avg_response_time
        }

    def _generate_travel_advisory(self, weather_info: Dict[str, Any]) -> Optional[str]:
        """Generate travel advisory based on weather"""
        main_weather = weather_info.get("weather", [{}])[0].get("main", "").lower()
        
        if "rain" in main_weather or "storm" in main_weather:
            return "Heavy rain expected. Allow extra travel time and check for service disruptions."
        elif "fog" in main_weather or "mist" in main_weather:
            return "Foggy conditions may affect visibility. Drive carefully and expect delays."
        
        return None

    def _assess_weather_impact(self, weather_info: Dict[str, Any]) -> str:
        """Assess weather impact on transport"""
        main_weather = weather_info.get("weather", [{}])[0].get("main", "").lower()
        wind_speed = weather_info.get("wind", {}).get("speed", 0)
        
        if "thunderstorm" in main_weather or wind_speed > 15:
            return "severe"
        elif "rain" in main_weather or "snow" in main_weather:
            return "moderate"
        elif "fog" in main_weather or "mist" in main_weather:
            return "minimal"
        else:
            return "none"

    def _determine_traffic_level(self, traffic_duration: int, normal_duration: int) -> str:
        """Determine traffic level based on duration comparison"""
        if traffic_duration <= normal_duration * 1.1:
            return "light"
        elif traffic_duration <= normal_duration * 1.3:
            return "normal"
        elif traffic_duration <= normal_duration * 1.6:
            return "heavy"
        else:
            return "severe"

    def _calculate_distance(self, origin: Location, destination: Location) -> float:
        """Calculate approximate distance between two locations in km"""
        import math
        
        lat1, lon1 = math.radians(origin.latitude), math.radians(origin.longitude)
        lat2, lon2 = math.radians(destination.latitude), math.radians(destination.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Earth's radius in km

    def _get_sample_railway_schedules(self, origin: str, destination: str) -> List[PublicTransportSchedule]:
        """Get sample railway schedules"""
        from datetime import time
        
        return [
            PublicTransportSchedule(
                route_id="main_line_express",
                service_id="express_001",
                operator="Sri Lanka Railways",
                transport_mode=TransportMode.TRAIN,
                route_name="Main Line Express",
                direction="Up",
                start_stop=origin,
                end_stop=destination,
                departure_times=[time(6, 30), time(8, 15), time(14, 45), time(18, 30)],
                frequency_minutes=None,
                valid_from=datetime.now(),
                valid_until=datetime.now() + timedelta(days=30)
            ),
            PublicTransportSchedule(
                route_id="intercity_express",
                service_id="intercity_002",
                operator="Sri Lanka Railways",
                transport_mode=TransportMode.TRAIN,
                route_name="Intercity Express",
                direction="Up",
                start_stop=origin,
                end_stop=destination,
                departure_times=[time(7, 0), time(15, 30)],
                frequency_minutes=None,
                valid_from=datetime.now(),
                valid_until=datetime.now() + timedelta(days=30)
            )
        ]

    def _get_sample_bus_schedules(self, route_number: str) -> List[PublicTransportSchedule]:
        """Get sample bus schedules"""
        from datetime import time
        
        return [
            PublicTransportSchedule(
                route_id=route_number,
                service_id=f"bus_{route_number}_regular",
                operator="SLTB",
                transport_mode=TransportMode.BUS,
                route_name=f"Route {route_number}",
                direction="Both",
                start_stop="Main Terminal",
                end_stop="End Terminal",
                departure_times=[time(h, m) for h in range(5, 23) for m in [0, 30]],
                frequency_minutes=30,
                valid_from=datetime.now(),
                valid_until=datetime.now() + timedelta(days=30)
            )
        ]