#!/usr/bin/env python3
"""Script to seed MongoDB with dummy transit data for multiagentic system."""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

MONGO_DETAILS = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "transit_companion_db")

async def seed_transit_routes(db):
    """Seed transit routes data"""
    collection = db["transit_routes"]
    await collection.delete_many({})
    
    routes = [
        {
            "route_id": "route_001",
            "route_number": "138",
            "origin": "Pettah",
            "destination": "Maharagama",
            "mode": "bus",
            "operator": "SLTB",
            "stops": ["Fort", "Maradana", "Borella", "Narahenpita", "Nugegoda"],
            "frequency": "every 10 minutes",
            "operating_hours": {"start": "05:00", "end": "23:00"},
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        },
        {
            "route_id": "route_002",
            "route_number": "177",
            "origin": "Kollupitiya",
            "destination": "Kaduwela",
            "mode": "bus",
            "operator": "Private",
            "stops": ["Bambalapitiya", "Thummulla", "Rajagiriya", "Battaramulla", "Malabe"],
            "frequency": "every 15 minutes",
            "operating_hours": {"start": "06:00", "end": "22:00"},
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        }
    ]
    
    result = await collection.insert_many(routes)
    print(f"✅ Seeded {len(result.inserted_ids)} transit routes")
    return result.inserted_ids

async def seed_transit_fares(db):
    """Seed transit fares data"""
    collection = db["transit_fares"]
    await collection.delete_many({})
    
    fares = [
        {
            "route_id": "route_001",
            "origin": "Pettah",
            "destination": "Maharagama",
            "mode": "bus",
            "fare_type": "fixed",
            "base_fare": 25.0,
            "currency": "LKR",
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        },
        {
            "route_id": "route_002",
            "origin": "Kollupitiya",
            "destination": "Kaduwela",
            "mode": "bus",
            "fare_type": "fixed",
            "base_fare": 35.0,
            "currency": "LKR",
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        }
    ]
    
    result = await collection.insert_many(fares)
    print(f"✅ Seeded {len(result.inserted_ids)} transit fares")
    return result.inserted_ids

async def seed_all_data():
    """Seed all collections with dummy data"""
    try:
        client = AsyncIOMotorClient(MONGO_DETAILS)
        db = client[DB_NAME]
        
        print(f"🔌 Connected to MongoDB: {DB_NAME}")
        
        await seed_transit_routes(db)
        await seed_transit_fares(db)
        
        print("\n🎉 All data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        client.close()
        print("\n🔌 MongoDB connection closed")

if __name__ == "__main__":
    print("🌱 Starting Transit Data Seeding...")
    asyncio.run(seed_all_data())
    print("✅ Seeding completed!")
