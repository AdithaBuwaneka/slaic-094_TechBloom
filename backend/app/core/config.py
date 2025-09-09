from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Transit Companion Backend"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "transit_companion_db"
    SECRET_KEY: str = "your-secret-key-here"
    
    # API Keys
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_GEMINI_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    LANGCHAIN_API_KEY: str = ""
    
    # Optional - Langfuse Configuration
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields from environment variables
        extra = "allow"


settings = Settings()