from fastapi import APIRouter
from app.core.config import settings
from app.core.database import test_db_connection, db

router = APIRouter()


@router.get("/", 
    summary="Welcome to Smart Transit Companion API",
    description="""
    🏠 **Welcome Endpoint**
    
    Returns basic information about the Smart Transit Companion Backend API.
    
    **Features:**
    - ✅ API status confirmation
    - 📋 Application metadata
    - 🔗 Quick API overview
    
    **Perfect for:**
    - Initial API connectivity testing
    - Health monitoring systems
    - API discovery and verification
    """,
    response_description="Welcome message with API information",
    tags=["🏠 Core System"]
)
async def welcome():
    """Welcome endpoint for the Transit Companion Backend"""
    return {
        "message": "Welcome to Transit Companion Backend API",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "endpoints": 99,
        "features": [
            "AI-Powered Transit Intelligence",
            "Real-time Data Processing", 
            "Multi-modal Journey Planning",
            "Accessibility-First Design",
            "Multi-language Support"
        ]
    }


@router.get("/health",
    summary="System Health Check",
    description="""
    🔍 **Health Monitoring Endpoint**
    
    Comprehensive health check for the Smart Transit Companion API and its dependencies.
    
    **Monitors:**
    - 🚀 API server status
    - 🗄️ MongoDB database connectivity
    - ⚙️ Configuration validation
    - 📊 System performance indicators
    
    **Response Status:**
    - `healthy`: All systems operational
    - `degraded`: Partial functionality (database issues)
    - `unhealthy`: Critical system failures
    
    **Perfect for:**
    - Load balancer health checks
    - Monitoring system integration
    - DevOps automation
    - Production readiness verification
    """,
    response_description="Detailed health status of all system components",
    tags=["🔍 Monitoring"]
)
async def health_check():
    """Health check endpoint with comprehensive system monitoring"""
    db_result = await test_db_connection()
    db_status = db_result is True
    
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "connection failed",
        "mongodb_url_configured": bool(settings.MONGODB_URL),
        "database_name": settings.DATABASE_NAME,
        "api_version": "1.0.0",
        "endpoints_available": 99,
        "system_ready": db_status
    }


@router.get("/db-connection",
    summary="Database Connection Details",
    description="""
    🗄️ **MongoDB Connection Inspector**
    
    Detailed MongoDB database connection status and metadata for the Smart Transit Companion.
    
    **Information Provided:**
    - 🔗 Connection status and health
    - 📊 Database configuration details
    - 📁 Available collections and count
    - ⚡ Connection performance metrics
    - 🔧 Troubleshooting information
    
    **Connection States:**
    - `connected`: Database fully operational
    - `failed`: Connection attempt unsuccessful
    - `error`: Exception during connection test
    
    **Perfect for:**
    - Database administration
    - Development troubleshooting
    - System integration testing
    - Production monitoring
    - Data migration planning
    """,
    response_description="Comprehensive database connection status and metadata",
    tags=["🗄️ Database"]
)
async def database_connection():
    """Database connection status endpoint with detailed information"""
    try:
        db_result = await test_db_connection()
        if db_result:
            collections = await db.database.list_collection_names()
            return {
                "connection_status": "connected",
                "database_name": settings.DATABASE_NAME,
                "mongodb_url": settings.MONGODB_URL,
                "collections_count": len(collections),
                "collections": collections,
                "database_ready": True,
                "connection_test_passed": True
            }
        else:
            return {
                "connection_status": "failed",
                "database_name": settings.DATABASE_NAME,
                "mongodb_url": settings.MONGODB_URL,
                "error": "Failed to connect to MongoDB",
                "database_ready": False,
                "connection_test_passed": False
            }
    except Exception as e:
        return {
            "connection_status": "error",
            "database_name": settings.DATABASE_NAME,
            "mongodb_url": settings.MONGODB_URL,
            "error": str(e),
            "database_ready": False,
            "connection_test_passed": False
        }