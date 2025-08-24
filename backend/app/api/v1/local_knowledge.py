from fastapi import APIRouter, HTTPException
from app.agents.agent_manager import agent_manager
from app.agents.local_knowledge_agent import LocalKnowledgeAgent
from app.models.local_knowledge import (
    LocalKnowledgeQuery, CreateKnowledgeRequest, UpdateKnowledgeRequest,
    CulturalInsightRequest, TouristGuidanceRequest
)
from app.models.transport_data import Location
from typing import Dict, Any

router = APIRouter()


@router.post("/query")
async def get_local_knowledge(request: LocalKnowledgeQuery):
    """Get comprehensive local knowledge for a location"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get local knowledge
        result = await agent_manager.orchestrate_request(
            request_type="get_local_knowledge",
            payload=request.model_dump(),
            timeout=8.0
        )
        
        return {
            "status": "success",
            "message": "Local knowledge retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/create")
async def create_knowledge_entry(request: CreateKnowledgeRequest):
    """Create a new local knowledge entry"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Create knowledge entry
        result = await agent_manager.orchestrate_request(
            request_type="create_knowledge_entry",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Knowledge entry created successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/update")
async def update_knowledge_entry(request: UpdateKnowledgeRequest):
    """Update an existing knowledge entry"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Update knowledge entry
        result = await agent_manager.orchestrate_request(
            request_type="update_knowledge_entry",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Knowledge entry updated successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/cultural-insights")
async def get_cultural_insights(request: CulturalInsightRequest):
    """Get cultural insights for a specific location and user type"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get cultural insights
        result = await agent_manager.orchestrate_request(
            request_type="get_cultural_insights",
            payload=request.model_dump(),
            timeout=6.0
        )
        
        return {
            "status": "success",
            "message": "Cultural insights retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/tourist-guidance")
async def get_tourist_guidance(request: TouristGuidanceRequest):
    """Get comprehensive tourist guidance for a journey"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get tourist guidance
        result = await agent_manager.orchestrate_request(
            request_type="get_tourist_guidance",
            payload=request.model_dump(),
            timeout=8.0
        )
        
        return {
            "status": "success",
            "message": "Tourist guidance retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/safety-info")
async def get_safety_information(location: Location):
    """Get safety information for a location"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get safety information
        result = await agent_manager.orchestrate_request(
            request_type="get_safety_information",
            payload={"location": location.model_dump()},
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Safety information retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/events")
async def get_local_events(request: Dict[str, Any]):
    """Get upcoming local events for a location"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get local events
        result = await agent_manager.orchestrate_request(
            request_type="get_local_events",
            payload=request,
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Local events retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/recommendations")
async def get_recommendations(request: LocalKnowledgeQuery):
    """Get local recommendations for a location"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get recommendations
        result = await agent_manager.orchestrate_request(
            request_type="get_recommendations",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Recommendations retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/test")
async def test_local_knowledge_agent():
    """Test the local knowledge agent functionality"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Test basic functionality by getting knowledge for Kandy
        test_query = LocalKnowledgeQuery(
            location=Location(
                latitude=7.2906,
                longitude=80.6337,
                address="Kandy, Central Province"
            ),
            radius_km=20.0,
            user_type="tourist",
            language="en"
        )
        
        result = await agent_manager.orchestrate_request(
            request_type="get_local_knowledge",
            payload=test_query.model_dump(),
            timeout=8.0
        )
        
        return {
            "status": "success",
            "message": "Local Knowledge Agent is operational",
            "agent_info": {
                "agent_id": "local_knowledge_agent",
                "name": "Local Knowledge Agent",
                "running": True
            },
            "test_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent test failed: {str(e)}")


@router.get("/attractions/{location_name}")
async def get_attractions_by_location(location_name: str):
    """Get tourist attractions for a named location"""
    try:
        # Register local knowledge agent if not already registered
        if "local_knowledge_agent" not in agent_manager.agents:
            local_knowledge_agent = LocalKnowledgeAgent()
            await agent_manager.register_agent(local_knowledge_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Map common location names to coordinates
        location_map = {
            "kandy": Location(latitude=7.2906, longitude=80.6337, address="Kandy"),
            "colombo": Location(latitude=6.9271, longitude=79.8612, address="Colombo"),
            "galle": Location(latitude=6.0535, longitude=80.2210, address="Galle"),
            "anuradhapura": Location(latitude=8.3114, longitude=80.4037, address="Anuradhapura"),
            "sigiriya": Location(latitude=7.9568, longitude=80.7592, address="Sigiriya")
        }
        
        location = location_map.get(location_name.lower())
        if not location:
            # Default location if not found
            location = Location(latitude=7.8731, longitude=80.7718, address=location_name)
        
        # Create query for tourist attractions
        query = LocalKnowledgeQuery(
            location=location,
            radius_km=25.0,
            user_type="tourist",
            language="en",
            include_tourist_attractions=True
        )
        
        result = await agent_manager.orchestrate_request(
            request_type="get_local_knowledge",
            payload=query.model_dump(),
            timeout=6.0
        )
        
        return {
            "status": "success",
            "message": f"Attractions for {location_name} retrieved successfully",
            "location": location.model_dump(),
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attractions: {str(e)}")