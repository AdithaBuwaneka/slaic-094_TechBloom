#!/usr/bin/env python3
"""
Migration script to move routes from route_history to travel_requests collection.
This ensures that chatbot-generated routes appear in the mobile app's Routes tab.
"""

import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_DETAILS = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "transit_companion_db")

async def migrate_routes():
    """Migrate routes from route_history to travel_requests collection"""
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    
    try:
        print("🔄 Starting route migration from route_history to travel_requests...")
        
        # Get all route_history items
        route_history_cursor = db.route_history.find({})
        route_history_items = await route_history_cursor.to_list(length=None)
        
        print(f"📊 Found {len(route_history_items)} routes in route_history collection")
        
        migrated_count = 0
        skipped_count = 0
        
        for item in route_history_items:
            try:
                # Check if this route already exists in travel_requests
                existing_request = await db.travel_requests.find_one({
                    "user_id": item.get("user_id"),
                    "source": item.get("source"),
                    "destination": item.get("destination"),
                    "request_timestamp": item.get("created_at")
                })
                
                if existing_request:
                    print(f"⏭️  Skipping existing route: {item.get('source')} → {item.get('destination')}")
                    skipped_count += 1
                    continue
                
                # Create travel request document from route history
                travel_request = {
                    "user_id": item.get("user_id"),
                    "source": item.get("source"),
                    "destination": item.get("destination"),
                    "mode": item.get("metadata", {}).get("mode", "transit"),
                    "preferred_transit": None,
                    "departure_time": None,
                    "request_timestamp": item.get("created_at"),
                    "result": {
                        "status": "success",
                        "response": {
                            "best_route": item.get("route_data"),
                            "all_routes": [item.get("route_data")],
                            "ai_disruption_analysis": item.get("ai_disruption_analysis"),
                            "destination_summary": item.get("destination_summary"),
                            "active_disruptions": item.get("active_disruptions", [])
                        }
                    },
                    "migrated_from_route_history": True,
                    "migration_timestamp": datetime.utcnow()
                }
                
                # Insert into travel_requests collection
                await db.travel_requests.insert_one(travel_request)
                migrated_count += 1
                
                print(f"✅ Migrated route: {item.get('source')} → {item.get('destination')}")
                
            except Exception as e:
                print(f"❌ Error migrating route {item.get('_id')}: {str(e)}")
                continue
        
        print(f"\n🎉 Migration completed!")
        print(f"📈 Migrated: {migrated_count} routes")
        print(f"⏭️  Skipped: {skipped_count} routes (already exist)")
        print(f"📊 Total processed: {len(route_history_items)} routes")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_routes())

