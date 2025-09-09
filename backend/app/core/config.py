from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Transit Companion Backend"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_CONNECTION_STRING: str = ""
    DATABASE_NAME: str = "transit_companion_db"
    SECRET_KEY: str = "your-secret-key-here"
    
    # API Keys
    GOOGLE_MAPS_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    
    # LangChain/LangSmith Configuration
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = ""
    LANGCHAIN_PROJECT: str = ""
    
    # Langfuse Configuration
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # Application Settings
    LOG_LEVEL: str = "INFO"
    MAX_ROUTES_PER_REQUEST: int = 5
    DEFAULT_SEARCH_RADIUS_KM: int = 50
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields from environment variables
        extra = "allow"


settings = Settings()