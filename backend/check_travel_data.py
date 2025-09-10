#!/usr/bin/env python3
"""
Check travel requests data to understand why count is 137 instead of 7
"""
import asyncio
from datetime import datetime
from app.core.database import db, connect_to_mongo

async def analyze_travel_data():
    try:
        await connect_to_mongo()
        
        print("=== TRAVEL REQUESTS ANALYSIS ===")
        
        # Total count
        total = await db.database.travel_requests.count_documents({})
        print(f"Total travel_requests: {total}")
        
        # Group by user_id to see distribution
        pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        user_counts = await db.database.travel_requests.aggregate(pipeline).to_list(length=None)
        print(f"\nRequests per user:")
        for user in user_counts[:10]:  # Top 10 users
            print(f"  User {user['_id']}: {user['count']} requests")
        
        # Group by date to see when requests were made
        pipeline = [
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$request_timestamp"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": -1}}
        ]
        date_counts = await db.database.travel_requests.aggregate(pipeline).to_list(length=None)
        print(f"\nRequests by date (recent first):")
        for date in date_counts[:10]:
            print(f"  {date['_id']}: {date['count']} requests")
        
        # Check for unique user trips (might be what we want)
        unique_users = await db.database.travel_requests.distinct("user_id")
        print(f"\nUnique users with travel requests: {len(unique_users)}")
        
        # Sample recent requests
        recent = await db.database.travel_requests.find().sort("request_timestamp", -1).limit(5).to_list(length=5)
        print(f"\nSample recent requests:")
        for req in recent:
            print(f"  {req['request_timestamp']} - User: {req['user_id'][:8]}... - {req['source']} → {req['destination']}")
        
        # Check if there's a different collection we should use
        print(f"\nOther potential collections:")
        collections = await db.database.list_collection_names()
        for col in collections:
            if 'route' in col.lower() or 'trip' in col.lower() or 'history' in col.lower():
                count = await db.database[col].count_documents({})
                print(f"  {col}: {count} documents")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if db.client:
            db.client.close()

if __name__ == "__main__":
    asyncio.run(analyze_travel_data())