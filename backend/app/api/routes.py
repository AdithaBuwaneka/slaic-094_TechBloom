from fastapi import APIRouter
from app.core.config import settings
from app.core.database import test_db_connection, db

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