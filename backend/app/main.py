from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, test_db_connection
from app.api.routes import router
from app.middleware.error_handler import (
    ErrorHandlerMiddleware,
    transit_companion_exception_handler,
    validation_exception_handler,
    http_exception_handler
)
from app.middleware.rate_limiter import RateLimitMiddleware
from app.core.exceptions import TransitCompanionException
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import sys
import asyncio

# Load environment variables from .env file
load_dotenv()

# Configure encoding for Windows systems to prevent Unicode errors
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Check for API Key on startup
if not os.getenv('GOOGLE_MAPS_API_KEY') or "YOUR_API_KEY_HERE" in os.getenv('GOOGLE_MAPS_API_KEY'):
    raise ValueError("GOOGLE_MAPS_API_KEY is not set or is invalid. Please check your .env file.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    print("Connected to MongoDB")
    
    # Test connection
    if await test_db_connection():
        print("MongoDB connection test successful")
    else:
        print("MongoDB connection test failed")
    
    yield
    
    # Shutdown
    await close_mongo_connection()
    print("Disconnected from MongoDB")


app = FastAPI(
    title=settings.APP_NAME, 
    debug=settings.DEBUG,
    lifespan=lifespan,
    description="AI-Powered Transit Companion Backend for Sri Lankan Transportation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add exception handlers
app.add_exception_handler(TransitCompanionException, transit_companion_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Add middleware (order matters - first added = outermost)
app.add_middleware(ErrorHandlerMiddleware)
# app.add_middleware(RateLimitMiddleware)  # Temporarily disabled for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)

# Background tasks
@app.on_event("startup")
async def startup_tasks():
    """Initialize background tasks"""
    try:
        # Start WebSocket periodic updates
        from app.api.v1.websocket_routes import send_periodic_updates
        asyncio.create_task(send_periodic_updates())
        print("Background tasks initialized")
    except Exception as e:
        print(f"Failed to initialize background tasks: {e}")

# Health check endpoint at root
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Transit Companion Backend API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Multi-agent travel planning",
            "Sri Lankan transit integration",
            "Real-time disruption monitoring",
            "Mobile app support",
            "Admin dashboard",
            "Community reporting",
            "Push notifications",
            "WebSocket real-time updates"
        ],
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "api_base": settings.API_V1_STR
    }
