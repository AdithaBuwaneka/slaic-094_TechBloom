from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.models.external_apis import (
    ExternalAPIConfig, APIIntegrationStatus, IntegrationHealthCheck,
    WeatherData, TrafficData, PublicTransportSchedule, RealTimeVehiclePosition,
    APIUsageStatistics
)
from app.models.transport_data import Location
from app.services.external_api_service import ExternalAPIService
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()
external_api_service = ExternalAPIService()
user_service = UserService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token (optional for some endpoints)"""
    try:
        token_data = user_service._verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return token_data["user_id"]
    except:
        return None


@router.get("/status")
async def get_integration_status():
    """Get overall external API integration status"""
    try:
        integration_status = await external_api_service.get_integration_status()
        
        return {
            "status": "success",
            "data": integration_status.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration status: {str(e)}"
        )


@router.get("/health-check")
async def perform_health_check(api_id: Optional[str] = Query(None)):
    """Perform health checks on external APIs"""
    try:
        health_checks = await external_api_service.perform_health_check(api_id)
        
        # Calculate overall health status
        total_checks = len(health_checks)
        passed_checks = sum(1 for check in health_checks if check.status == "passed")
        overall_status = "healthy" if passed_checks == total_checks else "issues_detected"
        
        return {
            "status": "success",
            "data": {
                "overall_status": overall_status,
                "checks_performed": total_checks,
                "checks_passed": passed_checks,
                "checks_failed": total_checks - passed_checks,
                "health_checks": [check.model_dump() for check in health_checks]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/weather")
async def get_weather_data(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    location_name: str = Query("Unknown Location")
):
    """Get weather data for a specific location"""
    try:
        location = Location(
            latitude=latitude,
            longitude=longitude,
            name=location_name
        )
        
        weather_data = await external_api_service.get_weather_data(location)
        
        if not weather_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weather data not available for this location"
            )
        
        return {
            "status": "success",
            "data": weather_data.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weather data: {str(e)}"
        )


@router.get("/traffic")
async def get_traffic_data(
    origin_lat: float = Query(..., ge=-90, le=90),
    origin_lng: float = Query(..., ge=-180, le=180),
    dest_lat: float = Query(..., ge=-90, le=90),
    dest_lng: float = Query(..., ge=-180, le=180),
    origin_name: str = Query("Origin"),
    dest_name: str = Query("Destination")
):
    """Get traffic data between two locations"""
    try:
        origin = Location(latitude=origin_lat, longitude=origin_lng, name=origin_name)
        destination = Location(latitude=dest_lat, longitude=dest_lng, name=dest_name)
        
        traffic_data = await external_api_service.get_traffic_data(origin, destination)
        
        if not traffic_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Traffic data not available for this route"
            )
        
        return {
            "status": "success",
            "data": traffic_data.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get traffic data: {str(e)}"
        )


@router.get("/schedules/railway")
async def get_railway_schedules(
    origin: str = Query(..., description="Origin station name"),
    destination: str = Query(..., description="Destination station name"),
    date: Optional[str] = Query(None, description="Travel date (YYYY-MM-DD)")
):
    """Get railway schedules from Sri Lanka Railways API"""
    try:
        travel_date = None
        if date:
            try:
                travel_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        schedules = await external_api_service.get_railway_schedules(origin, destination, travel_date)
        
        return {
            "status": "success",
            "message": f"Found {len(schedules)} railway schedules",
            "data": {
                "origin": origin,
                "destination": destination,
                "travel_date": travel_date.isoformat() if travel_date else None,
                "schedules": [schedule.model_dump() for schedule in schedules]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get railway schedules: {str(e)}"
        )


@router.get("/schedules/bus")
async def get_bus_schedules(
    route_number: str = Query(..., description="Bus route number")
):
    """Get bus schedules from SLTB API"""
    try:
        schedules = await external_api_service.get_bus_schedules(route_number)
        
        return {
            "status": "success",
            "message": f"Found {len(schedules)} bus schedules",
            "data": {
                "route_number": route_number,
                "schedules": [schedule.model_dump() for schedule in schedules]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bus schedules: {str(e)}"
        )


@router.get("/real-time/vehicles")
async def get_real_time_vehicles(
    route_id: str = Query(..., description="Route ID to get vehicle positions")
):
    """Get real-time vehicle positions for a route"""
    try:
        vehicles = await external_api_service.get_real_time_vehicle_positions(route_id)
        
        return {
            "status": "success",
            "message": f"Found {len(vehicles)} vehicles",
            "data": {
                "route_id": route_id,
                "vehicles": [vehicle.model_dump() for vehicle in vehicles],
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vehicle positions: {str(e)}"
        )


@router.get("/usage-statistics")
async def get_usage_statistics(
    api_id: Optional[str] = Query(None, description="Specific API ID"),
    current_user: str = Depends(get_current_user)
):
    """Get API usage statistics (admin only)"""
    try:
        # In a real implementation, you'd check if user has admin privileges
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        stats = external_api_service.usage_stats
        
        if api_id:
            if api_id not in stats:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No statistics found for API: {api_id}"
                )
            return {
                "status": "success",
                "data": stats[api_id].model_dump()
            }
        else:
            return {
                "status": "success",
                "data": {
                    "total_apis": len(stats),
                    "statistics": {api_id: stat.model_dump() for api_id, stat in stats.items()}
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage statistics: {str(e)}"
        )


@router.get("/configurations")
async def get_api_configurations(
    current_user: str = Depends(get_current_user)
):
    """Get external API configurations (admin only)"""
    try:
        # In a real implementation, you'd check if user has admin privileges
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        configs = external_api_service.api_configs
        
        # Remove sensitive information like API keys
        safe_configs = {}
        for api_id, config in configs.items():
            safe_config = config.model_dump()
            if "api_key" in safe_config:
                safe_config["api_key"] = "***masked***" if safe_config["api_key"] else None
            safe_configs[api_id] = safe_config
        
        return {
            "status": "success",
            "data": {
                "total_apis": len(safe_configs),
                "configurations": safe_configs
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API configurations: {str(e)}"
        )


@router.post("/test-connection")
async def test_api_connection(
    api_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Test connection to an external API (admin only)"""
    try:
        # In a real implementation, you'd check if user has admin privileges
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        api_id = api_data.get("api_id")
        endpoint = api_data.get("endpoint", "health")
        params = api_data.get("params", {})
        
        if not api_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="api_id is required"
            )
        
        response = await external_api_service.make_api_request(api_id, endpoint, params)
        
        return {
            "status": "success",
            "message": "API connection test completed",
            "data": {
                "api_id": api_id,
                "endpoint": endpoint,
                "test_result": {
                    "success": response.success,
                    "status_code": response.status_code,
                    "response_time_ms": response.response_time_ms,
                    "error_message": response.error_message,
                    "from_cache": response.from_cache
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API connection test failed: {str(e)}"
        )


@router.get("/data-freshness")
async def get_data_freshness():
    """Get information about data freshness and last updates"""
    try:
        freshness_info = {
            "weather_data": {
                "last_updated": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "update_frequency_minutes": 15,
                "freshness_score": 0.95
            },
            "traffic_data": {
                "last_updated": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "update_frequency_minutes": 5,
                "freshness_score": 0.98
            },
            "railway_schedules": {
                "last_updated": (datetime.utcnow() - timedelta(hours=24)).isoformat(),
                "update_frequency_minutes": 1440,  # Daily
                "freshness_score": 0.85
            },
            "bus_schedules": {
                "last_updated": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                "update_frequency_minutes": 720,  # Twice daily
                "freshness_score": 0.80
            }
        }
        
        # Calculate overall freshness score
        overall_score = sum(data["freshness_score"] for data in freshness_info.values()) / len(freshness_info)
        
        return {
            "status": "success",
            "data": {
                "overall_freshness_score": round(overall_score, 2),
                "last_system_update": datetime.utcnow().isoformat(),
                "data_sources": freshness_info
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data freshness: {str(e)}"
        )


@router.get("/coverage-areas")
async def get_coverage_areas():
    """Get information about geographical coverage areas"""
    try:
        coverage_info = {
            "sri_lanka_railways": {
                "provider": "Sri Lanka Railways",
                "coverage_areas": ["Western", "Central", "Southern", "Northern", "Eastern"],
                "coverage_type": "Provincial",
                "real_time_availability": True,
                "data_quality": 0.85
            },
            "sltb": {
                "provider": "Sri Lanka Transport Board", 
                "coverage_areas": ["All Districts"],
                "coverage_type": "National",
                "real_time_availability": False,
                "data_quality": 0.75
            },
            "weather": {
                "provider": "OpenWeather",
                "coverage_areas": ["Sri Lanka"],
                "coverage_type": "National",
                "real_time_availability": True,
                "data_quality": 0.95
            },
            "traffic": {
                "provider": "Google Maps",
                "coverage_areas": ["Major Cities", "Main Roads"],
                "coverage_type": "Urban Areas",
                "real_time_availability": True,
                "data_quality": 0.92
            }
        }
        
        return {
            "status": "success",
            "data": {
                "total_providers": len(coverage_info),
                "national_coverage": True,
                "real_time_providers": sum(1 for info in coverage_info.values() if info["real_time_availability"]),
                "coverage_details": coverage_info
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coverage areas: {str(e)}"
        )