from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from app.models.travel_schema import TravelState
from app.services.agent_nodes import *
from app.services.langfuse_service import langfuse_service
from datetime import datetime

def create_travel_agent_workflow():
    """
    Create the LangGraph workflow for the multi-agent travel system
    """
    
    # Initialize the state graph
    workflow = StateGraph(TravelState)
    
    # Add all nodes
    workflow.add_node("input_processing", input_processing_node)
    workflow.add_node("mode_router", mode_router_node)
    workflow.add_node("standard_route", standard_route_node)
    workflow.add_node("transit_route_aggregation", transit_route_aggregation_node)
    workflow.add_node("fare_calculation", fare_calculation_node)
    workflow.add_node("user_preference_analysis", user_preference_analysis_node)
    workflow.add_node("local_knowledge_agent", local_knowledge_agent_node)
    workflow.add_node("disruption_monitoring", disruption_monitoring_node)
    workflow.add_node("route_optimization", route_optimization_node)
    workflow.add_node("response_compilation", response_compilation_node)
    
    # Define the workflow edges
    
    # Start with input processing
    workflow.add_edge(START, "input_processing")
    workflow.add_edge("input_processing", "mode_router")
    
    # Conditional routing based on mode
    workflow.add_conditional_edges(
        "mode_router",
        should_use_multi_agent,
        {
            "standard_processing": "standard_route",
            "transit_processing": "transit_route_aggregation"
        }
    )
    
    # Standard route processing (direct to optimization)
    workflow.add_edge("standard_route", "route_optimization")
    
    # Multi-agent transit processing (parallel execution)
    workflow.add_edge("transit_route_aggregation", "fare_calculation")
    workflow.add_edge("transit_route_aggregation", "user_preference_analysis")
    workflow.add_edge("transit_route_aggregation", "local_knowledge_agent")
    
    # All parallel agents feed into optimization
    workflow.add_edge("fare_calculation", "route_optimization")
    workflow.add_edge("user_preference_analysis", "route_optimization")
    workflow.add_edge("local_knowledge_agent", "route_optimization")
    
    # Optimization leads to disruption monitoring
    workflow.add_edge("route_optimization", "disruption_monitoring")
    
    # Disruption monitoring leads to final compilation
    workflow.add_edge("disruption_monitoring", "response_compilation")
    
    # End with response compilation
    workflow.add_edge("response_compilation", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
    # If Langfuse is enabled, wrap with callbacks for automatic tracing
    if langfuse_service.is_enabled():
        compiled_workflow = compiled_workflow.with_config({
            "callbacks": [langfuse_service.get_handler()]
        })
    
    return compiled_workflow

# Utility function to run the workflow
def run_travel_agent(source: str, destination: str, mode: str, 
                    user_id: str, preferred_transit: str = None) -> Dict:
    """
    Run the complete travel agent workflow with Langfuse tracing
    """
    
    # Create initial state
    initial_state = TravelState(
        source=source,
        destination=destination,
        mode=mode,
        user_id=user_id,
        preferred_transit=preferred_transit
    )
    
    # Create and run workflow
    workflow = create_travel_agent_workflow()
    
    # Create Langfuse trace for this request
    trace = None
    if langfuse_service.is_enabled():
        trace = langfuse_service.create_trace(
            name="travel-agent-request",
            user_id=user_id,
            metadata={
                "source": source,
                "destination": destination,
                "mode": mode,
                "preferred_transit": preferred_transit,
                "request_timestamp": datetime.now().isoformat()
            }
        )
    
    try:
        # Execute the workflow
        final_state = workflow.invoke(initial_state)
        
        # Update trace with final results if tracing is enabled
        if trace:
            trace.update(
                output={
                    "status": "success",
                    "response": final_state.get("final_response", "No response generated"),
                    "agents_used": final_state.get("agents_completed", []),
                    "processing_time": (datetime.now() - initial_state.processing_start_time).total_seconds()
                }
            )
        
        # Return the final response
        return {
            "status": "success",
            "response": final_state.get("final_response", "No response generated"),  
            "processing_time": (datetime.now() - initial_state.processing_start_time).total_seconds(),
            "agents_used": final_state.get("agents_completed", []),
            "trace_id": trace.id if trace else None
        }
        
    except Exception as e:
        # Update trace with error information if tracing is enabled
        if trace:
            trace.update(
                output={
                    "status": "error",
                    "error": str(e),
                    "processing_time": (datetime.now() - initial_state.processing_start_time).total_seconds()
                }
            )
        
        return {
            "status": "error",
            "error": str(e),
            "processing_time": (datetime.now() - initial_state.processing_start_time).total_seconds(),
            "trace_id": trace.id if trace else None
        }
    
    finally:
        # Flush events to Langfuse
        if langfuse_service.is_enabled():
            langfuse_service.flush()

# Example usage and testing
if __name__ == "__main__":
    # Test the workflow
    
    # Test 1: Standard driving route
    print("Testing driving route...")
    result1 = run_travel_agent(
        source="Times Square, New York",
        destination="Brooklyn Bridge, New York",
        mode="driving",
        user_id="user_123"
    )
    print(f"Driving result: {result1['status']}")
    
    # Test 2: Transit route with multi-agent processing
    print("\nTesting transit route...")
    result2 = run_travel_agent(
        source="Manhattan, New York",
        destination="Queens, New York", 
        mode="transit",
        user_id="user_123",
        preferred_transit="train"
    )
    print(f"Transit result: {result2['status']}")
    
    # Test 3: Uber route
    print("\nTesting Uber route...")
    result3 = run_travel_agent(
        source="Central Park, New York",
        destination="JFK Airport, New York",
        mode="uber",
        user_id="user_123"
    )
    print(f"Uber result: {result3['status']}")
    
    print("\nAll tests completed!")