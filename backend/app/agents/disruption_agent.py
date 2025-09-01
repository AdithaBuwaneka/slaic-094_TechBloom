from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.database import db
from app.models.transport import Disruption, TransportMode, ServiceStatus
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class DisruptionAnalysis(BaseModel):
    """Analysis of current disruptions and their impact."""
    severity_level: str = Field(description="Overall disruption severity: low, medium, high, critical")
    affected_routes: List[str] = Field(description="List of route IDs affected")
    recommended_alternatives: List[str] = Field(description="Alternative route suggestions")
    estimated_delay: int = Field(description="Estimated delay in minutes")
    user_message: str = Field(description="User-friendly message about the disruption")

class DisruptionManagementAgent:
    """
    Agent responsible for detecting delays, service interruptions, and dynamically 
    rerouting users based on real-time disruptions.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        prompt_template = """You are a transportation disruption management expert for Sri Lanka's public transport system.
        
        Analyze the following disruption data and provide recommendations:
        
        Current Disruptions:
        {disruptions_data}
        
        Route Information:
        {route_info}
        
        User Journey:
        Origin: {origin}
        Destination: {destination}
        Preferred Transport: {transport_mode}
        
        Provide analysis including:
        1. Overall severity assessment
        2. Which routes are affected
        3. Alternative routes to recommend
        4. Estimated additional delay
        5. Clear message for the user
        
        Consider Sri Lankan context: monsoon delays, traffic conditions, strike actions, and infrastructure limitations.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        self.structured_llm = prompt | self.llm.with_structured_output(DisruptionAnalysis)
    
    async def check_disruptions(self, origin: str, destination: str, transport_mode: str = "any") -> DisruptionAnalysis:
        """
        Check for current disruptions affecting a specific journey.
        """
        try:
            # Get active disruptions from database
            current_time = datetime.utcnow()
            disruptions_cursor = db.disruptions_collection.find({
                "start_time": {"$lte": current_time},
                "$or": [
                    {"end_time": {"$gte": current_time}},
                    {"end_time": None}
                ]
            })
            
            disruptions = await disruptions_cursor.to_list(length=50)
            
            # Format disruption data for AI analysis
            disruptions_data = []
            for disruption in disruptions:
                disruptions_data.append({
                    "title": disruption.get("title", "Unknown disruption"),
                    "description": disruption.get("description", ""),
                    "severity": disruption.get("severity", "medium"),
                    "transport_mode": disruption.get("transport_mode", ""),
                    "affected_stops": disruption.get("affected_stops", []),
                    "route_id": disruption.get("route_id", ""),
                    "start_time": disruption.get("start_time", "").isoformat() if disruption.get("start_time") else ""
                })
            
            # Get relevant route information
            route_info = await self._get_relevant_routes(origin, destination, transport_mode)
            
            # Analyze with AI
            analysis = await self.structured_llm.ainvoke({
                "disruptions_data": disruptions_data,
                "route_info": route_info,
                "origin": origin,
                "destination": destination,
                "transport_mode": transport_mode
            })
            
            return analysis
            
        except Exception as e:
            print(f"Error in disruption analysis: {e}")
            return DisruptionAnalysis(
                severity_level="low",
                affected_routes=[],
                recommended_alternatives=[],
                estimated_delay=0,
                user_message="Unable to check for disruptions at the moment. Please proceed with caution."
            )
    
    async def create_disruption_alert(self, disruption_data: Dict[str, Any]) -> bool:
        """
        Create a new disruption alert in the system.
        """
        try:
            disruption = Disruption(
                transport_mode=TransportMode(disruption_data.get("transport_mode", "bus")),
                route_id=disruption_data.get("route_id", ""),
                title=disruption_data.get("title", "Service disruption"),
                description=disruption_data.get("description", ""),
                severity=disruption_data.get("severity", "medium"),
                start_time=disruption_data.get("start_time", datetime.utcnow()),
                end_time=disruption_data.get("end_time"),
                affected_stops=disruption_data.get("affected_stops", []),
                alternative_routes=disruption_data.get("alternative_routes", []),
                source=disruption_data.get("source", "automatic")
            )
            
            result = await db.disruptions_collection.insert_one(disruption.dict(exclude={"id"}))
            return result.inserted_id is not None
            
        except Exception as e:
            print(f"Error creating disruption alert: {e}")
            return False
    
    async def get_alternative_routes(self, original_route_id: str, origin: str, destination: str) -> List[str]:
        """
        Find alternative routes when the original route is disrupted.
        """
        try:
            # Query database for alternative routes
            alternatives = []
            
            # Search bus routes
            bus_routes = db.bus_routes_collection.find({
                "origin": {"$regex": origin, "$options": "i"},
                "destination": {"$regex": destination, "$options": "i"},
                "status": ServiceStatus.ACTIVE.value,
                "route_number": {"$ne": original_route_id}
            })
            
            async for route in bus_routes:
                alternatives.append(f"Bus Route {route.get('route_number', 'Unknown')}")
            
            # Search train routes
            train_routes = db.train_routes_collection.find({
                "origin": {"$regex": origin, "$options": "i"},
                "destination": {"$regex": destination, "$options": "i"},
                "status": ServiceStatus.ACTIVE.value
            })
            
            async for route in train_routes:
                alternatives.append(f"Train {route.get('route_name', 'Unknown')}")
            
            return alternatives[:5]  # Return top 5 alternatives
            
        except Exception as e:
            print(f"Error finding alternative routes: {e}")
            return []
    
    async def _get_relevant_routes(self, origin: str, destination: str, transport_mode: str) -> List[Dict]:
        """
        Get routes relevant to the user's journey for analysis.
        """
        try:
            routes = []
            
            if transport_mode in ["any", "bus"]:
                bus_cursor = db.bus_routes_collection.find({
                    "origin": {"$regex": origin, "$options": "i"},
                    "destination": {"$regex": destination, "$options": "i"}
                }).limit(10)
                
                async for route in bus_cursor:
                    routes.append({
                        "type": "bus",
                        "route_id": route.get("route_number", ""),
                        "name": f"Bus {route.get('route_number', '')} - {route.get('route_name', '')}",
                        "operator": route.get("operator", ""),
                        "status": route.get("status", "")
                    })
            
            if transport_mode in ["any", "train"]:
                train_cursor = db.train_routes_collection.find({
                    "origin": {"$regex": origin, "$options": "i"},
                    "destination": {"$regex": destination, "$options": "i"}
                }).limit(5)
                
                async for route in train_cursor:
                    routes.append({
                        "type": "train", 
                        "route_id": route.get("route_number", ""),
                        "name": route.get("route_name", ""),
                        "line": route.get("line", ""),
                        "status": route.get("status", "")
                    })
            
            return routes
            
        except Exception as e:
            print(f"Error getting relevant routes: {e}")
            return []