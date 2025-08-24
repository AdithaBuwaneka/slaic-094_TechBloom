from fastapi import APIRouter
from app.agents.agent_manager import agent_manager
from app.agents.fare_optimization_agent import FareOptimizationAgent

router = APIRouter()


@router.post("/calculate")
async def calculate_fare():
    """Test Fare Optimization Agent - Calculate detailed fare"""
    try:
        # Register fare optimization agent if not already registered
        if "fare_optimization_agent" not in agent_manager.agents:
            fare_agent = FareOptimizationAgent()
            await agent_manager.register_agent(fare_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test fare calculation
        result = await agent_manager.orchestrate_request(
            request_type="calculate_fare",
            payload={
                "route_id": "colombo_kandy_001",
                "transport_mode": "train",
                "operator": "Sri Lanka Railways",
                "distance_km": 115.0,
                "departure_time": "2025-08-22T08:00:00",
                "origin": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo Fort Railway Station"
                },
                "destination": {
                    "latitude": 7.2906,
                    "longitude": 80.6337,
                    "address": "Kandy Railway Station"
                }
            },
            timeout=5.0
        )
        
        return {
            "status": "success",
            "agent_test": "calculate_fare",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "calculate_fare"
        }


@router.post("/optimize")
async def optimize_fare():
    """Test Fare Optimization Agent - Find cheapest options"""
    try:
        # Register fare optimization agent if not already registered
        if "fare_optimization_agent" not in agent_manager.agents:
            fare_agent = FareOptimizationAgent()
            await agent_manager.register_agent(fare_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test fare optimization
        result = await agent_manager.orchestrate_request(
            request_type="optimize_fare",
            payload={
                "user_id": "user_001",
                "origin": {
                    "latitude": 6.0329,
                    "longitude": 80.2168,
                    "address": "Galle"
                },
                "destination": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo"
                },
                "travel_date": "2025-08-22T14:00:00",
                "group_size": 1,
                "user_profile": {
                    "age": 22,
                    "student": True,
                    "monthly_trips": 25
                }
            },
            timeout=5.0
        )
        
        return {
            "status": "success",
            "agent_test": "optimize_fare",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "optimize_fare"
        }


@router.post("/discounts")
async def find_discounts():
    """Test Fare Optimization Agent - Find applicable discounts"""
    try:
        # Register fare optimization agent if not already registered
        if "fare_optimization_agent" not in agent_manager.agents:
            fare_agent = FareOptimizationAgent()
            await agent_manager.register_agent(fare_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test discount finding
        result = await agent_manager.orchestrate_request(
            request_type="find_discounts",
            payload={
                "user_profile": {
                    "age": 65,
                    "student": False,
                    "documents": ["national_id"]
                },
                "travel_date": "2025-08-22T10:00:00",
                "group_size": 12,
                "transport_modes": ["bus", "train"]
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "find_discounts",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "find_discounts"
        }


@router.post("/season-passes")
async def analyze_season_passes():
    """Test Fare Optimization Agent - Analyze season pass options"""
    try:
        # Register fare optimization agent if not already registered
        if "fare_optimization_agent" not in agent_manager.agents:
            fare_agent = FareOptimizationAgent()
            await agent_manager.register_agent(fare_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test season pass analysis
        result = await agent_manager.orchestrate_request(
            request_type="analyze_season_passes",
            payload={
                "user_profile": {
                    "occupation": "daily_commuter",
                    "home_location": "Colombo",
                    "work_location": "Kandy"
                },
                "estimated_monthly_trips": 45,
                "typical_trip_cost": 75.0
            },
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "analyze_season_passes",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "analyze_season_passes"
        }