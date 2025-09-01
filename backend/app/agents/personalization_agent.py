from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.database import db
from app.models.transport import UserProfile, TransportMode, Location
from typing import List, Optional, Dict, Any
from datetime import datetime

class PersonalizedRecommendation(BaseModel):
    """Personalized travel recommendations based on user preferences."""
    recommended_routes: List[str] = Field(description="Recommended route options in order of preference")
    personalization_reason: str = Field(description="Why these routes match the user's preferences")
    accessibility_notes: str = Field(description="Accessibility considerations for this user")
    cost_estimation: str = Field(description="Estimated cost range based on user budget preferences")
    time_optimization: str = Field(description="How the recommendation optimizes for user's time preferences")

class PersonalizationAgent:
    """
    Agent that learns user preferences for travel modes, timings, and accessibility needs.
    Provides personalized route recommendations based on user history and preferences.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3,  # Slightly higher for more personalized responses
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        prompt_template = """You are a personalization expert for Sri Lanka's public transport system.
        
        Create personalized travel recommendations based on the user's profile and preferences.
        
        User Profile:
        {user_profile}
        
        Available Routes:
        {available_routes}
        
        Current Journey:
        Origin: {origin}
        Destination: {destination}
        Time of Travel: {travel_time}
        
        Travel History (if available):
        {travel_history}
        
        Consider:
        1. User's preferred transport modes
        2. Accessibility requirements
        3. Budget constraints
        4. Time preferences (express vs scenic)
        5. Past travel patterns
        6. Sri Lankan context (traffic patterns, cultural preferences)
        
        Provide personalized recommendations with clear reasoning.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        self.structured_llm = prompt | self.llm.with_structured_output(PersonalizedRecommendation)
    
    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        origin: str, 
        destination: str,
        available_routes: List[Dict],
        travel_time: Optional[str] = None
    ) -> PersonalizedRecommendation:
        """
        Generate personalized route recommendations for a user.
        """
        try:
            # Get user profile
            user_profile = await self.get_user_profile(user_id)
            if not user_profile:
                user_profile = await self.create_default_profile(user_id)
            
            # Get travel history
            travel_history = await self.get_travel_history(user_id, limit=10)
            
            # Generate personalized recommendations
            recommendation = await self.structured_llm.ainvoke({
                "user_profile": user_profile,
                "available_routes": available_routes,
                "origin": origin,
                "destination": destination,
                "travel_time": travel_time or datetime.now().strftime("%H:%M"),
                "travel_history": travel_history
            })
            
            # Update user preferences based on this query
            await self.update_user_preferences(user_id, origin, destination, travel_time)
            
            return recommendation
            
        except Exception as e:
            print(f"Error generating personalized recommendations: {e}")
            return PersonalizedRecommendation(
                recommended_routes=["Standard route recommendation"],
                personalization_reason="Using default recommendations due to system error",
                accessibility_notes="Standard accessibility features available",
                cost_estimation="Standard fare rates apply",
                time_optimization="Standard timing recommendations"
            )
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve user profile from database.
        """
        try:
            profile = await db.user_profiles_collection.find_one({"user_id": user_id})
            return profile
        except Exception as e:
            print(f"Error retrieving user profile: {e}")
            return None
    
    async def create_default_profile(self, user_id: str) -> Dict:
        """
        Create a default user profile for new users.
        """
        try:
            default_profile = UserProfile(
                user_id=user_id,
                preferred_language="en",
                accessibility_needs=[],
                preferred_transport_modes=[TransportMode.BUS, TransportMode.TRAIN],
                budget_preferences={"max_daily": 500, "prefer_economical": True},
                notification_preferences={
                    "disruptions": True,
                    "delays": True,
                    "offers": False
                }
            )
            
            result = await db.user_profiles_collection.insert_one(default_profile.dict(exclude={"id"}))
            if result.inserted_id:
                profile_dict = default_profile.dict()
                profile_dict["_id"] = result.inserted_id
                return profile_dict
            
        except Exception as e:
            print(f"Error creating default profile: {e}")
        
        return {
            "user_id": user_id,
            "preferred_language": "en",
            "accessibility_needs": [],
            "preferred_transport_modes": ["bus", "train"],
            "budget_preferences": {"max_daily": 500},
            "notification_preferences": {"disruptions": True, "delays": True}
        }
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        origin: str, 
        destination: str, 
        travel_time: Optional[str] = None
    ):
        """
        Update user preferences based on their search patterns.
        """
        try:
            current_time = datetime.utcnow()
            
            # Update frequently searched locations
            update_data = {
                "$inc": {"search_count": 1},
                "$set": {"last_search": current_time},
                "$addToSet": {
                    "frequent_origins": origin,
                    "frequent_destinations": destination
                }
            }
            
            if travel_time:
                # Analyze time preferences
                hour = int(travel_time.split(":")[0])
                if 6 <= hour <= 9:
                    time_preference = "morning_commute"
                elif 17 <= hour <= 20:
                    time_preference = "evening_commute"
                elif 10 <= hour <= 16:
                    time_preference = "midday"
                else:
                    time_preference = "off_peak"
                
                update_data["$addToSet"]["preferred_times"] = time_preference
            
            await db.user_profiles_collection.update_one(
                {"user_id": user_id},
                update_data,
                upsert=True
            )
            
        except Exception as e:
            print(f"Error updating user preferences: {e}")
    
    async def get_travel_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get user's recent travel history for pattern analysis.
        """
        try:
            # This would typically come from a travel_history collection
            # For now, we'll simulate with user profile data
            profile = await self.get_user_profile(user_id)
            if profile:
                return [{
                    "frequent_routes": profile.get("frequent_origins", []),
                    "preferred_times": profile.get("preferred_times", []),
                    "last_searches": profile.get("recent_searches", [])
                }]
            return []
            
        except Exception as e:
            print(f"Error retrieving travel history: {e}")
            return []
    
    async def learn_from_user_feedback(
        self, 
        user_id: str, 
        route_taken: str, 
        satisfaction_score: int, 
        feedback: str
    ):
        """
        Learn from user feedback to improve future recommendations.
        """
        try:
            feedback_data = {
                "user_id": user_id,
                "route_taken": route_taken,
                "satisfaction_score": satisfaction_score,  # 1-5 scale
                "feedback": feedback,
                "timestamp": datetime.utcnow()
            }
            
            # Store feedback for ML training
            await db.database.get_collection("user_feedback").insert_one(feedback_data)
            
            # Update user preferences based on feedback
            if satisfaction_score >= 4:
                # User liked this route, increase preference
                await db.user_profiles_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$addToSet": {"preferred_routes": route_taken},
                        "$inc": {"positive_feedback_count": 1}
                    }
                )
            elif satisfaction_score <= 2:
                # User disliked this route, decrease preference
                await db.user_profiles_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$addToSet": {"avoided_routes": route_taken},
                        "$inc": {"negative_feedback_count": 1}
                    }
                )
            
        except Exception as e:
            print(f"Error processing user feedback: {e}")
    
    async def get_accessibility_recommendations(self, user_id: str, routes: List[Dict]) -> List[Dict]:
        """
        Filter and enhance route recommendations based on accessibility needs.
        """
        try:
            profile = await self.get_user_profile(user_id)
            accessibility_needs = profile.get("accessibility_needs", []) if profile else []
            
            if not accessibility_needs:
                return routes
            
            enhanced_routes = []
            for route in routes:
                accessibility_info = {
                    "wheelchair_accessible": "wheelchair" in accessibility_needs,
                    "audio_guidance": "audio_guidance" in accessibility_needs,
                    "visual_aids": "visual_aids" in accessibility_needs
                }
                
                route["accessibility"] = accessibility_info
                
                # Filter out routes that don't meet accessibility requirements
                if "wheelchair" in accessibility_needs:
                    # Check if route supports wheelchair access
                    if route.get("type") == "train":
                        route["accessibility_score"] = 8  # Trains generally more accessible
                    elif route.get("type") == "bus" and route.get("operator") == "SLTB":
                        route["accessibility_score"] = 6  # Some SLTB buses are accessible
                    else:
                        route["accessibility_score"] = 3  # Lower score for uncertain accessibility
                
                enhanced_routes.append(route)
            
            # Sort by accessibility score if user has accessibility needs
            if accessibility_needs:
                enhanced_routes.sort(key=lambda x: x.get("accessibility_score", 0), reverse=True)
            
            return enhanced_routes
            
        except Exception as e:
            print(f"Error enhancing accessibility recommendations: {e}")
            return routes