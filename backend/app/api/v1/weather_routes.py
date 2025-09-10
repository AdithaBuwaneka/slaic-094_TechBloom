from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.weather_service import weather_service
import asyncio

router = APIRouter()

class WeatherRequest(BaseModel):
    city: str = Field(..., description="City name")
    action: str = Field("current", description="Action type: current, forecast, or travel_advice")

class CoordinatesWeatherRequest(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

@router.get("/")
async def weather_root():
    """Weather API root endpoint"""
    return {
        "message": "Weather API is running",
        "service": "OpenWeather API",
        "available": weather_service.available,
        "endpoints": {
            "current": "/current/{city}",
            "forecast": "/forecast/{city}",
            "travel_advice": "/travel-advice/{city}",
            "coordinates": "/coordinates"
        }
    }

@router.get("/current/{city}")
async def get_current_weather(city: str):
    """Get current weather for a city"""
    try:
        result = weather_service.get_current_weather(city)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{city}")
async def get_weather_forecast(city: str, days: int = 5):
    """Get weather forecast for a city"""
    try:
        if days < 1 or days > 5:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 5")
        
        result = weather_service.get_weather_forecast(city, days)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/travel-advice/{city}")
async def get_travel_weather_advice(city: str):
    """Get travel advice based on current weather conditions"""
    try:
        current_weather = weather_service.get_current_weather(city)
        if current_weather["status"] != "success":
            raise HTTPException(status_code=400, detail=current_weather.get("error", "Weather data unavailable"))
        
        advice = weather_service.get_travel_weather_advice(current_weather)
        
        return {
            "status": "success",
            "city": current_weather["city"],
            "current_weather": current_weather["weather"],
            "travel_advice": advice,
            "timestamp": current_weather["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coordinates")
async def get_weather_by_coordinates(request: CoordinatesWeatherRequest):
    """Get current weather by coordinates"""
    try:
        result = weather_service.get_weather_by_coordinates(request.lat, request.lng)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_weather(request: WeatherRequest):
    """Query weather with different actions"""
    try:
        if request.action == "current":
            result = weather_service.get_current_weather(request.city)
        elif request.action == "forecast":
            result = weather_service.get_weather_forecast(request.city)
        elif request.action == "travel_advice":
            current_weather = weather_service.get_current_weather(request.city)
            if current_weather["status"] != "success":
                return current_weather
            advice = weather_service.get_travel_weather_advice(current_weather)
            result = {
                "status": "success",
                "city": current_weather["city"],
                "current_weather": current_weather["weather"],
                "travel_advice": advice,
                "timestamp": current_weather["timestamp"]
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown action: {request.action}. Use 'current', 'forecast', or 'travel_advice'"
            )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def weather_health_check():
    """Weather service health check"""
    return {
        "status": "healthy" if weather_service.available else "disabled",
        "api_key_configured": weather_service.available,
        "service": "OpenWeather API"
    }