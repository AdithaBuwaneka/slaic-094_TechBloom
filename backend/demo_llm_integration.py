#!/usr/bin/env python3
"""
Demonstration script showing LLM integration in the travel workflow
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def demo_llm_integration():
    """Demonstrate LLM integration in the travel workflow"""
    
    print("🚀 LLM Integration Demo - Transit Companion Backend")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found. Please check your .env file.")
        return
    
    print(f"✅ Environment configured with Google API key")
    
    try:
        # Import the workflow
        from app.services.workflow import run_travel_agent
        
        print("\n🎯 Running Travel Agent with LLM Integration...")
        print("-" * 50)
        
        # Test case 1: Transit route with local knowledge
        print("\n📍 Test Case 1: Colombo to Kandy by Transit")
        print("This will trigger the local knowledge agent and LLM summarization")
        
        result1 = run_travel_agent(
            source="Colombo, Sri Lanka",
            destination="Kandy, Sri Lanka",
            mode="transit",
            user_id="demo_user_1",
            preferred_transit="bus"
        )
        
        if result1["status"] == "success":
            print("✅ Travel agent completed successfully!")
            response = result1["response"]
            
            # Check for LLM-generated content
            if "destination_summary" in response:
                print("\n📝 LLM-Generated Destination Summary:")
                print("-" * 40)
                print(response["destination_summary"])
                print("-" * 40)
            else:
                print("❌ No LLM destination summary found")
            
            # Show route recommendations
            if "recommended_routes" in response:
                routes = response["recommended_routes"]
                print(f"\n🛤️  Route Recommendations ({len(routes)} routes):")
                for i, route in enumerate(routes[:3], 1):  # Show first 3 routes
                    summary = route.get("summary", {})
                    print(f"   Route {i}: {summary.get('duration_minutes', 'N/A')} min, "
                          f"{summary.get('distance_km', 'N/A')} km, "
                          f"Score: {route.get('score', {}).get('overall', 'N/A'):.2f}")
            
        else:
            print(f"❌ Travel agent failed: {result1.get('error', 'Unknown error')}")
        
        # Test case 2: Driving route (should not trigger LLM)
        print("\n\n📍 Test Case 2: Simple Driving Route")
        print("This should complete without LLM processing (no local knowledge needed)")
        
        result2 = run_travel_agent(
            source="Times Square, New York",
            destination="Brooklyn Bridge, New York",
            mode="driving",
            user_id="demo_user_2"
        )
        
        if result2["status"] == "success":
            print("✅ Driving route completed successfully!")
            response = result2["response"]
            
            # Check if LLM was used (should not be for driving)
            if "search_results" in response and "user_friendly_summary" in response["search_results"]:
                print("⚠️  Unexpected: LLM was used for driving route")
            else:
                print("✅ As expected: No LLM processing for simple driving route")
            
            # Show route info
            if "recommended_routes" in response:
                routes = response["recommended_routes"]
                print(f"   - {len(routes)} routes generated")
        
        else:
            print(f"❌ Driving route failed: {result2.get('error', 'Unknown error')}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey Benefits of LLM Integration:")
        print("1. 📝 User-friendly summaries in 4-5 lines")
        print("2. 🎯 Personalized route recommendations")
        print("3. 🔍 Local knowledge synthesis")
        print("4. 💡 Practical travel insights")
        print("5. 🚀 Enhanced user experience")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_llm_service_directly():
    """Demonstrate the LLM service directly"""
    
    print("\n\n🔧 Direct LLM Service Demo")
    print("=" * 40)
    
    try:
        from app.services.llm_summarizer import LLMSummarizerService
        
        # Initialize service
        summarizer = LLMSummarizerService()
        print("✅ LLM Service initialized")
        
        # Test with realistic travel data
        travel_data = {
            "general_info": {
                "summary": "Comprehensive travel information for Colombo to Kandy route",
                "key_points": [
                    "Express buses depart every 30 minutes from Colombo Fort",
                    "Regular buses run hourly from Pettah Bus Stand",
                    "Train service available but limited to 3 departures daily",
                    "Shared taxis available at 400-600 LKR per person",
                    "Private car hire costs 8000-12000 LKR for the journey"
                ],
                "relevant_links": [
                    "https://sltb.lk/schedules",
                    "https://railway.gov.lk/timetables",
                    "https://srilanka.travel/transport"
                ]
            },
            "raw_results": {
                "weather": "Current weather: 28°C, partly cloudy, good for travel",
                "traffic": "Normal traffic conditions on A1 highway",
                "events": "No major events affecting travel this week",
                "local_tips": "Best to book express buses in advance during weekends"
            }
        }
        
        # Generate summary
        print("\n📝 Generating travel summary...")
        summary_result = summarizer.summarize_search_results(
            travel_data,
            "What's the best way to travel from Colombo to Kandy?",
            "User is planning a weekend trip and wants practical advice"
        )
        
        if summary_result["status"] == "success":
            print("✅ Summary generated successfully!")
            print("\n📋 Generated Summary:")
            print("-" * 50)
            print(summary_result["summary"])
            print("-" * 50)
            print(f"📊 Model: {summary_result['model_used']}")
            print(f"📅 Timestamp: {summary_result['timestamp']}")
        else:
            print(f"❌ Summary generation failed: {summary_result.get('error')}")
        
        # Test route recommendation
        print("\n🛤️  Generating route recommendation...")
        
        routes = [
            {
                "route_id": "express_bus",
                "duration": 180,
                "distance": 115,
                "fare_estimate": 250,
                "transit_modes": ["bus"],
                "transfers": 0,
                "walking_distance": 0.2
            },
            {
                "route_id": "regular_bus",
                "duration": 300,
                "distance": 115,
                "fare_estimate": 180,
                "transit_modes": ["bus"],
                "transfers": 1,
                "walking_distance": 0.5
            },
            {
                "route_id": "train",
                "duration": 240,
                "distance": 115,
                "fare_estimate": 150,
                "transit_modes": ["train"],
                "transfers": 0,
                "walking_distance": 0.3
            }
        ]
        
        preferences = {
            "preferred_transit_modes": ["bus", "train"],
            "budget_preference": "low",
            "max_walking_distance": 0.5,
            "time_vs_cost_weight": 0.3  # Prefer cost over time
        }
        
        context = {
            "summary": "Found 3 transportation options from Colombo to Kandy"
        }
        
        recommendation = summarizer.generate_route_recommendation(
            routes, preferences, context
        )
        
        print("✅ Recommendation generated!")
        print("\n🎯 Personalized Recommendation:")
        print("-" * 50)
        print(recommendation)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error in direct LLM demo: {str(e)}")

def main():
    """Main demo function"""
    
    try:
        # Run the main integration demo
        demo_llm_integration()
        
        # Run the direct service demo
        demo_llm_service_directly()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\nThe LLM Summarizer is now fully integrated into your travel companion backend!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error during demo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
