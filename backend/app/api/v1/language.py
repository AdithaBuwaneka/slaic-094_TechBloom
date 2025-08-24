from fastapi import APIRouter
from app.agents.agent_manager import agent_manager
from app.agents.language_accessibility_agent import LanguageAccessibilityAgent

router = APIRouter()


@router.post("/translate")
async def translate_text():
    """Test Language & Accessibility Agent - Translate text"""
    try:
        # Register language accessibility agent if not already registered
        if "language_accessibility_agent" not in agent_manager.agents:
            accessibility_agent = LanguageAccessibilityAgent()
            await agent_manager.register_agent(accessibility_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test text translation
        result = await agent_manager.orchestrate_request(
            request_type="translate_text",
            payload={
                "text": "Welcome to Sri Lankan Transit Companion",
                "from_language": "english",
                "to_language": "sinhala",
                "context": "general"
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "translate_text",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "translate_text"
        }