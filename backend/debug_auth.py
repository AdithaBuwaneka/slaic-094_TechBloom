#!/usr/bin/env python3
"""
Debug script to test admin authentication
"""
import asyncio
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.auth_service import auth_service
from app.core.config import settings

async def debug_admin_auth():
    # Test token
    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZDhmODc1Yi02YWM1LTRhZmItOGNlNi02YTZhYWVlMWNkNDMiLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzU3NDYzNDc4LCJleHAiOjE3NTc1NDk4NzgsInR5cGUiOiJhY2Nlc3MifQ.IQxYn_pnQa-OSERyiEqugAoFCARno80FFoAKWGLCIEw"
    
    print("1. Testing JWT token verification...")
    try:
        payload = auth_service.verify_token(admin_token, "access")
        print(f"OK Token verified successfully")
        print(f"   Subject: {payload.get('sub')}")
        print(f"   Email: {payload.get('email')}")
        print(f"   Role: {payload.get('role')}")
        user_id = payload.get("sub")
    except Exception as e:
        print(f"ERROR Token verification failed: {e}")
        return
    
    print("\n2. Testing database connection...")
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client.transit_companion
        
        # Test connection
        await db.command("ping")
        print("OK Database connection successful")
        
        print(f"\n3. Looking up user with user_id: {user_id}")
        user = await db.users.find_one({"user_id": user_id})
        
        if user:
            print("OK User found in database:")
            print(f"   user_id: {user['user_id']}")
            print(f"   email: {user['email']}")
            print(f"   role: {user['role']}")
            print(f"   is_active: {user.get('is_active', True)}")
        else:
            print("ERROR User not found in database")
            print("All users in database:")
            all_users = await db.users.find({}).to_list(length=None)
            for u in all_users:
                print(f"   - {u['user_id']} | {u['email']} | {u['role']}")
        
        client.close()
        
    except Exception as e:
        print(f"ERROR Database operation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_admin_auth())