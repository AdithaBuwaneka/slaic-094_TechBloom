#!/usr/bin/env python3
"""Complete data seeding script for the multiagentic transit system."""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

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
        },
        {
            "route_id": "route_003",
            "route_number": "120",
            "origin": "Pettah",
            "destination": "Piliyandala",
            "mode": "bus",
            "operator": "SLTB",
            "stops": ["Fort", "Slave Island", "Wellawatte", "Dehiwala", "Kohuwala", "Nugegoda", "Delkanda"],
            "frequency": "every 12 minutes",
            "operating_hours": {"start": "05:30", "end": "22:30"},
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        },
        {
            "route_id": "route_004",
            "route_number": "Express",
            "origin": "Colombo Fort",
            "destination": "Kandy",
            "mode": "train",
            "operator": "Sri Lanka Railways",
            "stops": ["Maradana", "Kelaniya", "Ragama", "Gampaha", "Veyangoda", "Polgahawela", "Peradeniya"],
            "frequency": "every 2 hours",
            "operating_hours": {"start": "06:00", "end": "20:00"},
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
        },
        {
            "route_id": "route_003",
            "origin": "Pettah",
            "destination": "Piliyandala",
            "mode": "bus",
            "fare_type": "fixed",
            "base_fare": 30.0,
            "currency": "LKR",
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        },
        {
            "route_id": "route_004",
            "origin": "Colombo Fort",
            "destination": "Kandy",
            "mode": "train",
            "fare_type": "fixed",
            "base_fare": 150.0,
            "currency": "LKR",
            "is_active": True,
            "created_at": datetime.now(ZoneInfo("Asia/Colombo"))
        }
    ]
    
    result = await collection.insert_many(fares)
    print(f"✅ Seeded {len(result.inserted_ids)} transit fares")
    return result.inserted_ids

async def seed_last_mile_options(db):
    """Seed last mile connectivity options"""
    collection = db["last_mile_options"]
    await collection.delete_many({})
    
    options = [
        {
            "option_id": "last_mile_001",
            "name": "Uber from Maharagama Station",
            "mode": "uber",
            "origin": "Maharagama Station",
            "destination": "Maharagama City Center",
            "estimated_duration": 8,
            "estimated_cost": 250.0,
            "currency": "LKR",
            "availability": "24/7",
            "is_active": True
        },
        {
            "option_id": "last_mile_002",
            "name": "Three Wheeler from Kaduwela",
            "mode": "three_wheeler",
            "origin": "Kaduwela Junction",
            "destination": "Kaduwela City Center",
            "estimated_duration": 5,
            "estimated_cost": 150.0,
            "currency": "LKR",
            "availability": "06:00-22:00",
            "is_active": True
        }
    ]
    
    result = await collection.insert_many(options)
    print(f"✅ Seeded {len(result.inserted_ids)} last mile options")
    return result.inserted_ids

async def seed_user_preferences(db):
    """Seed user preferences data"""
    collection = db["user_preferences"]
    await collection.delete_many({})
    
    preferences = [
        {
            "user_id": "user123",
            "preference_type": "cost",
            "weight": 0.8,
            "value": {"max_fare": 500, "prefer_cheaper": True},
            "last_updated": datetime.now(ZoneInfo("Asia/Colombo"))
        },
        {
            "user_id": "user123",
            "preference_type": "time",
            "weight": 0.6,
            "value": {"max_duration": 120, "prefer_faster": True},
            "last_updated": datetime.now(ZoneInfo("Asia/Colombo"))
        },
        {
            "user_id": "user123",
            "preference_type": "safety",
            "weight": 0.9,
            "value": {"avoid_night_travel": True, "prefer_well_lit_routes": True},
            "last_updated": datetime.now(ZoneInfo("Asia/Colombo"))
        }
    ]
    
    result = await collection.insert_many(preferences)
    print(f"✅ Seeded {len(result.inserted_ids)} user preferences")
    return result.inserted_ids

async def seed_disruptions(db):
    """Seed transit disruptions data"""
    collection = db["transit_disruptions"]
    await collection.delete_many({})
    
    disruptions = [
        {
            "disruption_id": "disp_001",
            "route_id": "route_001",
            "disruption_type": "delay",
            "severity": "medium",
            "description": "Traffic congestion due to road construction on Maradana-Borella stretch",
            "affected_stops": ["Maradana", "Borella"],
            "estimated_duration": 30,
            "alternative_routes": ["route_002", "route_003"],
            "reported_by": "user123",
            "reported_at": datetime.now(ZoneInfo("Asia/Colombo")) - timedelta(hours=1),
            "is_resolved": False,
            "location": {"lat": 6.9271, "lng": 79.8612}
        }
    ]
    
    result = await collection.insert_many(disruptions)
    print(f"✅ Seeded {len(result.inserted_ids)} transit disruptions")
    return result.inserted_ids

async def seed_all_data():
    """Seed all collections with dummy data"""
    try:
        client = AsyncIOMotorClient(MONGO_DETAILS)
        db = client[DB_NAME]
        
        print(f"🔌 Connected to MongoDB: {DB_NAME}")
        
        await seed_transit_routes(db)
        await seed_transit_fares(db)
        await seed_last_mile_options(db)
        await seed_user_preferences(db)
        await seed_disruptions(db)
        
        print("\n🎉 All data seeded successfully!")
        
        # Show collection statistics
        collections = ["transit_routes", "transit_fares", "last_mile_options", 
                      "user_preferences", "transit_disruptions"]
        
        print("\n📊 Collection Statistics:")
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"   {collection_name}: {count} documents")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        client.close()
        print("\n🔌 MongoDB connection closed")

if __name__ == "__main__":
    print("🌱 Starting Complete Transit Data Seeding...")
    asyncio.run(seed_all_data())
    print("✅ Seeding completed!")
