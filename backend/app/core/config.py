from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Transit Companion Backend"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "transit_companion_db"
    SECRET_KEY: str = "dev-secret-key-for-testing-transit-companion-app-12345"
    GOOGLE_MAPS_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # External API Configuration
    USE_MOCK_DATA: str = "true"
    RAILWAYS_API_KEY: str = ""
    RAILWAYS_API_URL: str = ""
    SLTB_API_KEY: str = ""
    SLTB_API_URL: str = ""
    WEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = ""
    GOOGLE_MAPS_API_URL: str = ""
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()