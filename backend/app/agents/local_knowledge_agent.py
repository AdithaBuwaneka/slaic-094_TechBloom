from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.database import db
from app.models.transport import CommunityUpdate, TransportMode, Location
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class LocalInsights(BaseModel):
    """Local knowledge and community insights about transport routes."""
    local_tips: List[str] = Field(description="Local tips and recommendations")
    community_alerts: List[str] = Field(description="Recent community-reported issues or updates")
    cultural_context: str = Field(description="Cultural context and local customs relevant to the route")
    hidden_routes: List[str] = Field(description="Lesser-known or informal transport options")
    seasonal_considerations: str = Field(description="Seasonal factors affecting this route")
    local_landmarks: List[str] = Field(description="Key landmarks and reference points")
    safety_notes: str = Field(description="Local safety considerations and advice")

class LocalKnowledgeAgent:
    """
    Agent that supplements official data with community-contributed updates,
    especially for rural and semi-urban areas where official data may be limited.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,  # Slightly higher for more diverse local knowledge
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        prompt_template = """You are a local transport knowledge expert for Sri Lanka with deep understanding of community-based transport information.
        
        Provide local insights for this journey based on community knowledge:
        
        Journey: {origin} to {destination}
        Transport Mode: {transport_mode}
        Time of Travel: {travel_time}
        
        Community Updates:
        {community_updates}
        
        Local Route Data:
        {local_routes}
        
        Consider:
        1. Rural and semi-urban transport patterns
        2. Informal transport options (three-wheelers, shared taxis, private buses)
        3. Local customs and etiquette
        4. Seasonal variations (monsoon, festival seasons)
        5. Community-reported issues or improvements
        6. Local landmarks and navigation aids
        7. Safety considerations specific to the area
        8. Cultural context for tourists and non-locals
        
        Provide practical, locally-informed advice that complements official transport data.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        self.structured_llm = prompt | self.llm.with_structured_output(LocalInsights)
    
    async def get_local_insights(
        self,
        origin: str,
        destination: str,
        transport_mode: str = "any",
        travel_time: Optional[str] = None
    ) -> LocalInsights:
        """
        Get local knowledge and community insights for a journey.
        """
        try:
            # Get recent community updates
            community_updates = await self._get_community_updates(origin, destination, limit=10)
            
            # Get local route information
            local_routes = await self._get_local_routes(origin, destination)
            
            # Generate insights
            insights = await self.structured_llm.ainvoke({
                "origin": origin,
                "destination": destination,
                "transport_mode": transport_mode,
                "travel_time": travel_time or datetime.now().strftime("%H:%M"),
                "community_updates": community_updates,
                "local_routes": local_routes
            })
            
            return insights
            
        except Exception as e:
            print(f"Error getting local insights: {e}")
            return LocalInsights(
                local_tips=["Check with local authorities for current transport schedules"],
                community_alerts=["No recent community reports available"],
                cultural_context="Sri Lankan public transport follows local customs of respect and courtesy",
                hidden_routes=["Ask locals about informal transport options"],
                seasonal_considerations="Weather conditions may affect transport schedules",
                local_landmarks=["Use major temples and markets as navigation points"],
                safety_notes="Keep belongings secure and travel during daylight hours when possible"
            )
    
    async def _get_community_updates(self, origin: str, destination: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent community updates relevant to the route.
        """
        try:
            # Get updates from the past 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            updates_cursor = db.community_updates_collection.find({
                "$or": [
                    {"message": {"$regex": origin, "$options": "i"}},
                    {"message": {"$regex": destination, "$options": "i"}}
                ],
                "created_at": {"$gte": cutoff_date},
                "verified": {"$ne": False}  # Include unverified but not explicitly false
            }).sort("created_at", -1).limit(limit)
            
            updates = []
            async for update in updates_cursor:
                updates.append({
                    "message": update.get("message", ""),
                    "update_type": update.get("update_type", "general"),
                    "transport_mode": update.get("transport_mode", ""),
                    "created_at": update.get("created_at", "").isoformat() if update.get("created_at") else "",
                    "upvotes": update.get("upvotes", 0),
                    "verified": update.get("verified", False)
                })
            
            return updates
            
        except Exception as e:
            print(f"Error retrieving community updates: {e}")
            return []
    
    async def _get_local_routes(self, origin: str, destination: str) -> List[Dict]:
        """
        Get local route information including informal transport options.
        """
        try:
            routes = []
            
            # Check for informal transport services (tuk-tuks, shared taxis)
            tuk_tuk_cursor = db.tuk_tuk_services_collection.find({
                "coverage_area": {
                    "$regex": f"{origin}|{destination}",
                    "$options": "i"
                }
            }).limit(5)
            
            async for service in tuk_tuk_cursor:
                routes.append({
                    "type": "tuk_tuk",
                    "service_name": service.get("service_name", "Local Tuk-tuk"),
                    "coverage_area": service.get("coverage_area", ""),
                    "contact": service.get("contact_number", "Ask locals"),
                    "estimated_fare": service.get("base_fare", 0),
                    "waiting_time": service.get("estimated_arrival_time", 5)
                })
            
            # Add known local transport patterns
            local_patterns = self._get_local_transport_patterns(origin, destination)
            routes.extend(local_patterns)
            
            return routes
            
        except Exception as e:
            print(f"Error getting local routes: {e}")
            return []
    
    def _get_local_transport_patterns(self, origin: str, destination: str) -> List[Dict]:
        """
        Get known local transport patterns and informal routes.
        """
        # This would typically be populated from local knowledge database
        local_patterns = {
            "rural_areas": [
                {
                    "type": "shared_taxi",
                    "description": "Shared taxis (hire cars) operate on popular rural routes",
                    "timing": "Early morning and evening",
                    "fare_range": "50-200 LKR depending on distance",
                    "booking": "Ask at local shops or bus stands"
                }
            ],
            "hill_country": [
                {
                    "type": "estate_transport",
                    "description": "Tea estate workers' transport available to public",
                    "timing": "6:00 AM and 4:00 PM shifts",
                    "fare_range": "Very economical",
                    "booking": "Check with estate offices"
                }
            ],
            "coastal_areas": [
                {
                    "type": "fishermen_transport",
                    "description": "Fishing community transport during non-fishing hours",
                    "timing": "Mid-day hours",
                    "fare_range": "Negotiate locally",
                    "booking": "Harbor areas and fishing villages"
                }
            ]
        }
        
        # Return relevant patterns based on locations
        origin_lower = origin.lower()
        destination_lower = destination.lower()
        
        relevant_patterns = []
        
        if any(term in origin_lower or term in destination_lower 
               for term in ["village", "rural", "estate", "plantation"]):
            relevant_patterns.extend(local_patterns["rural_areas"])
        
        if any(term in origin_lower or term in destination_lower 
               for term in ["nuwara eliya", "kandy", "matale", "badulla"]):
            relevant_patterns.extend(local_patterns["hill_country"])
        
        if any(term in origin_lower or term in destination_lower 
               for term in ["galle", "matara", "negombo", "chilaw", "puttalam"]):
            relevant_patterns.extend(local_patterns["coastal_areas"])
        
        return relevant_patterns
    
    async def add_community_update(
        self,
        user_id: str,
        route_id: str,
        transport_mode: TransportMode,
        update_type: str,
        message: str,
        location: Optional[Location] = None
    ) -> bool:
        """
        Add a community-contributed update to the system.
        """
        try:
            community_update = CommunityUpdate(
                route_id=route_id,
                transport_mode=transport_mode,
                update_type=update_type,
                message=message,
                user_id=user_id,
                location=location,
                verified=False,  # Requires verification
                upvotes=0,
                downvotes=0
            )
            
            result = await db.community_updates_collection.insert_one(
                community_update.dict(exclude={"id"})
            )
            
            return result.inserted_id is not None
            
        except Exception as e:
            print(f"Error adding community update: {e}")
            return False
    
    async def verify_community_update(self, update_id: str, verified: bool) -> bool:
        """
        Verify or reject a community update.
        """
        try:
            result = await db.community_updates_collection.update_one(
                {"_id": update_id},
                {"$set": {"verified": verified}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error verifying community update: {e}")
            return False
    
    async def vote_on_update(self, update_id: str, vote_type: str, user_id: str) -> bool:
        """
        Allow users to vote on community updates (upvote/downvote).
        """
        try:
            if vote_type not in ["upvote", "downvote"]:
                return False
            
            # Check if user already voted (would need a separate votes collection in production)
            vote_field = "upvotes" if vote_type == "upvote" else "downvotes"
            
            result = await db.community_updates_collection.update_one(
                {"_id": update_id},
                {"$inc": {vote_field: 1}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error voting on update: {e}")
            return False
    
    async def get_crowdsourced_schedules(self, route_id: str) -> Dict[str, Any]:
        """
        Get crowdsourced schedule information from community reports.
        """
        try:
            # Find schedule-related updates for the route
            schedule_updates = await db.community_updates_collection.find({
                "route_id": route_id,
                "update_type": {"$in": ["schedule_change", "timing_update", "frequency_change"]},
                "verified": True,
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}  # Recent updates
            }).to_list(length=20)
            
            # Aggregate schedule insights
            schedule_insights = {
                "frequent_times": [],
                "delays_reported": [],
                "service_improvements": [],
                "community_notes": []
            }
            
            for update in schedule_updates:
                message = update.get("message", "").lower()
                
                if "delay" in message or "late" in message:
                    schedule_insights["delays_reported"].append({
                        "message": update.get("message", ""),
                        "timestamp": update.get("created_at", "")
                    })
                elif "time" in message or "schedule" in message:
                    schedule_insights["frequent_times"].append({
                        "message": update.get("message", ""),
                        "upvotes": update.get("upvotes", 0)
                    })
                elif "better" in message or "improved" in message:
                    schedule_insights["service_improvements"].append(update.get("message", ""))
                else:
                    schedule_insights["community_notes"].append(update.get("message", ""))
            
            return schedule_insights
            
        except Exception as e:
            print(f"Error getting crowdsourced schedules: {e}")
            return {"error": "Unable to retrieve community schedule data"}
    
    async def get_local_landmarks(self, origin: str, destination: str) -> List[Dict[str, str]]:
        """
        Get local landmarks and reference points for navigation.
        """
        try:
            # This would typically query a landmarks database
            landmarks = {
                "colombo": [
                    {"name": "Galle Face Green", "type": "landmark", "description": "Major coastal park"},
                    {"name": "Pettah Market", "type": "market", "description": "Central commercial area"},
                    {"name": "Fort Railway Station", "type": "transport", "description": "Main railway station"}
                ],
                "kandy": [
                    {"name": "Temple of the Tooth", "type": "religious", "description": "Sacred Buddhist temple"},
                    {"name": "Kandy Lake", "type": "landmark", "description": "Central lake in city"},
                    {"name": "Central Market", "type": "market", "description": "Local shopping area"}
                ],
                "galle": [
                    {"name": "Galle Fort", "type": "historical", "description": "UNESCO World Heritage site"},
                    {"name": "Dutch Hospital", "type": "landmark", "description": "Shopping and dining complex"}
                ]
            }
            
            relevant_landmarks = []
            
            for location in [origin.lower(), destination.lower()]:
                for city, city_landmarks in landmarks.items():
                    if city in location:
                        relevant_landmarks.extend(city_landmarks)
            
            return relevant_landmarks[:10]  # Return top 10 most relevant
            
        except Exception as e:
            print(f"Error getting local landmarks: {e}")
            return []