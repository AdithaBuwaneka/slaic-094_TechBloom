from typing import TypedDict, Optional, List
from app.models.transport import RouteOption

class GraphState(TypedDict):
    """
    Represents the state of our agent.

    Attributes:
        user_query: The initial question from the user.
        origin: The starting point of the journey.
        destination: The ending point of the journey.
        tool_choice: The name of the tool selected by the router.
        direct_route_options: The results from the Google Maps tool.
        # We will add more fields for DB results later
        final_response: The final, user-facing response.
    """
    user_query: str
    origin: Optional[str]
    destination: Optional[str]
    tool_choice: str
    direct_route_options: Optional[List[RouteOption]]
    final_response: Optional[str]