from fastapi import APIRouter
from app.agents.agent_manager import agent_manager
from app.agents.route_optimization_agent import RouteOptimizationAgent

router = APIRouter()


@router.post("/optimize")
async def optimize_route():
    """Test Route Optimization Agent - Find optimized route"""
    try:
        # Register route optimization agent if not already registered
        if "route_optimization_agent" not in agent_manager.agents:
            route_agent = RouteOptimizationAgent()
            await agent_manager.register_agent(route_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test route optimization
        result = await agent_manager.orchestrate_request(
            request_type="optimize_route",
            payload={
                "origin": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo Fort Railway Station",
                    "district": "Colombo"
                },
                "destination": {
                    "latitude": 7.2906,
                    "longitude": 80.6337,
                    "address": "Kandy Railway Station", 
                    "district": "Kandy"
                },
                "preferred_modes": ["bus", "train"],
                "optimization_criteria": ["time", "cost"],
                "criteria_weights": {"time": 0.6, "cost": 0.4},
                "max_transfers": 2,
                "budget_limit": 200.0
            },
            timeout=5.0
        )
        
        return {
            "status": "success",
            "agent_test": "route_optimization",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed", 
            "error": str(e),
            "agent_test": "route_optimization"
        }


@router.post("/alternatives")
async def find_route_alternatives():
    """Test Route Optimization Agent - Find alternative routes"""
    try:
        # Register route optimization agent if not already registered
        if "route_optimization_agent" not in agent_manager.agents:
            route_agent = RouteOptimizationAgent()
            await agent_manager.register_agent(route_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test alternative route finding
        result = await agent_manager.orchestrate_request(
            request_type="find_alternatives",
            payload={
                "origin": {
                    "latitude": 6.0329,
                    "longitude": 80.2168,
                    "address": "Galle Bus Stand", 
                    "district": "Galle"
                },
                "destination": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo Fort",
                    "district": "Colombo"
                },
                "preferred_modes": ["bus", "train", "taxi"],
                "max_transfers": 3
            },
            timeout=5.0
        )
        
        return {
            "status": "success",
            "agent_test": "route_alternatives", 
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "route_alternatives"
        }


@router.post("/feasibility")
async def analyze_route_feasibility():
    """Test Route Optimization Agent - Analyze route feasibility"""
    try:
        # Register route optimization agent if not already registered
        if "route_optimization_agent" not in agent_manager.agents:
            route_agent = RouteOptimizationAgent()
            await agent_manager.register_agent(route_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test feasibility analysis
        result = await agent_manager.orchestrate_request(
            request_type="analyze_feasibility",
            payload={
                "origin": {
                    "latitude": 7.8731,
                    "longitude": 80.7718,
                    "address": "Anuradhapura",
                    "district": "Anuradhapura"
                },
                "destination": {
                    "latitude": 9.6615,
                    "longitude": 80.0255,
                    "address": "Jaffna",
                    "district": "Jaffna"
                },
                "preferred_modes": ["bus", "train"],
                "max_journey_time_minutes": 300,
                "budget_limit": 150.0
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "route_feasibility",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "route_feasibility"
        }