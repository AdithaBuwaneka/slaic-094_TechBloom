#!/usr/bin/env python3
"""
Script to create an admin user directly in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.auth_service import auth_service
from app.core.config import settings
from datetime import datetime

async def create_admin_user():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.transit_companion
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": "admin@example.com"})
    
    if existing_admin:
        # Update existing user to admin
        await db.users.update_one(
            {"email": "admin@example.com"},
            {"$set": {"role": "admin", "updated_at": datetime.utcnow()}}
        )
        print("Updated existing user to admin role")
    else:
        # Create new admin profile
        admin_profile = auth_service.create_user_profile(
            name="Admin User",
            email="admin@example.com",
            password="admin123456",
            role="admin"
        )
        
        # Insert admin
        await db.users.insert_one(admin_profile)
        print("Created new admin user")
    
    print("Admin user created/updated:")
    print("Email: admin@example.com")
    print("Password: admin123456")
    print("Role: admin")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())