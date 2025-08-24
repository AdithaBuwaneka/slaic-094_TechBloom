from fastapi import APIRouter
from app.agents.agent_manager import agent_manager

router = APIRouter()


@router.get("/status")
async def agents_status():
    """Get status of all agents"""
    return agent_manager.get_system_status()


@router.post("/test")
async def test_agent_framework():
    """Test the agent framework"""
    try:
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test basic agent functionality
        return {
            "test_status": "success",
            "framework_working": True,
            "message": "Agent framework operational",
            "system_status": agent_manager.get_system_status()
        }
        
    except Exception as e:
        return {
            "test_status": "failed",
            "framework_working": False,
            "error": str(e),
            "system_status": agent_manager.get_system_status()
        }