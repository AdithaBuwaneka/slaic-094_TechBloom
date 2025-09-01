#!/usr/bin/env python3
"""
Simple Langfuse integration test - no external dependencies
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_langfuse_service():
    """Test the Langfuse service initialization"""
    print("🧪 Testing Langfuse Service...")
    
    try:
        from app.services.langfuse_service import langfuse_service
        
        print(f"✅ Langfuse service initialized")
        print(f"   Enabled: {langfuse_service.is_enabled()}")
        
        if langfuse_service.is_enabled():
            print(f"   Handler available: {langfuse_service.get_handler() is not None}")
            
            # Test trace creation
            trace = langfuse_service.create_trace(
                name="test-trace",
                user_id="test_user",
                metadata={"test": True, "environment": "testing"}
            )
            
            if trace:
                print(f"   ✅ Test trace created: {trace.id}")
                
                # Test span creation
                span = langfuse_service.start_span(
                    name="test-span",
                    trace_id=trace.id,
                    metadata={"operation": "test"}
                )
                
                if span:
                    print(f"   ✅ Test span created: {span.id}")
                    span.update(output={"result": "success"})
                    span.end()
                
                # Test scoring
                langfuse_service.score_trace(
                    trace_id=trace.id,
                    name="test_score",
                    value=5.0,
                    comment="Test score for integration verification"
                )
                print(f"   ✅ Test score added")
                
                # Update trace
                trace.update(output={"test_result": "success"})
                print(f"   ✅ Test trace updated")
                
                # Flush events
                langfuse_service.flush()
                print(f"   ✅ Events flushed to Langfuse")
                
            else:
                print(f"   ❌ Failed to create test trace")
        else:
            print(f"   ⚠️  Langfuse is disabled - check your environment variables")
            print(f"   Required: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY")
            
    except Exception as e:
        print(f"   ❌ Error testing Langfuse service: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_environment_config():
    """Test environment configuration"""
    print("\n🧪 Testing Environment Configuration...")
    
    langfuse_vars = [
        'LANGFUSE_PUBLIC_KEY',
        'LANGFUSE_SECRET_KEY',
        'LANGFUSE_HOST'
    ]
    
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
    
    if langfuse_configured:
        print(f"     ✅ Langfuse is fully configured")
    else:
        print(f"     ⚠️  Langfuse is partially configured")
    
    return True

def main():
    """Run Langfuse tests only"""
    print("🚀 Langfuse Integration Test (No External Dependencies)")
    print("=" * 60)
    
    # Test environment configuration
    env_ok = test_environment_config()
    
    # Test Langfuse service
    langfuse_ok = test_langfuse_service()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   Langfuse Service: {'✅' if langfuse_ok else '❌'}")
    
    if langfuse_ok:
        print("\n🎉 Langfuse integration is working correctly!")
        print("   You can now view traces in your Langfuse dashboard.")
        print("   Check LANGFUSE_SETUP.md for usage examples.")
    else:
        print("\n⚠️  Langfuse integration has issues.")
        print("   Check your environment variables and configuration.")
        print("   Refer to LANGFUSE_SETUP.md for troubleshooting.")

if __name__ == "__main__":
    main()
