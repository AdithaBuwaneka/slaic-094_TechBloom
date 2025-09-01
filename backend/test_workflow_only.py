#!/usr/bin/env python3
"""
Simple test script for the workflow without database connections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.workflow import create_travel_agent_workflow
from app.models.travel_schema import TravelState
from datetime import datetime

def test_workflow_creation():
    """Test that the workflow can be created without errors"""
    try:
        print("🔄 Testing workflow creation...")
        workflow = create_travel_agent_workflow()
        print("✅ Workflow created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return False

def test_workflow_execution():
    """Test that the workflow can be executed without the request_id error"""
    try:
        print("🔄 Testing workflow execution...")
        
        # Create initial state
        initial_state = TravelState(
            source="colombo",
            destination="kandy",
            mode="transit",
            user_id="test_user",
            preferred_transit="bus"
        )
        
        # Create workflow
        workflow = create_travel_agent_workflow()
        
        # Try to invoke the workflow
        print("   Invoking workflow...")
        final_state = workflow.invoke(initial_state)
        print("✅ Workflow executed successfully")
        
        # Check what type we got back
        print(f"   Return type: {type(final_state)}")
        
        # LangGraph converts Pydantic models to dicts, which is normal
        if isinstance(final_state, dict):
            print("   ℹ️  Info: Workflow returned dict (normal LangGraph behavior)")
            print(f"   Dict keys: {list(final_state.keys())}")
            
            # Check if the dict contains the expected TravelState fields
            if 'current_step' in final_state and 'agents_completed' in final_state:
                print(f"   Final step: {final_state['current_step']}")
                print(f"   Agents completed: {final_state['agents_completed']}")
                print(f"   Errors: {len(final_state.get('errors', []))}")
                return True
            else:
                print("   ❌ Error: Dict missing expected TravelState fields")
                return False
        else:
            # If it's a TravelState object, that's also fine
            print(f"   Final step: {final_state.current_step}")
            print(f"   Agents completed: {final_state.agents_completed}")
            print(f"   Errors: {len(final_state.errors)}")
            return True
        
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return False

def test_workflow_with_run_function():
    """Test the run_travel_agent function which returns a dict"""
    try:
        print("🔄 Testing run_travel_agent function...")
        
        from app.services.workflow import run_travel_agent
        
        # Test the function
        result = run_travel_agent(
            source="colombo",
            destination="kandy", 
            mode="transit",
            user_id="test_user",
            preferred_transit="bus"
        )
        
        print("✅ run_travel_agent executed successfully")
        print(f"   Status: {result['status']}")
        print(f"   Processing time: {result['processing_time']:.2f}s")
        print(f"   Agents used: {result['agents_used']}")
        
        if result['status'] == 'success':
            response = result['response']
            print(f"   Request ID: {response.get('request_id', 'N/A')}")
            print(f"   Routes found: {len(response.get('recommended_routes', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error executing run_travel_agent: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Workflow Without Database")
    print("=" * 50)
    
    # Test 1: Workflow creation
    if not test_workflow_creation():
        sys.exit(1)
    
    print()
    
    # Test 2: Workflow execution
    if not test_workflow_execution():
        sys.exit(1)
    
    print()
    
    # Test 3: run_travel_agent function
    if not test_workflow_with_run_function():
        sys.exit(1)
    
    print("\n🎉 All tests passed! The workflow is working correctly.")
