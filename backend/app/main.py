from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, test_db_connection
from app.api import journey_planner, auth, mobile, react_native, admin, analytics, authenticated_agents, payments
from app.middleware.rate_limit import RateLimitMiddleware, AgentRateLimitMiddleware
from app.middleware.error_handler import ErrorHandlingMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware
from dotenv import load_dotenv
import os
import logging
import time
import psutil
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", mode="a")
    ]
)

logger = logging.getLogger(__name__)

# Track application start time for uptime metrics
start_time = time.time()

# Check for API Keys on startup (skip Google Maps if using mock data)
use_mock_data = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

if not use_mock_data:
    if not os.getenv('GOOGLE_MAPS_API_KEY') or "YOUR_API_KEY_HERE" in os.getenv('GOOGLE_MAPS_API_KEY'):
        raise ValueError("GOOGLE_MAPS_API_KEY is not set or is invalid. Please check your .env file.")

# Check for Gemini AI key (required for agents)
if not os.getenv('GOOGLE_API_KEY'):
    raise ValueError("GOOGLE_API_KEY is not set. Please check your .env file.")

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
    description="Smart Transit Companion Backend - AI-powered journey planning for Sri Lankan public transport with 7 specialized AI agents",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add security and logging middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, calls=1000, period=3600)  # 1000 requests per hour
app.add_middleware(AgentRateLimitMiddleware, calls=100, period=3600)  # 100 AI requests per hour

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Core API routes
app.include_router(journey_planner.router, prefix="/api/v1", tags=["Journey Planning"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Mobile and device-specific routes
app.include_router(mobile.router, prefix="/api/v1/mobile", tags=["Mobile Features"])
app.include_router(react_native.router, prefix="/api/v1/rn", tags=["React Native Optimized"])

# AI Agent routes (authenticated)
app.include_router(authenticated_agents.router, prefix="/api/v1/agents", tags=["AI Agents"])

# Analytics and tracking
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics & Tracking"])

# Payment and subscription system
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments & Subscriptions"])

# Admin dashboard (restricted)
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin Dashboard"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify service status."""
    try:
        # Check database connection
        db_status = await test_db_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if db_status else "disconnected",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "use_mock_data": use_mock_data
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Performance monitoring endpoint
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get system performance metrics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Windows-compatible disk usage
        try:
            disk_path = 'C:\\' if os.name == 'nt' else '/'
            disk = psutil.disk_usage(disk_path)
            disk_info = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        except Exception as disk_error:
            disk_info = {"error": f"Unable to get disk info: {disk_error}"}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": disk_info,
            "uptime_seconds": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {"error": "Unable to collect metrics", "timestamp": datetime.now().isoformat()}