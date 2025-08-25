from fastapi import APIRouter, HTTPException, Depends
from app.models.path import PathRequest, RouteResponse
from app.core.config import settings
from app.core.database import test_db_connection, db
from app.services import google_maps_service
from datetime import datetime
import time


router = APIRouter()


@router.get("/")
async def welcome():
    """Welcome endpoint for the Transit Companion Backend"""
    return {
        "message": "Welcome to Transit Companion Backend API",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    db_result = await test_db_connection()
    db_status = db_result is True
    
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "connection failed",
        "mongodb_url_configured": bool(settings.MONGODB_URL),
        "database_name": settings.DATABASE_NAME
    }


@router.get("/db-connection")
async def database_connection():
    """Database connection status endpoint"""
    try:
        db_result = await test_db_connection()
        if db_result:
            collections = await db.database.list_collection_names()
            return {
                "connection_status": "connected",
                "database_name": settings.DATABASE_NAME,
                "mongodb_url": settings.MONGODB_URL,
                "collections_count": len(collections),
                "collections": collections
            }
        else:
            return {
                "connection_status": "failed",
                "database_name": settings.DATABASE_NAME,
                "mongodb_url": settings.MONGODB_URL,
                "error": "Failed to connect to MongoDB"
            }
    except Exception as e:
        return {
            "connection_status": "error",
            "database_name": settings.DATABASE_NAME,
            "mongodb_url": settings.MONGODB_URL,
            "error": str(e)
        }


@router.post("/shortest-path", response_model=RouteResponse)
async def get_shortest_path(request: PathRequest):
    """
    Calculates the shortest and most optimal path between any two locations 
    in Sri Lanka using a specified travel mode.
    """
    if not request.start or not request.end:
        raise HTTPException(status_code=400, detail="Start and end locations cannot be empty.")

    departure_timestamp = None
    if request.departure_time:
        try:
            departure_timestamp = int(request.departure_time.timestamp())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid departure_time format. Use ISO 8601 format, e.g., '2025-08-25T16:30:00'")
    else:
        # Default to the current time if not provided
        departure_timestamp = int(time.time())

    # Pass all parameters to the service
    result, error = google_maps_service.get_optimized_route(
        origin=request.start,
        destination=request.end,
        mode=request.mode.value,
        departure_time=departure_timestamp,
        transit_mode_preference=request.transit_mode_preference.value if request.transit_mode_preference else None
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return result
