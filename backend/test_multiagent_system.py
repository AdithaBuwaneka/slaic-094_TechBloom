#!/usr/bin/env python3
"""
Test script for the multiagentic transit system.
Run this to verify the system is working correctly.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

async def test_database_connection():
    """Test database connection and collections"""
    print("🧪 Testing Database Connection...")
    
    try:
        from app.core.database import db, connect_to_mongo, test_db_connection
        
        # First connect to MongoDB
        await connect_to_mongo()
        
        # Test connection
        connection_status = await test_db_connection()
        if connection_status:
            print("✅ Database connection successful")
            
            # Check collections
            collections = await db.database.list_collection_names()
            print(f"   Collections found: {collections}")
            
            # Check data in key collections
            key_collections = ["transit_routes", "transit_fares", "user_preferences"]
            for collection_name in key_collections:
                if collection_name in collections:
                    count = await db.database[collection_name].count_documents({})
                    print(f"   {collection_name}: {count} documents")
                else:
                    print(f"   ⚠️  {collection_name}: Not found")
        else:
            print("❌ Database connection failed")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")

async def test_enhanced_route_service():
    """Test the enhanced route service"""
    print("\n🧪 Testing Enhanced Route Service...")
    
    try:
        from app.services.enhanced_route_service import EnhancedRouteService
        
        service = EnhancedRouteService()
        
        # Test basic enhanced route
        result = await service.get_enhanced_route(
            origin="Colombo Fort",
            destination="Maharagama",
            mode="transit",
            transit_preference="bus"
        )
        
        if result.get("success"):
            print("✅ Enhanced route service working correctly")
            print(f"   Primary route: {result['primary_route']['distance_text']} in {result['primary_route']['duration_text']}")
            print(f"   Supplementary routes: {len(result.get('supplementary_routes', []))}")
            print(f"   Fares found: {len(result.get('fares', []))}")
        else:
            print(f"❌ Enhanced route service failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Enhanced route service test failed: {e}")

async def test_multiagent_system():
    """Test the multiagent system"""
    print("\n🧪 Testing Multiagent System...")
    
    try:
        from app.services.multiagent_system import TransitMultiAgentSystem
        
        system = TransitMultiAgentSystem()
        await system.initialize_agents()
        
        # Test route planning
        result = await system.plan_route(
            origin="Colombo Fort",
            destination="Maharagama",
            mode="transit"
        )
        
        if result.get("success"):
            print("✅ Multiagent system working correctly")
            print(f"   Agent used: {result.get('agent_used')}")
            print(f"   Route found: {result['route']['distance_text']} in {result['route']['duration_text']}")
        else:
            print(f"❌ Multiagent system failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Multiagent system test failed: {e}")

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        from app.api.enhanced_routes import router as enhanced_router
        
        # Check if router is properly configured
        if enhanced_router:
            print("✅ Enhanced routes router configured")
            
            # List available endpoints
            routes = []
            for route in enhanced_router.routes:
                if hasattr(route, 'path'):
                    routes.append(f"{route.methods} {route.path}")
            
            print(f"   Available endpoints: {len(routes)}")
            for route in routes[:5]:  # Show first 5
                print(f"     {route}")
        else:
            print("❌ Enhanced routes router not configured")
            
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Multiagentic System Tests...\n")
    
    # Test database connection first
    await test_database_connection()
    
    # Test enhanced route service
    await test_enhanced_route_service()
    
    # Test multiagent system
    await test_multiagent_system()
    
    # Test API endpoints
    await test_api_endpoints()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    # Check environment variables
    required_vars = ["MONGODB_URL", "GOOGLE_MAPS_API_KEY", "GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your .env file")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())
