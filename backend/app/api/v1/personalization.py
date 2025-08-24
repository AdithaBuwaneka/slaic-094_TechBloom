from fastapi import APIRouter
from app.agents.agent_manager import agent_manager
from app.agents.personalization_agent import PersonalizationAgent

router = APIRouter()


@router.post("/create-profile")
async def create_user_profile():
    """Test Personalization Agent - Create user profile"""
    try:
        # Register personalization agent if not already registered
        if "personalization_agent" not in agent_manager.agents:
            personalization_agent = PersonalizationAgent()
            await agent_manager.register_agent(personalization_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test user profile creation
        result = await agent_manager.orchestrate_request(
            request_type="create_user_profile",
            payload={
                "user_id": "user_001",
                "name": "Nimal Silva",
                "age_group": "26-35",
                "occupation": "Software Engineer",
                "home_location": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo 01",
                    "district": "Colombo"
                },
                "work_location": {
                    "latitude": 6.9319,
                    "longitude": 79.8478,
                    "address": "Colombo 03", 
                    "district": "Colombo"
                },
                "preferred_modes": ["train", "bus"],
                "budget_sensitivity": "moderate",
                "comfort_preference": "standard",
                "time_flexibility": "moderate",
                "max_walking_distance_meters": 800
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "create_user_profile",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "create_user_profile"
        }


@router.post("/get-preferences")
async def get_user_preferences():
    """Test Personalization Agent - Get contextual preferences"""
    try:
        # Register personalization agent if not already registered
        if "personalization_agent" not in agent_manager.agents:
            personalization_agent = PersonalizationAgent()
            await agent_manager.register_agent(personalization_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test getting user preferences with context
        result = await agent_manager.orchestrate_request(
            request_type="get_user_preferences",
            payload={
                "user_id": "user_001",
                "context": {
                    "weather_condition": "rainy",
                    "time_of_day": "rush_hour",
                    "purpose": "business",
                    "with_luggage": True,
                    "group_size": 1
                }
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "get_user_preferences",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "get_user_preferences"
        }


@router.post("/generate-recommendations")
async def generate_personalized_recommendations():
    """Test Personalization Agent - Generate personalized route recommendations"""
    try:
        # Register personalization agent if not already registered
        if "personalization_agent" not in agent_manager.agents:
            personalization_agent = PersonalizationAgent()
            await agent_manager.register_agent(personalization_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Mock route data for personalization
        mock_routes = [
            {
                "route_id": "route_001",
                "overall_score": 0.75,
                "time_score": 0.8,
                "cost_score": 0.6,
                "comfort_score": 0.7,
                "reliability_score": 0.9,
                "total_cost": 120.0,
                "segments": [{"transport_mode": "train"}]
            },
            {
                "route_id": "route_002", 
                "overall_score": 0.65,
                "time_score": 0.6,
                "cost_score": 0.9,
                "comfort_score": 0.5,
                "reliability_score": 0.7,
                "total_cost": 80.0,
                "segments": [{"transport_mode": "bus"}]
            },
            {
                "route_id": "route_003",
                "overall_score": 0.55,
                "time_score": 0.4,
                "cost_score": 1.0,
                "comfort_score": 0.3,
                "reliability_score": 1.0,
                "total_cost": 0.0,
                "segments": [{"transport_mode": "walking"}]
            }
        ]
        
        # Test personalized recommendation generation
        result = await agent_manager.orchestrate_request(
            request_type="generate_personalized_recommendations",
            payload={
                "user_id": "user_001",
                "routes": mock_routes,
                "context": {
                    "weather_condition": "sunny",
                    "purpose": "commute",
                    "time_of_day": "morning",
                    "with_luggage": False
                }
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "generate_personalized_recommendations",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "generate_personalized_recommendations"
        }