from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()


async def test_db_connection():
    """Test database connection"""
    try:
        await db.client.admin.command('ping')
        return True
    except Exception:
        return False