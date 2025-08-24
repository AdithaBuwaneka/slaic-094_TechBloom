from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Transit Companion Backend"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "transit_companion_db"
    SECRET_KEY: str = "your-secret-key-here"
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # External API Configuration
    USE_MOCK_DATA: bool = True  # Set to False for production
    RAILWAYS_API_KEY: str = "mock_railways_key"
    RAILWAYS_API_URL: str = "https://api.railway.gov.lk/v1/"
    SLTB_API_KEY: str = "mock_sltb_key" 
    SLTB_API_URL: str = "https://api.ntc.gov.lk/bus/v1/"
    WEATHER_API_KEY: str = "mock_weather_key"
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/"
    GOOGLE_MAPS_API_KEY: str = "mock_google_key"
    GOOGLE_MAPS_API_URL: str = "https://maps.googleapis.com/maps/api/"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()