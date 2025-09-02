#!/usr/bin/env python3
"""
Test script for Langfuse agent action tracing
This script tests the updated Langfuse integration to ensure agent actions are properly traced
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_langfuse_agent_tracing():
    """Test the Langfuse agent action tracing"""
    print("🧪 Testing Langfuse Agent Action Tracing...")
    
    try:
        from app.services.langfuse_service import langfuse_service
        from app.services.workflow import run_travel_agent
        
        # Check if Langfuse is enabled
        if not langfuse_service.is_enabled():
            print("❌ Langfuse is not enabled. Please configure LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")
            return False
        
        print("✅ Langfuse service is enabled")
        
        # Test 1: Simple trace creation
        print("\n📝 Test 1: Creating a simple trace...")
        trace = langfuse_service.create_trace(
            name="test-agent-trace",
            user_id="test_user_123",
            metadata={
                "test_type": "agent_tracing",
                "environment": "testing"
            }
        )
        
        if trace:
            print(f"✅ Trace created successfully: {trace.id}")
            
            # Test span creation
            print("\n🔍 Test 2: Creating agent spans...")
            with langfuse_service.start_span(
                name="test_agent_action",
                metadata={
                    "agent_type": "test_agent",
                    "action": "test_action"
                }
            ) as span:
                if span:
                    span.update(
                        input={"test_input": "test_value"},
                        output={"test_output": "success"}
                    )
                    print("✅ Agent span created and updated successfully")
                else:
                    print("❌ Failed to create agent span")
            
            # Update and end trace
            trace.update(output={"test_result": "success"})
            trace.end()
            print("✅ Trace updated and ended successfully")
            
        else:
            print("❌ Failed to create trace")
            return False
        
        # Test 3: Full workflow with agent tracing
        print("\n🚀 Test 3: Running full workflow with agent tracing...")
        
        result = run_travel_agent(
            source="Times Square, New York",
            destination="Brooklyn Bridge, New York",
            mode="driving",
            user_id="test_user_456"
        )
        
        if result["status"] == "success":
            print("✅ Workflow executed successfully")
            print(f"   Processing time: {result['processing_time']:.2f}s")
            print(f"   Agents used: {', '.join(result['agents_used'])}")
            
            if result.get('trace_id'):
                print(f"   🔍 Trace ID: {result['trace_id']}")
                print(f"      View in Langfuse: https://cloud.langfuse.com/traces/{result['trace_id']}")
            else:
                print("   ⚠️  No trace ID returned")
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test 4: Transit workflow (more complex agent interactions)
        print("\n🚌 Test 4: Running transit workflow with multiple agents...")
        
        result2 = run_travel_agent(
            source="Manhattan, New York",
            destination="JFK Airport, New York",
            mode="transit",
            user_id="test_user_789",
            preferred_transit="train"
        )
        
        if result2["status"] == "success":
            print("✅ Transit workflow executed successfully")
            print(f"   Processing time: {result2['processing_time']:.2f}s")
            print(f"   Agents used: {', '.join(result2['agents_used'])}")
            
            if result2.get('trace_id'):
                print(f"   🔍 Trace ID: {result2['trace_id']}")
                print(f"      View in Langfuse: https://cloud.langfuse.com/traces/{result2['trace_id']}")
        else:
            print(f"❌ Transit workflow failed: {result2.get('error', 'Unknown error')}")
            return False
        
        # Flush all events
        print("\n🔄 Flushing events to Langfuse...")
        langfuse_service.flush()
        print("✅ Events flushed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during agent tracing test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_config():
    """Test environment configuration for Langfuse"""
    print("\n🔧 Testing Environment Configuration...")
    
    required_vars = [
        'GOOGLE_MAPS_API_KEY',
        'SERPER_API_KEY',
        'MONGODB_CONNECTION_STRING'
    ]
    
    langfuse_vars = [
        'LANGFUSE_PUBLIC_KEY',
        'LANGFUSE_SECRET_KEY',
        'LANGFUSE_HOST'
    ]
    
    print("   Required variables:")
    all_required_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"     ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"     ❌ {var}: Not set")
            all_required_set = False
    
    print("   Langfuse variables:")
    langfuse_configured = True
    for var in langfuse_vars:
        value = os.getenv(var)
        if value:
            print(f"     ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"     ⚠️  {var}: Not set")
            if var in ['LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY']:
                langfuse_configured = False
    
    if not all_required_set:
        print("   ❌ Some required variables are missing")
        return False
    
    if langfuse_configured:
        print("   ✅ Langfuse is fully configured")
    else:
        print("   ⚠️  Langfuse is partially configured")
    
    return True

def main():
    """Run all agent tracing tests"""
    print("🚀 Langfuse Agent Action Tracing Test Suite")
    print("=" * 60)
    
    # Test environment configuration
    env_ok = test_environment_config()
    
    if not env_ok:
        print("\n❌ Environment configuration issues. Please fix and try again.")
        return
    
    # Test agent tracing
    tracing_ok = test_langfuse_agent_tracing()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   Agent Tracing: {'✅' if tracing_ok else '❌'}")
    
    if tracing_ok:
        print("\n🎉 Langfuse agent action tracing is working correctly!")
        print("   You can now view detailed agent traces in your Langfuse dashboard.")
        print("   Each agent action will be tracked as a separate span within the main trace.")
        print("\n📋 What you should see in Langfuse:")
        print("   • Main trace for each travel request")
        print("   • Individual spans for each agent action:")
        print("     - input_processing_agent")
        print("     - standard_route_agent (for driving routes)")
        print("     - local_knowledge_agent (for transit routes)")
        print("     - fare_calculation_agent")
        print("     - user_preference_analysis_agent")
        print("     - route_optimization_agent")
        print("     - response_compilation_agent")
        print("   • Input/output data for each agent")
        print("   • Performance metrics and timing")
        print("   • Error tracking if any agent fails")
    else:
        print("\n⚠️  Langfuse agent tracing has issues.")
        print("   Check your environment variables and configuration.")
        print("   Refer to LANGFUSE_SETUP.md for troubleshooting.")

if __name__ == "__main__":
    main()
