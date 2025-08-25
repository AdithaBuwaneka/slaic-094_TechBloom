from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.transport import JourneyRequest, RouteOption
from app.services.google_maps_service1 import GoogleMapsService
from app.agents.graph import agentic_graph 
from pydantic import BaseModel

router = APIRouter()
gmaps_service = GoogleMapsService()

@router.post("/plan-journey/direct", response_model=List[RouteOption])
def get_direct_journey(request: JourneyRequest):
    if not request.origin or not request.destination:
        raise HTTPException(status_code=400, detail="Origin and destination cannot be empty.")
    routes = gmaps_service.get_directions(request.origin, request.destination, request.mode)
    if not routes:
        raise HTTPException(status_code=404, detail="Could not find a route for the given locations in Sri Lanka.")
    return routes


class AgenticJourneyRequest(BaseModel):
    query: str

@router.post("/plan-journey/agentic", response_model=Dict[str, Any])
async def get_agentic_journey(request: AgenticJourneyRequest):
    """
    Provides a route plan using the AI agentic workflow.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    # The input to the graph must be a dictionary with keys matching the GraphState
    inputs = {"user_query": request.query}

    # Run the graph
    final_state = await agentic_graph.ainvoke(inputs)
    
    return final_state