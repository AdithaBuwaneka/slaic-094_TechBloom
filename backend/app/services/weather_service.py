"""
OpenWeather API Service
Provides weather data integration for travel planning
"""

import requests
import os
from typing import Dict, Any, Optional
from app.core.config import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.available = bool(self.api_key)
        
        if not self.available:
            print("WARNING: OPENWEATHER_API_KEY not set. Weather data will be disabled.")
        else:
            print("OpenWeather API service initialized successfully")

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city"""
        if not self.available:
            return {
                "status": "disabled",
                "error": "OpenWeather API key not configured"
            }
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "status": "success",
                "city": data["name"],
                "country": data["sys"]["country"],
                "weather": {
                    "main": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "cloudiness": data["clouds"]["all"]
                },
                "coordinates": {
                    "lat": data["coord"]["lat"],
                    "lng": data["coord"]["lon"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"OpenWeather API request failed: {str(e)}")
            return {
                "status": "error",
                "error": f"Weather API request failed: {str(e)}"
            }
        except KeyError as e:
            logger.error(f"Unexpected weather API response format: {str(e)}")
            return {
                "status": "error",
                "error": f"Invalid weather data format: {str(e)}"
            }

    def get_weather_by_coordinates(self, lat: float, lng: float) -> Dict[str, Any]:
        """Get current weather by coordinates"""
        if not self.available:
            return {
                "status": "disabled",
                "error": "OpenWeather API key not configured"
            }
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lng,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "status": "success",
                "city": data["name"],
                "country": data["sys"]["country"],
                "weather": {
                    "main": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "visibility": data.get("visibility", 0) / 1000,
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "cloudiness": data["clouds"]["all"]
                },
                "coordinates": {
                    "lat": data["coord"]["lat"],
                    "lng": data["coord"]["lon"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"OpenWeather API request failed: {str(e)}")
            return {
                "status": "error",
                "error": f"Weather API request failed: {str(e)}"
            }

    def get_weather_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        if not self.available:
            return {
                "status": "disabled",
                "error": "OpenWeather API key not configured"
            }
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            forecasts = []
            for item in data["list"][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecasts.append({
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "weather": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "cloudiness": item["clouds"]["all"],
                    "precipitation_probability": item.get("pop", 0) * 100
                })
            
            return {
                "status": "success",
                "city": data["city"]["name"],
                "country": data["city"]["country"],
                "forecasts": forecasts,
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"OpenWeather forecast API request failed: {str(e)}")
            return {
                "status": "error",
                "error": f"Weather forecast API request failed: {str(e)}"
            }

    def get_travel_weather_advice(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate travel advice based on weather conditions"""
        if weather_data.get("status") != "success":
            return {"advice": "Weather data unavailable"}
        
        weather = weather_data["weather"]
        advice = {
            "travel_conditions": "good",
            "warnings": [],
            "recommendations": []
        }
        
        # Temperature-based advice
        temp = weather["temperature"]
        if temp < 10:
            advice["recommendations"].append("Dress warmly, cold weather")
        elif temp > 35:
            advice["recommendations"].append("Stay hydrated, very hot weather")
            advice["warnings"].append("Heat warning - avoid prolonged outdoor exposure")
        
        # Weather condition-based advice
        main_weather = weather["main"].lower()
        if main_weather in ["rain", "thunderstorm"]:
            advice["travel_conditions"] = "moderate"
            advice["warnings"].append("Rainy conditions - expect slower traffic and reduced visibility")
            advice["recommendations"].append("Carry umbrella, allow extra travel time")
        elif main_weather == "snow":
            advice["travel_conditions"] = "poor"
            advice["warnings"].append("Snow conditions - roads may be slippery")
            advice["recommendations"].append("Drive carefully, use winter tires if available")
        elif main_weather == "fog" or weather["visibility"] < 2:
            advice["travel_conditions"] = "moderate"
            advice["warnings"].append("Low visibility conditions")
            advice["recommendations"].append("Drive slowly, use headlights")
        
        # Wind-based advice
        if weather["wind_speed"] > 15:  # > 54 km/h
            advice["warnings"].append("High wind conditions")
            advice["recommendations"].append("Be cautious with motorcycles and high-profile vehicles")
        
        return advice

# Global weather service instance
weather_service = WeatherService()