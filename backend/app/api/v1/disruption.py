from fastapi import APIRouter, HTTPException
from app.agents.agent_manager import agent_manager
from app.agents.disruption_management_agent import DisruptionManagementAgent
from app.models.disruption_management import (
    CreateDisruptionRequest, UpdateDisruptionRequest,
    DisruptionQuery, DisruptionMonitoringRequest
)
from typing import Dict, Any

router = APIRouter()


@router.post("/create")
async def create_disruption(request: CreateDisruptionRequest):
    """Create a new disruption alert"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Create disruption
        result = await agent_manager.orchestrate_request(
            request_type="create_disruption",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Disruption created successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/update")
async def update_disruption(request: UpdateDisruptionRequest):
    """Update an existing disruption"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Update disruption
        result = await agent_manager.orchestrate_request(
            request_type="update_disruption",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Disruption updated successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/query")
async def get_disruptions(request: DisruptionQuery):
    """Get disruptions based on query criteria"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Query disruptions
        result = await agent_manager.orchestrate_request(
            request_type="get_disruptions",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Disruptions retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/impact/{disruption_id}")
async def assess_disruption_impact(disruption_id: str):
    """Assess the impact of a specific disruption"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Assess impact
        result = await agent_manager.orchestrate_request(
            request_type="assess_impact",
            payload={"disruption_id": disruption_id},
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Impact assessment completed",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/contingency-plans")
async def get_contingency_plans(request: Dict[str, Any]):
    """Get contingency plans for specific disruption scenarios"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get contingency plans
        result = await agent_manager.orchestrate_request(
            request_type="get_contingency_plans",
            payload=request,
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Contingency plans retrieved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/monitor-route")
async def monitor_route(request: DisruptionMonitoringRequest):
    """Set up monitoring for a specific route"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Set up route monitoring
        result = await agent_manager.orchestrate_request(
            request_type="monitor_route",
            payload=request.model_dump(),
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Route monitoring set up successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/resolve/{disruption_id}")
async def resolve_disruption(disruption_id: str, resolution_data: Dict[str, Any] = None):
    """Resolve a disruption"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Prepare payload
        payload = {"disruption_id": disruption_id}
        if resolution_data:
            payload.update(resolution_data)
        
        # Resolve disruption
        result = await agent_manager.orchestrate_request(
            request_type="resolve_disruption",
            payload=payload,
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Disruption resolved successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/active")
async def get_active_disruptions():
    """Get all currently active disruptions"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Get active disruptions
        result = await agent_manager.orchestrate_request(
            request_type="get_disruptions",
            payload={"active_only": True},
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Active disruptions retrieved",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/test")
async def test_disruption_agent():
    """Test the disruption management agent functionality"""
    try:
        # Register disruption agent if not already registered
        if "disruption_management_agent" not in agent_manager.agents:
            disruption_agent = DisruptionManagementAgent()
            await agent_manager.register_agent(disruption_agent)
        
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
        
        # Test basic functionality by getting active disruptions
        result = await agent_manager.orchestrate_request(
            request_type="get_disruptions",
            payload={"active_only": True},
            timeout=5.0
        )
        
        return {
            "status": "success",
            "message": "Disruption Management Agent is operational",
            "agent_info": {
                "agent_id": "disruption_management_agent",
                "name": "Disruption Management Agent",
                "running": True
            },
            "test_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent test failed: {str(e)}")