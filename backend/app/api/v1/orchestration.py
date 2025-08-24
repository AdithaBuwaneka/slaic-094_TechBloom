from fastapi import APIRouter, HTTPException
from app.agents.agent_manager import agent_manager
from app.agents.advanced_orchestrator import AdvancedOrchestrator
from app.models.orchestration import (
    OrchestrationRequest, OrchestrationConfig,
    OrchestrationStrategy, ExecutionMode, ConflictResolutionMethod,
    AgentRole
)
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()

# Global advanced orchestrator instance
advanced_orchestrator = AdvancedOrchestrator()


@router.post("/execute")
async def execute_orchestrated_request(request: OrchestrationRequest):
    """Execute a complex multi-agent request with advanced orchestration"""
    try:
        # Register all current agents with the advanced orchestrator
        for agent_id, agent in agent_manager.agents.items():
            advanced_orchestrator.register_agent(agent)
        
        # Start monitoring if not already started
        await advanced_orchestrator.start_monitoring()
        
        # Execute the orchestrated request
        result = await advanced_orchestrator.orchestrate_request(request)
        
        return {
            "status": "success",
            "message": "Orchestrated request executed successfully",
            "result": result.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


@router.post("/complex-route-planning")
async def complex_route_planning():
    """Demonstrate complex multi-agent route planning with all agents"""
    try:
        # Create a complex request that involves multiple agents
        request = OrchestrationRequest(
            request_type="complex_route_planning",
            payload={
                "origin": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo Fort"
                },
                "destination": {
                    "latitude": 7.2906,
                    "longitude": 80.6337,
                    "address": "Kandy"
                },
                "user_preferences": {
                    "budget_conscious": True,
                    "accessibility_needs": ["wheelchair_access"],
                    "language": "en",
                    "user_type": "tourist"
                },
                "travel_time": "2025-08-22T14:00:00"
            },
            strategy=OrchestrationStrategy.COLLABORATIVE,
            execution_mode=ExecutionMode.SYNCHRONOUS,
            conflict_resolution=ConflictResolutionMethod.WEIGHTED_VOTING,
            timeout_seconds=15.0,
            required_agents=[
                "data_aggregation_agent",
                "route_optimization_agent",
                "fare_optimization_agent",
                "local_knowledge_agent",
                "disruption_management_agent"
            ],
            agent_roles={
                "route_optimization_agent": AgentRole.PRIMARY,
                "data_aggregation_agent": AgentRole.SUPPORTING,
                "fare_optimization_agent": AgentRole.OPTIMIZER,
                "local_knowledge_agent": AgentRole.SUPPORTING,
                "disruption_management_agent": AgentRole.MONITOR
            },
            agent_weights={
                "route_optimization_agent": 1.0,
                "data_aggregation_agent": 0.8,
                "fare_optimization_agent": 0.9,
                "local_knowledge_agent": 0.7,
                "disruption_management_agent": 0.95
            }
        )
        
        # Execute the request
        result = await execute_orchestrated_request(request)
        
        return {
            "status": "success",
            "message": "Complex route planning completed",
            "scenario": "Colombo Fort to Kandy with tourist preferences",
            "agents_involved": len(request.required_agents),
            "orchestration_strategy": request.strategy.value,
            "result": result["result"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complex route planning failed: {str(e)}")


@router.get("/system-status")
async def get_orchestration_system_status():
    """Get comprehensive system status including orchestration metrics"""
    try:
        # Get basic agent manager status
        basic_status = agent_manager.get_system_status()
        
        # Get advanced orchestration status
        advanced_status = advanced_orchestrator.get_system_status()
        
        return {
            "status": "success",
            "message": "System status retrieved",
            "timestamp": datetime.utcnow().isoformat(),
            "basic_orchestration": basic_status,
            "advanced_orchestration": advanced_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.get("/performance-metrics")
async def get_performance_metrics():
    """Get detailed performance metrics and analytics"""
    try:
        status = advanced_orchestrator.get_system_status()
        
        return {
            "status": "success",
            "message": "Performance metrics retrieved",
            "metrics": status["performance_metrics"],
            "request_history_size": status["request_history_size"],
            "optimization_status": {
                "monitoring_active": status["orchestrator_status"] == "active",
                "active_requests": status["active_requests"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/optimization-recommendations/{request_type}")
async def get_optimization_recommendations(request_type: str):
    """Get optimization recommendations for a specific request type"""
    try:
        recommendations = advanced_orchestrator.get_optimization_recommendations(request_type)
        
        return {
            "status": "success",
            "message": f"Optimization recommendations for {request_type}",
            "request_type": request_type,
            "recommendations": [rec.model_dump() for rec in recommendations],
            "recommendations_count": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/strategy-comparison")
async def compare_orchestration_strategies():
    """Compare different orchestration strategies with the same request"""
    try:
        base_payload = {
            "origin": {
                "latitude": 6.9271,
                "longitude": 79.8612,
                "address": "Colombo"
            },
            "destination": {
                "latitude": 7.2906,
                "longitude": 80.6337,
                "address": "Kandy"
            }
        }
        
        strategies_to_test = [
            OrchestrationStrategy.PARALLEL,
            OrchestrationStrategy.SEQUENTIAL,
            OrchestrationStrategy.PRIORITY_BASED
        ]
        
        results = {}
        
        for strategy in strategies_to_test:
            request = OrchestrationRequest(
                request_type="route_optimization_comparison",
                payload=base_payload,
                strategy=strategy,
                execution_mode=ExecutionMode.SYNCHRONOUS,
                timeout_seconds=10.0
            )
            
            # Register agents
            for agent_id, agent in agent_manager.agents.items():
                advanced_orchestrator.register_agent(agent)
            
            # Execute
            result = await advanced_orchestrator.orchestrate_request(request)
            
            results[strategy.value] = {
                "success": result.success,
                "processing_time": result.total_processing_time,
                "quality_score": result.quality_score,
                "confidence_score": result.confidence_score,
                "successful_agents": result.successful_agents,
                "failed_agents": result.failed_agents
            }
        
        return {
            "status": "success",
            "message": "Strategy comparison completed",
            "comparison_results": results,
            "best_strategy": min(results.keys(), 
                               key=lambda k: results[k]["processing_time"]) if results else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy comparison failed: {str(e)}")


@router.post("/agent-collaboration-test")
async def test_agent_collaboration():
    """Test collaborative agent interaction for complex scenarios"""
    try:
        # Create a complex collaborative request
        request = OrchestrationRequest(
            request_type="collaborative_planning",
            payload={
                "scenario": "Tourist visiting multiple locations with constraints",
                "user_profile": {
                    "type": "tourist",
                    "budget": "moderate",
                    "interests": ["culture", "food", "shopping"],
                    "accessibility_needs": [],
                    "language": "en"
                },
                "itinerary": [
                    {
                        "location": {"latitude": 6.9271, "longitude": 79.8612, "address": "Colombo"},
                        "duration_hours": 4
                    },
                    {
                        "location": {"latitude": 7.2906, "longitude": 80.6337, "address": "Kandy"},
                        "duration_hours": 8
                    },
                    {
                        "location": {"latitude": 6.0535, "longitude": 80.2210, "address": "Galle"},
                        "duration_hours": 6
                    }
                ],
                "constraints": {
                    "total_budget": 15000,
                    "max_travel_time_per_leg": 4,
                    "preferred_transport_modes": ["train", "bus"]
                }
            },
            strategy=OrchestrationStrategy.COLLABORATIVE,
            execution_mode=ExecutionMode.SYNCHRONOUS,
            conflict_resolution=ConflictResolutionMethod.CONSENSUS_BASED,
            timeout_seconds=20.0,
            agent_roles={
                "route_optimization_agent": AgentRole.PRIMARY,
                "fare_optimization_agent": AgentRole.OPTIMIZER,
                "local_knowledge_agent": AgentRole.SUPPORTING,
                "disruption_management_agent": AgentRole.VALIDATOR
            }
        )
        
        # Register agents and execute
        for agent_id, agent in agent_manager.agents.items():
            advanced_orchestrator.register_agent(agent)
        
        result = await advanced_orchestrator.orchestrate_request(request)
        
        return {
            "status": "success",
            "message": "Agent collaboration test completed",
            "test_scenario": "Multi-location tourist itinerary planning",
            "collaboration_strategy": request.strategy.value,
            "agents_participated": len([r for r in result.agent_results if r.success]),
            "overall_success": result.success,
            "quality_metrics": {
                "quality_score": result.quality_score,
                "confidence_score": result.confidence_score,
                "consensus_achieved": getattr(result, 'consensus_achieved', False)
            },
            "result": result.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collaboration test failed: {str(e)}")


@router.post("/update-config")
async def update_orchestration_config(config: OrchestrationConfig):
    """Update orchestration configuration"""
    try:
        # Create new orchestrator with updated config
        global advanced_orchestrator
        
        # Stop current monitoring
        await advanced_orchestrator.stop_monitoring()
        
        # Create new orchestrator with new config
        advanced_orchestrator = AdvancedOrchestrator(config)
        
        # Re-register agents
        for agent_id, agent in agent_manager.agents.items():
            advanced_orchestrator.register_agent(agent)
        
        # Start monitoring
        await advanced_orchestrator.start_monitoring()
        
        return {
            "status": "success",
            "message": "Orchestration configuration updated successfully",
            "new_config": config.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@router.get("/test")
async def test_advanced_orchestration():
    """Test advanced orchestration functionality"""
    try:
        # Register all available agents
        for agent_id, agent in agent_manager.agents.items():
            advanced_orchestrator.register_agent(agent)
        
        # Start monitoring
        await advanced_orchestrator.start_monitoring()
        
        # Create a simple test request
        test_request = OrchestrationRequest(
            request_type="orchestration_test",
            payload={
                "test_data": "advanced_orchestration_test",
                "location": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Colombo"
                }
            },
            strategy=OrchestrationStrategy.PARALLEL,
            execution_mode=ExecutionMode.SYNCHRONOUS,
            timeout_seconds=8.0
        )
        
        # Execute test
        result = await advanced_orchestrator.orchestrate_request(test_request)
        
        return {
            "status": "success",
            "message": "Advanced Orchestration System is operational",
            "system_info": {
                "orchestrator_active": True,
                "monitoring_enabled": True,
                "registered_agents": len(advanced_orchestrator.agents),
                "available_strategies": [s.value for s in OrchestrationStrategy],
                "available_execution_modes": [m.value for m in ExecutionMode],
                "conflict_resolution_methods": [c.value for c in ConflictResolutionMethod]
            },
            "test_result": {
                "request_id": result.request_id,
                "success": result.success,
                "processing_time": result.total_processing_time,
                "quality_score": result.quality_score,
                "agents_executed": len(result.agent_results),
                "successful_agents": result.successful_agents
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration test failed: {str(e)}")