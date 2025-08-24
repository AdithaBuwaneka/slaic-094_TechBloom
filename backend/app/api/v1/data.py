from fastapi import APIRouter
from app.agents.agent_manager import agent_manager
from app.agents.data_aggregation_agent import DataAggregationAgent

router = APIRouter()


@router.post("/transport")
async def get_transport_data():
    """Test Data Aggregation Agent - Get transport data"""
    try:
        # Register data aggregation agent if not already registered
        if "data_aggregation_agent" not in agent_manager.agents:
            data_agent = DataAggregationAgent()
            await agent_manager.register_agent(data_agent)
            
        # Start agents if not running  
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test transport data aggregation
        result = await agent_manager.orchestrate_request(
            request_type="get_transport_data",
            payload={
                "query_id": "test_query_001",
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
                "transport_modes": ["bus", "train"]
            },
            timeout=5.0
        )
        
        return {
            "status": "success",
            "agent_test": "data_aggregation_agent",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "data_aggregation_agent"
        }


@router.post("/validate-sources")  
async def validate_data_sources():
    """Test Data Aggregation Agent - Validate data sources"""
    try:
        # Register data aggregation agent if not already registered
        if "data_aggregation_agent" not in agent_manager.agents:
            data_agent = DataAggregationAgent()
            await agent_manager.register_agent(data_agent)
            
        # Start agents if not running
        if not agent_manager.is_running:
            await agent_manager.start_all_agents()
            
        # Test data source validation
        result = await agent_manager.orchestrate_request(
            request_type="validate_data_sources", 
            payload={},
            timeout=3.0
        )
        
        return {
            "status": "success",
            "agent_test": "data_source_validation",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "agent_test": "data_source_validation"
        }