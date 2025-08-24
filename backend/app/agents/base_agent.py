from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import asyncio
import uuid
import json


class AgentMessage(BaseModel):
    id: str
    sender_id: str
    receiver_id: Optional[str] = None
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1-10, 1 = highest priority


class AgentResponse(BaseModel):
    agent_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float
    timestamp: datetime


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, priority_weight: float = 1.0):
        self.agent_id = agent_id
        self.name = name
        self.priority_weight = priority_weight
        self.is_active = False
        self.message_queue = asyncio.Queue()
        self.response_handlers = {}
        
    async def start(self):
        """Start the agent"""
        self.is_active = True
        asyncio.create_task(self._message_processor())
        await self.on_start()
        
    async def stop(self):
        """Stop the agent"""
        self.is_active = False
        await self.on_stop()
        
    async def on_start(self):
        """Called when agent starts - override in subclasses"""
        pass
        
    async def on_stop(self):
        """Called when agent stops - override in subclasses"""
        pass
        
    async def _message_processor(self):
        """Internal message processing loop"""
        while self.is_active:
            try:
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._handle_message(message)
                await asyncio.sleep(0.1)  # Prevent busy waiting
            except Exception as e:
                print(f"Error in {self.name} message processor: {e}")
                
    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        try:
            start_time = datetime.utcnow()
            
            # Process the message based on type
            if message.message_type == "process_request":
                result = await self.process_request(message.payload)
            else:
                result = await self.handle_custom_message(message)
                
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Create response
            response = AgentResponse(
                agent_id=self.agent_id,
                success=True,
                data=result,
                processing_time=processing_time,
                timestamp=end_time
            )
            
            # Send response back if there's a response handler
            if message.id in self.response_handlers:
                await self.response_handlers[message.id](response)
                del self.response_handlers[message.id]
                
        except Exception as e:
            error_response = AgentResponse(
                agent_id=self.agent_id,
                success=False,
                data={},
                error=str(e),
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
            
            if message.id in self.response_handlers:
                await self.response_handlers[message.id](error_response)
                del self.response_handlers[message.id]
                
    async def send_message(self, message: AgentMessage, response_handler=None):
        """Send message to another agent"""
        if response_handler:
            self.response_handlers[message.id] = response_handler
        await self.message_queue.put(message)
        
    async def broadcast_message(self, message_type: str, payload: Dict[str, Any], priority: int = 5):
        """Broadcast message to all agents"""
        message = AgentMessage(
            id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow(),
            priority=priority
        )
        
        # This will be handled by the AgentManager
        from app.agents.agent_manager import agent_manager
        await agent_manager.broadcast_message(message)
        
    @abstractmethod
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method - must be implemented by subclasses"""
        pass
        
    async def handle_custom_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle custom message types - override in subclasses"""
        return {"status": "message_not_handled", "message_type": message.message_type}
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_active": self.is_active,
            "priority_weight": self.priority_weight,
            "queue_size": self.message_queue.qsize()
        }