from langgraph.graph import StateGraph, END
from .graph_state import GraphState
from .router_agent import RouterAgent
from .disruption_agent import DisruptionManagementAgent
from .personalization_agent import PersonalizationAgent
from .language_accessibility_agent import LanguageAccessibilityAgent
from .fare_optimization_agent import FareOptimizationAgent
from .local_knowledge_agent import LocalKnowledgeAgent
from app.services.google_maps_service1 import GoogleMapsService

# Agent and Service Initialization
router_agent = RouterAgent()
gmaps_service = GoogleMapsService()
disruption_agent = DisruptionManagementAgent()
personalization_agent = PersonalizationAgent()
language_agent = LanguageAccessibilityAgent()
fare_agent = FareOptimizationAgent()
local_knowledge_agent = LocalKnowledgeAgent()

# Core Data Retrieval Tools
async def google_maps_tool(state: GraphState) -> GraphState:
    """Node that calls the Google Maps service."""
    print("---EXECUTING GOOGLE MAPS TOOL---")
    origin = state['origin']
    destination = state['destination']
    
    if not origin or not destination:
        state['final_response'] = "I need both an origin and a destination for this request."
        return state

    routes = gmaps_service.get_directions(origin, destination)
    
    if not routes:
        state['final_response'] = "Sorry, I couldn't find a route."
        return state

    state['direct_route_options'] = routes
    return state

async def database_search_tool(state: GraphState) -> GraphState:
    """Node for searching Sri Lankan transport database."""
    print("---EXECUTING DATABASE SEARCH TOOL---")
    # This would query our Sri Lankan transport database
    state['final_response'] = "Database search functionality ready for Sri Lankan routes."
    return state

# Specialized Agent Nodes
async def disruption_analysis_node(state: GraphState) -> GraphState:
    """Analyze disruptions and provide alternative routes."""
    print("---ANALYZING DISRUPTIONS---")
    try:
        analysis = await disruption_agent.check_disruptions(
            origin=state['origin'] or "",
            destination=state['destination'] or "",
            transport_mode=state.get('transport_mode', 'any')
        )
        state['disruption_analysis'] = analysis.dict()
    except Exception as e:
        print(f"Disruption analysis error: {e}")
        state['disruption_analysis'] = {"severity_level": "unknown", "user_message": "Disruption check unavailable"}
    return state

async def personalization_node(state: GraphState) -> GraphState:
    """Generate personalized recommendations."""
    print("---PERSONALIZING RECOMMENDATIONS---")
    try:
        if state.get('direct_route_options'):
            # Convert route options to format expected by personalization agent
            routes_data = []
            for route in state['direct_route_options']:
                routes_data.append({
                    "summary": route.summary,
                    "duration": route.total_duration,
                    "distance": route.total_distance,
                    "legs": len(route.legs)
                })
            
            recommendations = await personalization_agent.get_personalized_recommendations(
                user_id=state.get('user_id', 'anonymous'),
                origin=state['origin'] or "",
                destination=state['destination'] or "",
                available_routes=routes_data,
                travel_time=state.get('travel_time')
            )
            state['personalized_recommendations'] = recommendations.dict()
    except Exception as e:
        print(f"Personalization error: {e}")
        state['personalized_recommendations'] = {"recommended_routes": ["Standard recommendation"]}
    return state

async def fare_optimization_node(state: GraphState) -> GraphState:
    """Optimize fares and provide cost analysis."""
    print("---OPTIMIZING FARES---")
    try:
        if state.get('direct_route_options'):
            routes_data = []
            for route in state['direct_route_options']:
                routes_data.append({
                    "transport_mode": "mixed",
                    "distance": route.total_distance,
                    "duration": route.total_duration
                })
            
            optimization = await fare_agent.optimize_fare(
                origin=state['origin'] or "",
                destination=state['destination'] or "",
                available_routes=routes_data,
                passenger_type=state.get('passenger_type', 'adult'),
                budget_preference=state.get('budget_preference')
            )
            state['fare_optimization'] = optimization.dict()
    except Exception as e:
        print(f"Fare optimization error: {e}")
        state['fare_optimization'] = {"total_cost": 100.0, "cheapest_route": "Standard fare"}
    return state

async def local_knowledge_node(state: GraphState) -> GraphState:
    """Add local knowledge and community insights."""
    print("---GATHERING LOCAL INSIGHTS---")
    try:
        insights = await local_knowledge_agent.get_local_insights(
            origin=state['origin'] or "",
            destination=state['destination'] or "",
            transport_mode=state.get('transport_mode', 'any'),
            travel_time=state.get('travel_time')
        )
        state['local_insights'] = insights.dict()
    except Exception as e:
        print(f"Local knowledge error: {e}")
        state['local_insights'] = {"local_tips": ["Check with locals for current conditions"]}
    return state

async def language_accessibility_node(state: GraphState) -> GraphState:
    """Generate multilingual and accessible responses."""
    print("---ENHANCING ACCESSIBILITY---")
    try:
        # Compile all information for translation
        content_to_translate = f"""
        Route: {state['origin']} to {state['destination']}
        Disruption Status: {state.get('disruption_analysis', {}).get('user_message', 'No issues reported')}
        Cost: {state.get('fare_optimization', {}).get('total_cost', 'Contact operator')}
        Local Tips: {state.get('local_insights', {}).get('local_tips', [])}
        """
        
        multilingual_response = await language_agent.translate_response(
            content=content_to_translate.strip(),
            preferred_language=state.get('language_preference', 'en'),
            accessibility_needs=state.get('accessibility_needs', []),
            user_type="local"
        )
        state['multilingual_response'] = multilingual_response.dict()
    except Exception as e:
        print(f"Language/accessibility error: {e}")
        state['multilingual_response'] = {"primary_language_response": "Standard response available"}
    return state

async def response_synthesis_node(state: GraphState) -> GraphState:
    """Synthesize all agent outputs into final response."""
    print("---SYNTHESIZING FINAL RESPONSE---")
    
    # Get route information
    routes_info = ""
    if state.get('direct_route_options'):
        route = state['direct_route_options'][0]  # Best route
        routes_info = f"Best route takes {route.total_duration} covering {route.total_distance}"
    
    # Get disruption info
    disruption_info = ""
    if state.get('disruption_analysis'):
        disruption_info = state['disruption_analysis'].get('user_message', '')
    
    # Get cost info
    cost_info = ""
    if state.get('fare_optimization'):
        cost = state['fare_optimization'].get('total_cost', 'N/A')
        cost_info = f"Estimated cost: LKR {cost}"
    
    # Get personalization info
    personal_info = ""
    if state.get('personalized_recommendations'):
        reason = state['personalized_recommendations'].get('personalization_reason', '')
        personal_info = f"Personalized: {reason}"
    
    # Get local insights
    local_info = ""
    if state.get('local_insights'):
        tips = state['local_insights'].get('local_tips', [])
        if tips:
            local_info = f"Local tip: {tips[0]}"
    
    # Compile final response
    response_parts = [part for part in [routes_info, disruption_info, cost_info, personal_info, local_info] if part]
    state['final_response'] = " | ".join(response_parts)
    
    # Enhanced response with multilingual support
    if state.get('multilingual_response'):
        state['enhanced_response'] = {
            'standard': state['final_response'],
            'multilingual': state['multilingual_response']
        }
    
    return state

# Conditional Logic
def should_continue_to_agents(state: GraphState) -> str:
    """Determine if we should proceed to specialized agents after data retrieval."""
    if state.get('direct_route_options') or state.get('tool_choice') == 'database_search':
        return 'disruption_analysis'
    return 'response_synthesis'

def should_continue_after_router(state: GraphState) -> str:
    """Determines which data retrieval tool to use."""
    print(f"---ROUTER DECISION: {state['tool_choice']}---")
    if state['tool_choice'] == 'google_maps_search':
        return 'google_maps_tool'
    elif state['tool_choice'] == 'database_search':
        return 'database_search_tool'
    return 'response_synthesis'

# Graph Definition
def build_graph():
    """Builds and compiles the comprehensive multi-agent LangGraph."""
    workflow = StateGraph(GraphState)

    # Add all nodes
    workflow.add_node("router", router_agent.route_query)
    workflow.add_node("google_maps_tool", google_maps_tool)
    workflow.add_node("database_search_tool", database_search_tool)
    workflow.add_node("disruption_analysis", disruption_analysis_node)
    workflow.add_node("personalization", personalization_node)
    workflow.add_node("fare_optimization", fare_optimization_node)
    workflow.add_node("local_knowledge", local_knowledge_node)
    workflow.add_node("language_accessibility", language_accessibility_node)
    workflow.add_node("response_synthesis", response_synthesis_node)

    # Set the entry point
    workflow.set_entry_point("router")

    # Router to data retrieval tools
    workflow.add_conditional_edges(
        "router",
        should_continue_after_router,
        {
            "google_maps_tool": "google_maps_tool",
            "database_search_tool": "database_search_tool",
            "response_synthesis": "response_synthesis"
        }
    )

    # Data retrieval tools to specialized agents
    workflow.add_conditional_edges(
        "google_maps_tool",
        should_continue_to_agents,
        {
            "disruption_analysis": "disruption_analysis",
            "response_synthesis": "response_synthesis"
        }
    )
    
    workflow.add_conditional_edges(
        "database_search_tool",
        should_continue_to_agents,
        {
            "disruption_analysis": "disruption_analysis", 
            "response_synthesis": "response_synthesis"
        }
    )

    # Sequential flow through specialized agents
    workflow.add_edge("disruption_analysis", "personalization")
    workflow.add_edge("personalization", "fare_optimization")
    workflow.add_edge("fare_optimization", "local_knowledge")
    workflow.add_edge("local_knowledge", "language_accessibility")
    workflow.add_edge("language_accessibility", "response_synthesis")

    # Final node to end
    workflow.add_edge("response_synthesis", END)

    # Compile the graph
    return workflow.compile()

# Create a single instance of the compiled graph
agentic_graph = build_graph()