from fastapi import APIRouter
from app.agents.agent_manager import agent_manager
from app.agents.language_accessibility_agent import LanguageAccessibilityAgent

router = APIRouter()


@router.post("/profile")
async def create_accessibility_profile():
    """Test Language & Accessibility Agent - Create accessibility profile"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test accessibility profile creation
        result = await agent_manager.orchestrate_request(
            request_type="create_accessibility_profile",
            payload={
                "user_id": "accessibility_user_001",
                "primary_language": "english",
                "accessibility_needs": ["wheelchair", "visual_impairment"],
                "disability_types": ["mobility", "visual"],
                "uses_wheelchair": True,
                "prefers_audio_announcements": True,
                "needs_visual_alerts": False,
                "requires_boarding_assistance": True,
                "requires_navigation_assistance": True,
                "needs_simplified_instructions": False
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "create_accessibility_profile",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "create_accessibility_profile"
        }


@router.post("/info")
async def get_accessibility_info():
    """Test Language & Accessibility Agent - Get transport accessibility information"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test accessibility info retrieval
        result = await agent_manager.orchestrate_request(
            request_type="get_accessibility_info",
            payload={
                "operator": "Sri Lanka Railways",
                "transport_mode": "train"
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "get_accessibility_info",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "get_accessibility_info"
        }


@router.post("/assess")
async def assess_route_accessibility():
    """Test Language & Accessibility Agent - Assess route accessibility"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test route accessibility assessment
        result = await agent_manager.orchestrate_request(
            request_type="assess_accessibility",
            payload={
                "route_id": "colombo_kandy_accessible_001",
                "user_id": "accessibility_user_001",
                "accessibility_needs": ["wheelchair", "mobility_assistance"],
                "operators": ["SLTB", "Sri Lanka Railways"]
            },
            timeout=5.0
        )
        
        return {
            "status": "success",
            "agent_test": "assess_route_accessibility",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "assess_route_accessibility"
        }


@router.post("/alerts")
async def get_accessibility_alerts():
    """Test Language & Accessibility Agent - Get accessibility alerts"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test accessibility alerts
        result = await agent_manager.orchestrate_request(
            request_type="get_accessibility_alerts",
            payload={
                "transport_mode": "train",
                "location": "Colombo Fort"
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "get_accessibility_alerts",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "get_accessibility_alerts"
        }


@router.post("/emergency-info")
async def get_emergency_accessibility_info():
    """Test Language & Accessibility Agent - Get emergency accessibility information"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test emergency accessibility info
        result = await agent_manager.orchestrate_request(
            request_type="get_emergency_info",
            payload={
                "transport_mode": "train",
                "language": "english"
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "get_emergency_accessibility_info",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "get_emergency_accessibility_info"
        }


@router.post("/feedback")
async def submit_accessibility_feedback():
    """Test Language & Accessibility Agent - Submit accessibility feedback"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test feedback submission
        result = await agent_manager.orchestrate_request(
            request_type="submit_accessibility_feedback",
            payload={
                "user_id": "accessibility_user_001",
                "transport_mode": "bus",
                "operator": "SLTB",
                "route_id": "138",
                "accessibility_rating": 4,
                "specific_ratings": {
                    "boarding": 4,
                    "navigation": 3,
                    "communication": 5
                },
                "accessibility_features_used": ["wheelchair", "visual_impairment"],
                "positive_experiences": ["Staff very helpful", "Audio announcements clear"],
                "issues_encountered": ["Platform slightly too high"],
                "suggested_improvements": ["Lower platform height", "Better wheelchair ramps"],
                "trip_date": "2025-08-22T09:00:00",
                "time_of_day": "morning",
                "crowd_level": "heavy",
                "feedback_text": "Overall good experience but platform accessibility could be improved"
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "submit_accessibility_feedback",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "submit_accessibility_feedback"
        }