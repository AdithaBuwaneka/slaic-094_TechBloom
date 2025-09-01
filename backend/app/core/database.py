# app/core/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings 
from app.models.transport import MockBusRoute, BusRoute, TrainRoute, TukTukService, Disruption, UserProfile, CommunityUpdate

class Database:
    client: AsyncIOMotorClient = None
    database = None
    # Core transport collections
    bus_routes_collection = None
    train_routes_collection = None
    tuk_tuk_services_collection = None
    # Support collections
    disruptions_collection = None
    user_profiles_collection = None
    community_updates_collection = None
    # Mobile app collections
    users_collection = None
    devices_collection = None
    notifications_collection = None
    journey_history_collection = None
    user_favorites_collection = None
    # Analytics & Admin collections
    analytics_events_collection = None
    journey_analytics_collection = None
    feedback_collection = None
    admin_logs_collection = None
    error_logs_collection = None
    # Legacy collection
    mock_bus_routes_collection = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]
    
    # Initialize all collections
    db.bus_routes_collection = db.database.get_collection("bus_routes")
    db.train_routes_collection = db.database.get_collection("train_routes")
    
    # Mobile app collections
    db.users_collection = db.database.get_collection("users")
    db.devices_collection = db.database.get_collection("devices") 
    db.notifications_collection = db.database.get_collection("notifications")
    db.journey_history_collection = db.database.get_collection("journey_history")
    db.user_favorites_collection = db.database.get_collection("user_favorites")
    db.tuk_tuk_services_collection = db.database.get_collection("tuk_tuk_services")
    db.disruptions_collection = db.database.get_collection("disruptions")
    db.user_profiles_collection = db.database.get_collection("user_profiles")
    db.community_updates_collection = db.database.get_collection("community_updates")
    db.mock_bus_routes_collection = db.database.get_collection("mock_bus_routes")  # Legacy
    
    # Analytics & Admin collections
    db.analytics_events_collection = db.database.get_collection("analytics_events")
    db.journey_analytics_collection = db.database.get_collection("journey_analytics")
    db.feedback_collection = db.database.get_collection("feedback")
    db.admin_logs_collection = db.database.get_collection("admin_logs")
    db.error_logs_collection = db.database.get_collection("error_logs")
    
    print("Connected to MongoDB and initialized all collections.")


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("MongoDB connection closed.")


async def test_db_connection():
    """Test database connection"""
    if not db.client:
        return False
    try:
        await db.client.admin.command('ping')
        return True
    except Exception:
        return False


def bus_route_helper(bus_route) -> MockBusRoute:
    """Parses a MongoDB document into a Pydantic model."""
    return MockBusRoute(
        id=str(bus_route["_id"]),
        route_number=bus_route["route_number"],
        origin=bus_route["origin"],
        destination=bus_route["destination"],
        stops=bus_route["stops"],
        operator=bus_route["operator"],
    )