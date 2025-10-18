from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings 

class Database:
    client: AsyncIOMotorClient = None
    database = None
    bus_routes_collection = None 

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    # Add connection settings with shorter DNS timeout to fail fast if DNS is unavailable
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,  # 5 seconds timeout for server selection
        connectTimeoutMS=10000,  # 10 seconds timeout for initial connection
        socketTimeoutMS=10000,   # 10 seconds timeout for socket operations
        maxPoolSize=10,
        minPoolSize=1,
        retryWrites=True
    )
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
