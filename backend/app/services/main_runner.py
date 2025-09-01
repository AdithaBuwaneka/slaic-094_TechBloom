"""
Multi-Agent Travel System
Main application entry point
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from app.services.workflow import run_travel_agent
from app.services.langfuse_service import langfuse_service

# Load environment variables
load_dotenv()

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        'GOOGLE_MAPS_API_KEY',
        'SERPER_API_KEY', 
        'MONGODB_CONNECTION_STRING'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all variables are set.")
        return False
    
    print("✅ Environment variables validated")
    
    # Check Langfuse configuration
    if langfuse_service.is_enabled():
        print("✅ Langfuse tracing enabled")
    else:
        print("⚠️  Langfuse tracing disabled (configure LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable)")
    
    return True

def print_route_results(result):
    """Pretty print route results"""
    if result["status"] == "error":
        print(f"❌ Error: {result['error']}")
        return
    
    response = result["response"]
    print(f"\n📍 Route Results:")
    print(f"   Request ID: {response['request_id']}")
    print(f"   From: {response['query']['source']}")
    print(f"   To: {response['query']['destination']}")
    print(f"   Mode: {response['query']['mode']}")
    print(f"   Processing time: {result['processing_time']:.2f}s")
    print(f"   Agents used: {', '.join(result['agents_used'])}")
    
    # Show trace ID if Langfuse is enabled
    if result.get('trace_id'):
        print(f"   🔍 Trace ID: {result['trace_id']}")
        print(f"      View in Langfuse: https://cloud.langfuse.com/traces/{result['trace_id']}")
    
    print(f"\n🛤️  Recommended Routes ({len(response['recommended_routes'])}):")
    for i, route in enumerate(response['recommended_routes'], 1):
        print(f"\n   Route {i}:")
        print(f"      Duration: {route['summary']['duration_minutes']} min")
        print(f"      Distance: {route['summary']['distance_km']:.1f} km")
        if route['summary']['estimated_fare']:
            print(f"      Fare: ${route['summary']['estimated_fare']:.2f}")
        print(f"      Score: {route['score']['overall']:.2f}")
        
        if 'transit_info' in route:
            transit = route['transit_info']
            print(f"      Transit: {', '.join(transit['modes'])}")
            if transit['transfers'] > 0:
                print(f"      Transfers: {transit['transfers']}")
            print(f"      Walking: {transit['walking_distance_km']:.2f} km")
        
        if 'last_mile' in route:
            lm = route['last_mile']
            print(f"      Last mile: {lm['mode']} (${lm['cost']:.2f}, {lm['duration']:.0f} min)")
    
    # Show disruptions if any
    if 'disruptions' in response:
        print(f"\n⚠️  Active Disruptions ({len(response['disruptions'])}):")
        for disruption in response['disruptions']:
            print(f"   - {disruption['type']} at {disruption['location']} ({disruption['severity']})")
    
    # Show warnings if any
    if 'warnings' in response:
        print(f"\n⚠️  Warnings:")
        for warning in response['warnings']:
            print(f"   - {warning['source']}: {warning['message']}")

def interactive_mode():
    """Run interactive mode for testing"""
    print("\n🎮 Interactive Mode")
    print("=" * 50)
    
    while True:
        try:
            print("\nEnter travel details (or 'quit' to exit):")
            
            # Get user input
            source = input("📍 From: ").strip()
            if source.lower() == 'quit':
                break
                
            destination = input("📍 To: ").strip()
            if destination.lower() == 'quit':
                break
            
            print("\nTravel modes:")
            print("  1. driving")
            print("  2. two_wheeler") 
            print("  3. transit")
            print("  4. uber")
            
            mode_choice = input("Select mode (1-4): ").strip()
            mode_map = {"1": "driving", "2": "two_wheeler", "3": "transit", "4": "uber"}
            mode = mode_map.get(mode_choice, "driving")
            
            preferred_transit = None
            if mode == "transit":
                transit_choice = input("Preferred transit (bus/train/any): ").strip()
                preferred_transit = transit_choice if transit_choice != "any" else None
            
            user_id = input("User ID (or press Enter for default): ").strip() or "user_123"
            
            print(f"\n🚀 Processing route from {source} to {destination} via {mode}...")
            
            # Run the travel agent
            result = run_travel_agent(
                source=source,
                destination=destination,
                mode=mode,
                user_id=user_id,
                preferred_transit=preferred_transit
            )
            
            # Display results
            print_route_results(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def run_demo_scenarios():
    """Run pre-defined demo scenarios"""
    print("\n🎬 Demo Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "NYC Driving Route",
            "source": "Times Square, New York",
            "destination": "Brooklyn Bridge, New York", 
            "mode": "driving",
            "user_id": "demo_user_1"
        },
        {
            "name": "NYC Transit Route",
            "source": "Manhattan, New York",
            "destination": "JFK Airport, New York",
            "mode": "transit",
            "user_id": "demo_user_2",
            "preferred_transit": "train"
        },
        {
            "name": "NYC Uber Route",
            "source": "Central Park, New York",
            "destination": "Wall Street, New York",
            "mode": "uber", 
            "user_id": "demo_user_3"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['name']}")
        print("-" * 30)
        
        result = run_travel_agent(
            source=scenario["source"],
            destination=scenario["destination"],
            mode=scenario["mode"],
            user_id=scenario["user_id"],
            preferred_transit=scenario.get("preferred_transit")
        )
        
        print_route_results(result)
        
        input("\n Press Enter to continue to next scenario...")

def main():
    """Main application function"""
    print("🚀 Multi-Agent Travel System")
    print("=" * 50)
    
    # Validate environment
    if not validate_environment():
        return
    
    # Setup database
    # setup_choice = input("\n🗄️  Setup database with dummy data? (y/n): ").lower()
    # if setup_choice == 'y':
    #     if not setup_database():
    #         print("❌ Cannot continue without database setup")
    #         return
    
    # Choose mode
    print("\n🎯 Choose operation mode:")
    print("  1. Interactive mode")
    print("  2. Demo scenarios")
    print("  3. Single test")
    
    choice = input("\nSelect mode (1-3): ").strip()
    
    if choice == "1":
        interactive_mode()
    elif choice == "2":
        run_demo_scenarios()
    elif choice == "3":
        # Single test
        print("\n🧪 Running single test...")
        result = run_travel_agent(
            source="Times Square, New York",
            destination="Brooklyn Bridge, New York",
            mode="transit", 
            user_id="test_user",
            preferred_transit="subway"
        )
        print_route_results(result)
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()