from typing import TypedDict, Optional, List, Dict, Any
from app.models.transport import RouteOption

class GraphState(TypedDict):
    """
    Represents the comprehensive state of our multi-agent system.

    Attributes:
        # Core journey information
        user_query: The initial question from the user.
        user_id: Unique identifier for personalization.
        origin: The starting point of the journey.
        destination: The ending point of the journey.
        transport_mode: Preferred transport mode(s).
        travel_time: Preferred travel time.
        passenger_type: Type of passenger (adult, student, senior, etc.).
        
        # Router decision
        tool_choice: The name of the tool selected by the router.
        
        # Agent outputs
        direct_route_options: Results from the Google Maps/Database tool.
        disruption_analysis: Output from disruption management agent.
        personalized_recommendations: Output from personalization agent.
        multilingual_response: Output from language & accessibility agent.
        fare_optimization: Output from fare optimization agent.
        local_insights: Output from local knowledge agent.
        
        # User preferences
        user_profile: User profile data for personalization.
        accessibility_needs: List of accessibility requirements.
        language_preference: Preferred language code.
        budget_preference: Budget constraints.
        
        # Final output
        final_response: The comprehensive, user-facing response.
        enhanced_response: Multilingual and accessible version.
    """
    # Core journey information
    user_query: str
    user_id: Optional[str]
    origin: Optional[str]
    destination: Optional[str]
    transport_mode: Optional[str]
    travel_time: Optional[str]
    passenger_type: Optional[str]
    
    # Router decision
    tool_choice: str
    
    # Agent outputs
    direct_route_options: Optional[List[RouteOption]]
    disruption_analysis: Optional[Dict[str, Any]]
    personalized_recommendations: Optional[Dict[str, Any]]
    multilingual_response: Optional[Dict[str, Any]]
    fare_optimization: Optional[Dict[str, Any]]
    local_insights: Optional[Dict[str, Any]]
    
    # User preferences  
    user_profile: Optional[Dict[str, Any]]
    accessibility_needs: Optional[List[str]]
    language_preference: Optional[str]
    budget_preference: Optional[float]
    
    # Final output
    final_response: Optional[str]
    enhanced_response: Optional[Dict[str, Any]]