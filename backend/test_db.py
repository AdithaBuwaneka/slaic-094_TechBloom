#!/usr/bin/env python3
"""
Test script to check database collections and count documents
"""
import asyncio
from app.core.database import db, connect_to_mongo

async def test_collections():
    try:
        # Connect to database
        await connect_to_mongo()
        
        # List all collections
        collections = await db.database.list_collection_names()
        print("Available collections:")
        for collection in collections:
            print(f"  - {collection}")
        
        # Count documents in key collections
        print("\nDocument counts:")
        
        # Users
        if "users" in collections:
            user_count = await db.database.users.count_documents({})
            print(f"  users: {user_count}")
        
        # Travel requests (route history)
        if "travel_requests" in collections:
            travel_count = await db.database.travel_requests.count_documents({})
            print(f"  travel_requests: {travel_count}")
        
        # Community reports
        if "community_reports" in collections:
            reports_count = await db.database.community_reports.count_documents({})
            print(f"  community_reports: {reports_count}")
        
        # Sample travel request
        if "travel_requests" in collections:
            sample = await db.database.travel_requests.find_one()
            if sample:
                print(f"\nSample travel request structure:")
                for key in sample.keys():
                    print(f"  {key}: {type(sample[key]).__name__}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if db.client:
            db.client.close()

if __name__ == "__main__":
    asyncio.run(test_collections())