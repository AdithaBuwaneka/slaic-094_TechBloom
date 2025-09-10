#!/usr/bin/env python3
"""
Check route_history collection count
"""
import asyncio
from app.core.database import db, connect_to_mongo

async def check_route_history():
    try:
        await connect_to_mongo()
        
        print("=== ROUTE HISTORY ANALYSIS ===")
        
        # Count route_history collection
        route_history_count = await db.database.route_history.count_documents({})
        print(f"route_history count: {route_history_count}")
        
        # Sample documents
        sample = await db.database.route_history.find().limit(3).to_list(length=3)
        print(f"\nSample route_history documents:")
        for i, doc in enumerate(sample, 1):
            print(f"  Document {i}:")
            for key, value in doc.items():
                if key != '_id':
                    print(f"    {key}: {value}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if db.client:
            db.client.close()

if __name__ == "__main__":
    asyncio.run(check_route_history())