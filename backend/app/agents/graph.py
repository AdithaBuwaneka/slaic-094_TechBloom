from langgraph.graph import StateGraph, END
from .graph_state import GraphState
from .router_agent import RouterAgent
from app.services.google_maps_service1 import GoogleMapsService

# Agent and Service Initialization
router_agent = RouterAgent()
gmaps_service = GoogleMapsService()

async def google_maps_tool(state: GraphState) -> GraphState:
    """Node that calls the Google Maps service."""
    print("---EXECUTING GOOGLE MAPS TOOL---")
    origin = state['origin']
    destination = state['destination']
    
    if not origin or not destination:
        state['final_response'] = "I need both an origin and a destination for this request."
        return state

    # This calls the real service 
    routes = gmaps_service.get_directions(origin, destination)
    
    if not routes:
        state['final_response'] = "Sorry, I couldn't find a route on Google Maps."
        return state

    state['direct_route_options'] = routes

    state['final_response'] = f"Found {len(routes)} options on Google Maps. The best option takes {routes[0].total_duration}."
    return state

async def database_search_tool(state: GraphState) -> GraphState:
    """Placeholder node for searching our mock database."""
    print("---EXECUTING DATABASE SEARCH TOOL---")
    # The logic is not implemented yet
    state['final_response'] = "This query would use the database. The logic for this is not yet implemented."
    return state


# Conditional Logic
def should_continue(state: GraphState) -> str:
    """Determines which tool to call based on the router's decision."""
    print(f"---DECIDING NEXT STEP based on: {state['tool_choice']}---")
    if state['tool_choice'] == 'google_maps_search':
        return 'google_maps_tool'
    elif state['tool_choice'] == 'database_search':
        return 'database_search_tool'
    return END

# Graph Definition 
def build_graph():
    """Builds and compiles the LangGraph agent."""
    workflow = StateGraph(GraphState)

    # Add the nodes
    workflow.add_node("router", router_agent.route_query)
    workflow.add_node("google_maps_tool", google_maps_tool)
    workflow.add_node("database_search_tool", database_search_tool)

    # Set the entry point
    workflow.set_entry_point("router")

    # Add the conditional edges
    workflow.add_conditional_edges(
        "router",
        should_continue,
        {
            "google_maps_tool": "google_maps_tool",
            "database_search_tool": "database_search_tool",
        }
    )

    # Add edges from the tools back to the end
    workflow.add_edge('google_maps_tool', END)
    workflow.add_edge('database_search_tool', END)

    # Compile the graph
    return workflow.compile()

# Create a single instance of the compiled graph
agentic_graph = build_graph()