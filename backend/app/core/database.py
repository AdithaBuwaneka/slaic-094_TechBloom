from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings 

class Database:
    client: AsyncIOMotorClient = None
    database = None
    bus_routes_collection = None 

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL) # Make sure MONGODB_URL is in your settings
    db.database = db.client[settings.DATABASE_NAME] # Make sure DATABASE_NAME is in your settings
    print("Connected to MongoDB and initialized collections.")


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
