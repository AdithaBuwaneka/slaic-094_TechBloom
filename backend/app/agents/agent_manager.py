from typing import Dict, List, Optional, Any
from app.agents.base_agent import BaseAgent, AgentMessage, AgentResponse
import asyncio
from datetime import datetime
import json


class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.is_running = False
        
        # Conflict resolution priority matrix (from project specs)
        self.priority_matrix = {
            "safety": 1.0,
            "user_preferences": 0.8,
            "time_efficiency": 0.7,
            "cost_optimization": 0.6,
            "local_knowledge": 0.5
        }
        
    async def register_agent(self, agent: BaseAgent):
        """Register an agent with the manager"""
        self.agents[agent.agent_id] = agent
        if self.is_running:
            await agent.start()
            
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            await self.agents[agent_id].stop()
            del self.agents[agent_id]
            
    async def start_all_agents(self):
        """Start all registered agents"""
        self.is_running = True
        for agent in self.agents.values():
            await agent.start()
            
    async def stop_all_agents(self):
        """Stop all registered agents"""
        self.is_running = False
        for agent in self.agents.values():
            await agent.stop()
            
    async def broadcast_message(self, message: AgentMessage):
        """Broadcast message to all agents except sender"""
        for agent_id, agent in self.agents.items():
            if agent_id != message.sender_id and agent.is_active:
                await agent.send_message(message)
                
    async def send_message_to_agent(self, agent_id: str, message: AgentMessage):
        """Send message to specific agent"""
        if agent_id in self.agents and self.agents[agent_id].is_active:
            await self.agents[agent_id].send_message(message)
            
    async def orchestrate_request(self, request_type: str, payload: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
        """Orchestrate a request across multiple agents with conflict resolution"""
        
        # Create orchestration message
        message = AgentMessage(
            id=f"orchestration_{datetime.utcnow().isoformat()}",
            sender_id="agent_manager",
            message_type="process_request",
            payload={
                "request_type": request_type,
                "data": payload
            },
            timestamp=datetime.utcnow(),
            priority=3
        )
        
        # Collect responses from all agents
        responses = {}
        response_futures = {}
        
        # Send to all active agents
        for agent_id, agent in self.agents.items():
            if agent.is_active:
                future = asyncio.Future()
                response_futures[agent_id] = future
                
                # Create response handler
                async def response_handler(response: AgentResponse, aid=agent_id):
                    if aid in response_futures and not response_futures[aid].done():
                        response_futures[aid].set_result(response)
                
                # Send message with response handler
                await agent.send_message(message, response_handler)
        
        # Wait for responses with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*response_futures.values(), return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"Timeout waiting for agent responses after {timeout}s")
            
        # Collect completed responses
        for agent_id, future in response_futures.items():
            if future.done() and not future.exception():
                responses[agent_id] = future.result()
                
        # Apply conflict resolution
        resolved_response = await self._resolve_conflicts(responses, request_type)
        
        return resolved_response
        
    async def _resolve_conflicts(self, responses: Dict[str, AgentResponse], request_type: str) -> Dict[str, Any]:
        """Resolve conflicts between agent responses using weighted voting"""
        
        if not responses:
            return {"status": "no_responses", "data": {}}
            
        # Separate successful and failed responses
        successful_responses = {k: v for k, v in responses.items() if v.success}
        failed_responses = {k: v for k, v in responses.items() if not v.success}
        
        if not successful_responses:
            return {
                "status": "all_failed",
                "errors": {k: v.error for k, v in failed_responses.items()}
            }
            
        # For now, implement simple weighted averaging
        # In a full implementation, this would be more sophisticated
        total_weight = 0
        weighted_data = {}
        
        for agent_id, response in successful_responses.items():
            agent = self.agents[agent_id]
            weight = agent.priority_weight
            total_weight += weight
            
            # Merge response data with weights
            for key, value in response.data.items():
                if key not in weighted_data:
                    weighted_data[key] = []
                weighted_data[key].append({
                    "value": value,
                    "weight": weight,
                    "agent_id": agent_id
                })
        
        # Create resolved response
        resolved_data = {}
        for key, values in weighted_data.items():
            if len(values) == 1:
                resolved_data[key] = values[0]["value"]
            else:
                # Use the value from the highest weighted agent
                best_value = max(values, key=lambda x: x["weight"])
                resolved_data[key] = best_value["value"]
                
        return {
            "status": "success",
            "data": resolved_data,
            "agent_responses": len(successful_responses),
            "failed_responses": len(failed_responses),
            "response_details": {k: {"success": v.success, "processing_time": v.processing_time} for k, v in responses.items()}
        }
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "is_running": self.is_running,
            "total_agents": len(self.agents),
            "active_agents": sum(1 for agent in self.agents.values() if agent.is_active),
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()}
        }


# Global agent manager instance
agent_manager = AgentManager()