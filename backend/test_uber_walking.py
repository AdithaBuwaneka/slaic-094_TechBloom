#!/usr/bin/env python3
"""
Test script for Uber walking alternative functionality
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.workflow import run_travel_agent

# Load environment variables
load_dotenv()

def test_uber_walking_alternative():
    """Test the Uber walking alternative functionality"""
    
    print("🧪 Testing Uber Walking Alternative Functionality")
    print("=" * 60)
    
    # Test with user who prefers time over cost (time_vs_cost_weight > 0.5)
    print("\n📍 Test Case: Pettah to Maharagama with time preference")
    print("   - User prefers time over cost")
    print("   - Looking for walking segments > 0.5km")
    print("   - Should show Uber alternatives for long walking segments")
    
    try:
        # Run the travel agent with the provided example
        result = run_travel_agent(
            source="pettah",
            destination="maharagama", 
            mode="transit",
            user_id="dawfw",  # Same user ID as in the example
            preferred_transit="bus"
        )
        
        if result["status"] == "success":
            response = result["response"]
            
            print(f"\n✅ Request processed successfully!")
            print(f"   Processing time: {result['processing_time']:.2f}s")
            print(f"   Total routes found: {response.get('total_routes_found', 0)}")
            
            # Check if we have routes with Uber alternatives
            routes_with_uber = 0
            total_walking_steps = 0
            uber_alternatives_found = 0
            
            for route in response.get("all_routes", []):
                print(f"\n🛤️  Route: {route.get('route_id', 'unknown')}")
                print(f"   Duration: {route.get('duration_text', 'unknown')}")
                print(f"   Distance: {route.get('distance_text', 'unknown')}")
                print(f"   Cost: {route.get('estimated_cost', 0)} LKR")
                
                # Check steps for Uber alternatives
                for i, step in enumerate(route.get("steps", [])):
                    if step.get("travel_mode") == "WALKING":
                        total_walking_steps += 1
                        distance_text = step.get("distance", "0 m")
                        print(f"   🚶 Step {i+1}: {step.get('html_instructions', 'Walk')} - {distance_text}")
                        
                        # Check for Uber alternative
                        if step.get("uber_alternative"):
                            uber_alt = step["uber_alternative"]
                            uber_alternatives_found += 1
                            routes_with_uber += 1
                            print(f"      🚗 Uber Alternative Available:")
                            print(f"         Duration: {uber_alt['duration_minutes']} min")
                            print(f"         Cost: {uber_alt['cost_lkr']} LKR")
                            print(f"         Distance: {uber_alt['distance_km']} km")
                            print(f"         Reason: {uber_alt['reason']}")
                        else:
                            print(f"      ℹ️  No Uber alternative (distance: {distance_text})")
            
            print(f"\n📊 Summary:")
            print(f"   Total walking steps: {total_walking_steps}")
            print(f"   Routes with Uber alternatives: {routes_with_uber}")
            print(f"   Uber alternatives found: {uber_alternatives_found}")
            
            if uber_alternatives_found > 0:
                print(f"\n✅ SUCCESS: Uber alternatives were found for long walking segments!")
            else:
                print(f"\n⚠️  No Uber alternatives found. This could mean:")
                print(f"   - No walking segments > 0.5km")
                print(f"   - User doesn't prefer time over cost")
                print(f"   - Implementation needs adjustment")
                
        else:
            print(f"❌ Request failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

def test_user_preferences():
    """Test with different user preference scenarios"""
    
    print("\n\n🧪 Testing Different User Preference Scenarios")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            "name": "Time Preference (time_vs_cost_weight = 0.8)",
            "user_id": "time_preference_user",
            "expected_uber": True
        },
        {
            "name": "Cost Preference (time_vs_cost_weight = 0.2)", 
            "user_id": "cost_preference_user",
            "expected_uber": False
        },
        {
            "name": "Balanced Preference (time_vs_cost_weight = 0.5)",
            "user_id": "balanced_user", 
            "expected_uber": False
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 Scenario: {scenario['name']}")
        print("-" * 40)
        
        try:
            result = run_travel_agent(
                source="pettah",
                destination="maharagama",
                mode="transit", 
                user_id=scenario["user_id"],
                preferred_transit="bus"
            )
            
            if result["status"] == "success":
                response = result["response"]
                uber_found = False
                
                # Check for Uber alternatives
                for route in response.get("all_routes", []):
                    for step in route.get("steps", []):
                        if step.get("uber_alternative"):
                            uber_found = True
                            break
                    if uber_found:
                        break
                
                status = "✅ PASS" if uber_found == scenario["expected_uber"] else "❌ FAIL"
                print(f"   Expected Uber: {scenario['expected_uber']}")
                print(f"   Found Uber: {uber_found}")
                print(f"   Result: {status}")
                
            else:
                print(f"   ❌ Request failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ['GOOGLE_MAPS_API_KEY', 'SERPER_API_KEY', 'MONGODB_CONNECTION_STRING']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all variables are set.")
        sys.exit(1)
    
    # Run tests
    test_uber_walking_alternative()
    test_user_preferences()
    
    print("\n\n🎉 All tests completed!")
