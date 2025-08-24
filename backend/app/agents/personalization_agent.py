from app.agents.base_agent import BaseAgent
from app.models.personalization import (
    UserProfile, TravelHistory, TravelPreferences, PersonalizationInsights,
    PersonalizationRecommendation, LearningEvent, PersonalizationMetrics,
    PreferenceUpdateRequest, TravelPurpose, TimeFlexibility, BudgetSensitivity,
    ComfortPreference
)
from app.models.transport_data import Location, TransportMode
from app.models.route_optimization import OptimizedRoute
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import math
import json
from datetime import datetime, timedelta
import random


class PersonalizationAgent(BaseAgent):
    """
    Personalization Agent - Adaptive User Experience
    
    Primary Functions:
    - Travel pattern recognition and analysis
    - Preference evolution tracking
    - Context-aware recommendation refinement  
    - Behavioral modeling and prediction
    - Cost sensitivity analysis
    - Time flexibility assessment
    - Comfort priority evaluation
    - Accessibility need accommodation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="personalization_agent",
            name="Personalization Agent",
            priority_weight=0.8  # High priority for user experience
        )
        
        # In-memory storage for demo (in production would use MongoDB)
        self.user_profiles = {}
        self.travel_history = {}
        self.user_insights = {}
        self.learning_events = {}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.min_trips_for_learning = 3
        self.confidence_threshold = 0.6
        
        # Context weights for different situations
        self.context_weights = {
            "weather_rainy": {"comfort": 0.3, "cost": -0.2},
            "weather_hot": {"comfort": 0.2, "time": 0.1},
            "rush_hour": {"time": 0.4, "reliability": 0.3},
            "weekend": {"cost": 0.2, "comfort": 0.1},
            "with_luggage": {"comfort": 0.4, "walking": -0.3},
            "group_travel": {"cost": 0.2, "comfort": 0.1}
        }
        
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for personalization requests"""
        
        request_type = payload.get("request_type", "")
        data = payload.get("data", {})
        
        if request_type == "get_user_preferences":
            return await self._get_user_preferences(data)
        elif request_type == "update_preferences":
            return await self._update_user_preferences(data)
        elif request_type == "analyze_travel_patterns":
            return await self._analyze_travel_patterns(data)
        elif request_type == "generate_personalized_recommendations":
            return await self._generate_personalized_recommendations(data)
        elif request_type == "record_travel_feedback":
            return await self._record_travel_feedback(data)
        elif request_type == "create_user_profile":
            return await self._create_user_profile(data)
        elif request_type == "get_personalization_insights":
            return await self._get_personalization_insights(data)
        elif request_type == "evaluate_personalization_metrics":
            return await self._evaluate_personalization_metrics(data)
        else:
            return {
                "status": "unknown_request",
                "message": f"Unknown request type: {request_type}",
                "supported_requests": [
                    "get_user_preferences", "update_preferences", "analyze_travel_patterns",
                    "generate_personalized_recommendations", "record_travel_feedback",
                    "create_user_profile", "get_personalization_insights",
                    "evaluate_personalization_metrics"
                ]
            }
            
    async def _create_user_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        
        try:
            user_id = data.get("user_id")
            if not user_id:
                return {"status": "error", "message": "user_id is required"}
                
            # Create profile with provided data or defaults
            profile_data = {
                "user_id": user_id,
                "name": data.get("name"),
                "age_group": data.get("age_group"),
                "occupation": data.get("occupation"),
                "preferred_modes": data.get("preferred_modes", ["bus", "train"]),
                "budget_sensitivity": data.get("budget_sensitivity", "moderate"),
                "comfort_preference": data.get("comfort_preference", "standard"),
                "time_flexibility": data.get("time_flexibility", "moderate"),
                "max_walking_distance_meters": data.get("max_walking_distance_meters", 800),
                "max_acceptable_transfers": data.get("max_acceptable_transfers", 2)
            }
            
            # Parse locations if provided
            if "home_location" in data:
                profile_data["home_location"] = Location(**data["home_location"])
            if "work_location" in data:
                profile_data["work_location"] = Location(**data["work_location"])
                
            profile = UserProfile(**profile_data)
            
            # Store profile
            self.user_profiles[user_id] = profile
            
            # Initialize other user data
            self.travel_history[user_id] = []
            self.user_insights[user_id] = None
            self.learning_events[user_id] = []
            
            return {
                "status": "success",
                "message": "User profile created successfully",
                "user_profile": profile.dict(),
                "recommendations": [
                    "Take a few trips to help us learn your preferences",
                    "Rate your journeys to improve recommendations",
                    "Update your profile as your needs change"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create user profile: {str(e)}"
            }
            
    async def _get_user_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user preferences with context awareness"""
        
        try:
            user_id = data.get("user_id")
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            profile = self.user_profiles[user_id]
            context = data.get("context", {})
            
            # Generate context-aware preferences
            preferences = await self._generate_contextual_preferences(profile, context)
            
            return {
                "status": "success",
                "user_id": user_id,
                "base_preferences": {
                    "preferred_modes": profile.preferred_modes,
                    "budget_sensitivity": profile.budget_sensitivity,
                    "comfort_preference": profile.comfort_preference,
                    "time_flexibility": profile.time_flexibility,
                    "max_walking_distance": profile.max_walking_distance_meters,
                    "max_transfers": profile.max_acceptable_transfers
                },
                "contextual_preferences": preferences.dict(),
                "learning_status": {
                    "trips_taken": profile.trips_taken,
                    "preferences_learned": profile.preferences_learned,
                    "profile_age_days": (datetime.utcnow() - profile.profile_created).days
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user preferences: {str(e)}"
            }
            
    async def _generate_contextual_preferences(self, profile: UserProfile, 
                                             context: Dict[str, Any]) -> TravelPreferences:
        """Generate context-aware preferences based on user profile and current context"""
        
        # Start with base preferences
        base_weights = {
            "time": 0.4,
            "cost": 0.3 if profile.budget_sensitivity == BudgetSensitivity.MODERATE else 
                    (0.5 if profile.budget_sensitivity in [BudgetSensitivity.HIGH, BudgetSensitivity.VERY_HIGH] else 0.2),
            "comfort": 0.15 if profile.comfort_preference == ComfortPreference.STANDARD else
                      (0.3 if profile.comfort_preference in [ComfortPreference.PREMIUM, ComfortPreference.LUXURY] else 0.1),
            "reliability": 0.15
        }
        
        # Adjust for context
        weather = context.get("weather_condition", "clear")
        time_of_day = context.get("time_of_day", "day")
        purpose = context.get("purpose", "commute")
        with_luggage = context.get("with_luggage", False)
        group_size = context.get("group_size", 1)
        
        # Weather adjustments
        if weather in ["rainy", "heavy_rain"]:
            base_weights["comfort"] += 0.2
            base_weights["time"] -= 0.1
        elif weather in ["very_hot", "sunny"]:
            base_weights["comfort"] += 0.1
            
        # Time of day adjustments
        if time_of_day == "rush_hour":
            base_weights["time"] += 0.2
            base_weights["reliability"] += 0.1
        elif time_of_day == "night":
            base_weights["comfort"] += 0.1
            base_weights["reliability"] += 0.1
            
        # Purpose adjustments
        if purpose == "business":
            base_weights["time"] += 0.2
            base_weights["reliability"] += 0.2
            base_weights["cost"] -= 0.1
        elif purpose == "leisure":
            base_weights["cost"] += 0.1
            base_weights["comfort"] += 0.1
            base_weights["time"] -= 0.1
            
        # Luggage adjustment
        if with_luggage:
            base_weights["comfort"] += 0.2
            base_weights["time"] -= 0.1
            
        # Group size adjustment
        if group_size > 1:
            base_weights["cost"] += 0.1
            base_weights["comfort"] += 0.1
            
        # Normalize weights
        total_weight = sum(base_weights.values())
        normalized_weights = {k: v/total_weight for k, v in base_weights.items()}
        
        # Generate mode preferences based on context
        mode_prefs = {}
        for mode in TransportMode:
            base_pref = 0.5  # Neutral
            
            # Apply user's preferred/avoided modes
            if mode in profile.preferred_modes:
                base_pref += 0.3
            if mode in profile.avoided_modes:
                base_pref -= 0.3
                
            # Context adjustments
            if weather == "rainy" and mode == TransportMode.WALKING:
                base_pref -= 0.4
            if with_luggage and mode == TransportMode.WALKING:
                base_pref -= 0.3
            if group_size > 2 and mode == TransportMode.TAXI:
                base_pref += 0.2
                
            mode_prefs[mode] = max(-1.0, min(1.0, base_pref))
            
        preferences = TravelPreferences(
            user_id=profile.user_id,
            context=context,
            time_importance=normalized_weights["time"],
            cost_importance=normalized_weights["cost"],
            comfort_importance=normalized_weights["comfort"],
            reliability_importance=normalized_weights["reliability"],
            mode_preferences=mode_prefs,
            departure_flexibility_minutes=30 if profile.time_flexibility == TimeFlexibility.FLEXIBLE else 15
        )
        
        return preferences
        
    async def _analyze_travel_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's travel patterns and generate insights"""
        
        try:
            user_id = data.get("user_id")
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            profile = self.user_profiles[user_id]
            history = self.travel_history.get(user_id, [])
            
            if len(history) < self.min_trips_for_learning:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least {self.min_trips_for_learning} trips for pattern analysis",
                    "current_trips": len(history),
                    "suggestions": ["Take more trips to enable pattern learning"]
                }
                
            # Simulate pattern analysis (in real implementation would analyze actual history)
            insights = PersonalizationInsights(
                user_id=user_id,
                most_common_routes=[
                    {"origin": "Colombo Fort", "destination": "Kandy", "frequency": 0.4},
                    {"origin": "Galle", "destination": "Colombo", "frequency": 0.3}
                ],
                peak_travel_times=["08:00-09:00", "17:30-18:30"],
                preferred_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
                mode_usage_frequency={
                    TransportMode.BUS: 0.6,
                    TransportMode.TRAIN: 0.3,
                    TransportMode.WALKING: 0.1
                },
                mode_satisfaction_scores={
                    TransportMode.BUS: 3.8,
                    TransportMode.TRAIN: 4.2,
                    TransportMode.WALKING: 3.5
                },
                average_trip_cost=85.0,
                budget_adherence_rate=0.85,
                cost_sensitivity_score=0.7 if profile.budget_sensitivity == BudgetSensitivity.HIGH else 0.5,
                average_trip_duration=95.0,
                on_time_performance=0.78,
                time_flexibility_score=0.6,
                comfort_vs_cost_ratio=0.4,
                transfer_tolerance=0.7,
                walking_tolerance=0.6,
                reliability_importance_score=0.8,
                disruption_adaptation_score=0.6,
                weather_impact_patterns={"rainy": -0.3, "sunny": 0.1, "cloudy": 0.0},
                time_of_day_patterns={"morning": 0.2, "afternoon": 0.0, "evening": -0.1},
                prediction_confidence=min(0.9, len(history) / 20),  # Confidence grows with data
                data_points_analyzed=len(history)
            )
            
            # Store insights
            self.user_insights[user_id] = insights
            
            # Update profile learning status
            profile.preferences_learned = True
            profile.last_updated = datetime.utcnow()
            
            return {
                "status": "success",
                "insights": insights.dict(),
                "learning_recommendations": [
                    "Patterns successfully identified",
                    "Recommendations will now be personalized",
                    "Continue taking trips to improve accuracy"
                ],
                "confidence_level": "high" if insights.prediction_confidence > 0.8 else 
                                  ("medium" if insights.prediction_confidence > 0.6 else "low")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze travel patterns: {str(e)}"
            }
            
    async def _generate_personalized_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized recommendations for route selection"""
        
        try:
            user_id = data.get("user_id")
            routes = data.get("routes", [])
            context = data.get("context", {})
            
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            if not routes:
                return {"status": "error", "message": "No routes provided for personalization"}
                
            profile = self.user_profiles[user_id]
            insights = self.user_insights.get(user_id)
            
            # Generate contextual preferences
            preferences = await self._generate_contextual_preferences(profile, context)
            
            # Score routes based on personal preferences
            personalized_scores = {}
            reasoning = []
            
            for route in routes:
                route_id = route.get("route_id", "unknown")
                
                # Calculate personalized score
                base_score = route.get("overall_score", 0.5)
                
                # Apply preference weights
                time_score = route.get("time_score", 0.5)
                cost_score = route.get("cost_score", 0.5)
                comfort_score = route.get("comfort_score", 0.5)
                reliability_score = route.get("reliability_score", 0.5)
                
                personalized_score = (
                    time_score * preferences.time_importance +
                    cost_score * preferences.cost_importance +
                    comfort_score * preferences.comfort_importance +
                    reliability_score * preferences.reliability_importance
                )
                
                # Apply mode preferences
                modes_used = route.get("segments", [{}])[0].get("transport_mode", "bus")
                if modes_used in preferences.mode_preferences:
                    mode_bonus = preferences.mode_preferences[modes_used] * 0.1
                    personalized_score += mode_bonus
                    
                # Apply insights if available
                if insights:
                    # Bonus for frequently used modes
                    if modes_used in insights.mode_usage_frequency:
                        frequency_bonus = insights.mode_usage_frequency[modes_used] * 0.05
                        personalized_score += frequency_bonus
                        
                    # Adjust for cost sensitivity
                    if route.get("total_cost", 0) > insights.average_trip_cost * 1.5:
                        if insights.cost_sensitivity_score > 0.7:
                            personalized_score -= 0.1  # Penalize expensive routes for cost-sensitive users
                            
                personalized_scores[route_id] = max(0.0, min(1.0, personalized_score))
                
            # Find best personalized route
            best_route_id = max(personalized_scores.items(), key=lambda x: x[1])[0]
            
            # Generate reasoning
            reasoning = [
                f"Personalized based on your {profile.budget_sensitivity} budget sensitivity",
                f"Adjusted for {profile.comfort_preference} comfort preference",
                f"Considered your {profile.time_flexibility} time flexibility"
            ]
            
            if insights:
                reasoning.extend([
                    f"Based on analysis of {insights.data_points_analyzed} previous trips",
                    f"Matched your travel patterns with {insights.prediction_confidence:.1%} confidence"
                ])
                
            # Context-specific reasoning
            weather = context.get("weather_condition")
            if weather == "rainy":
                reasoning.append("Prioritized comfort due to rainy weather")
            
            purpose = context.get("purpose")
            if purpose == "business":
                reasoning.append("Emphasized reliability and time for business travel")
                
            # Create simplified personalization factors dictionary
            personalization_factors = {
                "time_importance": preferences.time_importance,
                "cost_importance": preferences.cost_importance,
                "comfort_importance": preferences.comfort_importance,
                "reliability_importance": preferences.reliability_importance,
                "departure_flexibility_minutes": preferences.departure_flexibility_minutes
            }
            
            recommendation = PersonalizationRecommendation(
                recommendation_id=f"rec_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                request_context=context,
                personalization_factors=personalization_factors,
                confidence_score=insights.prediction_confidence if insights else 0.3,
                personalized_route_scores=personalized_scores,
                reasoning=reasoning,
                alternative_suggestions=[
                    "Try the train for better comfort on longer trips",
                    "Consider off-peak times for better prices",
                    "Walking + bus combination saves money"
                ] if profile.budget_sensitivity in [BudgetSensitivity.HIGH, BudgetSensitivity.VERY_HIGH] else []
            )
            
            return {
                "status": "success",
                "recommendation": recommendation.dict(),
                "best_route_id": best_route_id,
                "personalization_summary": {
                    "factors_considered": len(personalized_scores),
                    "confidence": recommendation.confidence_score,
                    "learning_status": "active" if insights else "building"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate personalized recommendations: {str(e)}"
            }
            
    async def _record_travel_feedback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Record user feedback about a trip for learning"""
        
        try:
            user_id = data.get("user_id")
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            # Create travel history entry
            trip_data = {
                "trip_id": data.get("trip_id", f"trip_{datetime.utcnow().isoformat()}"),
                "user_id": user_id,
                "origin": Location(**data["origin"]) if "origin" in data else None,
                "destination": Location(**data["destination"]) if "destination" in data else None,
                "departure_time": datetime.fromisoformat(data.get("departure_time", datetime.utcnow().isoformat())),
                "arrival_time": datetime.fromisoformat(data.get("arrival_time", datetime.utcnow().isoformat())),
                "actual_duration_minutes": data.get("actual_duration_minutes", 60),
                "chosen_route_id": data.get("chosen_route_id", "unknown"),
                "transport_modes_used": data.get("transport_modes_used", ["bus"]),
                "total_cost": data.get("total_cost", 0.0),
                "purpose": data.get("purpose", "commute"),
                "satisfaction_rating": data.get("satisfaction_rating"),
                "weather_condition": data.get("weather_condition"),
                "rush_hour": data.get("rush_hour", False),
                "with_luggage": data.get("with_luggage", False),
                "group_size": data.get("group_size", 1)
            }
            
            trip_history = TravelHistory(**trip_data)
            
            # Store trip history
            if user_id not in self.travel_history:
                self.travel_history[user_id] = []
            self.travel_history[user_id].append(trip_history)
            
            # Update profile trip count
            profile = self.user_profiles[user_id]
            profile.trips_taken += 1
            profile.last_updated = datetime.utcnow()
            
            # Create learning event
            learning_event = LearningEvent(
                event_id=f"feedback_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                event_type="travel_feedback",
                event_data=trip_data,
                confidence_weight=1.0,
                learning_value=0.2 if trip_data.get("satisfaction_rating", 3) >= 4 else -0.1,
                context_at_event=data.get("context", {})
            )
            
            self.learning_events.setdefault(user_id, []).append(learning_event)
            
            # Determine if we should re-analyze patterns
            should_reanalyze = (profile.trips_taken % 5 == 0 and 
                               profile.trips_taken >= self.min_trips_for_learning)
            
            return {
                "status": "success",
                "message": "Travel feedback recorded successfully",
                "trip_recorded": trip_history.dict(),
                "learning_status": {
                    "total_trips": profile.trips_taken,
                    "should_reanalyze_patterns": should_reanalyze,
                    "learning_confidence": min(1.0, profile.trips_taken / 20)
                },
                "next_steps": [
                    "Pattern analysis will be updated" if should_reanalyze else
                    f"Take {self.min_trips_for_learning - profile.trips_taken} more trips for pattern analysis"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to record travel feedback: {str(e)}"
            }
            
    async def _update_user_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences based on explicit feedback or implicit learning"""
        
        try:
            user_id = data.get("user_id")
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            profile = self.user_profiles[user_id]
            updates = data.get("preference_changes", {})
            update_type = data.get("update_type", "explicit")
            
            # Apply updates
            updated_fields = []
            for field, new_value in updates.items():
                if hasattr(profile, field):
                    old_value = getattr(profile, field)
                    setattr(profile, field, new_value)
                    updated_fields.append(f"{field}: {old_value} → {new_value}")
                    
            profile.last_updated = datetime.utcnow()
            
            # Create learning event
            learning_event = LearningEvent(
                event_id=f"pref_update_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                event_type="preference_update",
                event_data={"updates": updates, "type": update_type},
                confidence_weight=1.0 if update_type == "explicit" else 0.5,
                learning_value=0.1,
                context_at_event=data.get("context", {})
            )
            
            self.learning_events.setdefault(user_id, []).append(learning_event)
            
            return {
                "status": "success",
                "message": "Preferences updated successfully",
                "updated_fields": updated_fields,
                "updated_profile": profile.dict(),
                "learning_event": learning_event.dict()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update user preferences: {str(e)}"
            }
            
    async def _get_personalization_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalization insights for a user"""
        
        try:
            user_id = data.get("user_id")
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            insights = self.user_insights.get(user_id)
            if not insights:
                return {
                    "status": "no_insights",
                    "message": "Insufficient data for insights generation",
                    "suggestion": "Take more trips to generate personalization insights"
                }
                
            return {
                "status": "success",
                "insights": insights.dict(),
                "summary": {
                    "learning_confidence": insights.prediction_confidence,
                    "trips_analyzed": insights.data_points_analyzed,
                    "top_preferences": [
                        f"Most used transport: {max(insights.mode_usage_frequency.items(), key=lambda x: x[1])[0].value}",
                        f"Average trip cost: Rs.{insights.average_trip_cost:.0f}",
                        f"On-time rate: {insights.on_time_performance:.1%}"
                    ]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get personalization insights: {str(e)}"
            }
            
    async def _evaluate_personalization_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the effectiveness of personalization for a user"""
        
        try:
            user_id = data.get("user_id")
            if not user_id or user_id not in self.user_profiles:
                return {"status": "error", "message": "User profile not found"}
                
            # Simulate metrics calculation (would be based on actual user behavior)
            metrics = PersonalizationMetrics(
                user_id=user_id,
                evaluation_period_days=30,
                recommendation_acceptance_rate=random.uniform(0.7, 0.9),
                user_satisfaction_trend=random.uniform(0.1, 0.3),
                prediction_accuracy_score=random.uniform(0.6, 0.9),
                preference_stability_score=random.uniform(0.7, 0.95),
                adaptation_speed_score=random.uniform(0.5, 0.8),
                context_awareness_score=random.uniform(0.6, 0.9),
                active_feedback_rate=random.uniform(0.3, 0.7),
                preference_exploration_rate=random.uniform(0.1, 0.4),
                system_trust_score=random.uniform(0.7, 0.95)
            )
            
            # Determine overall personalization quality
            overall_score = (
                metrics.recommendation_acceptance_rate * 0.3 +
                metrics.prediction_accuracy_score * 0.25 +
                metrics.context_awareness_score * 0.2 +
                metrics.system_trust_score * 0.15 +
                metrics.preference_stability_score * 0.1
            )
            
            quality_rating = (
                "excellent" if overall_score > 0.8 else
                "good" if overall_score > 0.6 else
                "needs_improvement"
            )
            
            return {
                "status": "success",
                "metrics": metrics.dict(),
                "overall_score": overall_score,
                "quality_rating": quality_rating,
                "recommendations": [
                    "Personalization is working well" if overall_score > 0.8 else
                    "Consider providing more feedback to improve recommendations",
                    "Try different transport modes to improve exploration",
                    "Rate your trips to help us learn your preferences better"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to evaluate personalization metrics: {str(e)}"
            }