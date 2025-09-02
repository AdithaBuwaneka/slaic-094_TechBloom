import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import math
from langchain.tools import BaseTool

class RouteComparisonTool(BaseTool):
    name: str = "route_comparison"
    description: str = "Compare and rank routes based on multiple criteria"
    
    def _run(self, routes: List[Dict], user_preferences: Dict, 
             weights: Optional[Dict] = None) -> Dict:
        """
        Compare routes using multi-criteria decision making
        """
        try:
            if not routes:
                return {"status": "error", "error": "No routes provided"}
            
            # Default weights if not provided
            default_weights = {
                "time": 0.3,
                "cost": 0.25,
                "comfort": 0.2,
                "convenience": 0.15,
                "reliability": 0.1
            }
            weights = weights or default_weights
            
            # Calculate scores for each route
            scored_routes = []
            for route in routes:
                score = self._calculate_route_score(route, user_preferences, weights)
                scored_routes.append({
                    "route": route,
                    "score": score,
                    "breakdown": score["breakdown"]
                })
            
            # Sort by total score (descending)
            scored_routes.sort(key=lambda x: x["score"]["total"], reverse=True)
            
            return {
                "status": "success",
                "ranked_routes": scored_routes,
                "weights_used": weights,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_route_score(self, route: Dict, preferences: Dict, 
                              weights: Dict) -> Dict:
        """Calculate comprehensive score for a single route"""
        
        # Time score (inverse - lower time is better)
        time_minutes = route.get("duration", 60)
        time_score = max(0, (120 - time_minutes) / 120)  # Normalize to 0-1
        
        # Cost score (inverse - lower cost is better)
        # Fix: Handle None fare_estimate safely
        fare_estimate = route.get("fare_estimate")
        if fare_estimate is None:
            cost = 50  # Default cost if no fare estimate
        else:
            cost = fare_estimate
        
        max_budget = self._get_max_budget(preferences.get("budget_preference", "medium"))
        cost_score = max(0, (max_budget - cost) / max_budget)
        
        # Comfort score
        comfort_score = self._calculate_comfort_score(route, preferences)
        
        # Convenience score (based on walking distance, transfers)
        convenience_score = self._calculate_convenience_score(route, preferences)
        
        # Reliability score (based on mode and historical data)
        reliability_score = self._calculate_reliability_score(route)
        
        # Calculate weighted total
        breakdown = {
            "time": time_score,
            "cost": cost_score,
            "comfort": comfort_score,
            "convenience": convenience_score,
            "reliability": reliability_score
        }
        
        # Debug: Check if all required keys exist in weights
        missing_keys = [criterion for criterion in breakdown if criterion not in weights]
        if missing_keys:
            print(f"⚠️  Missing weight keys: {missing_keys}")
            print(f"Available weight keys: {list(weights.keys())}")
            # Use default weights for missing keys
            default_weights = {"time": 0.3, "cost": 0.25, "comfort": 0.2, "convenience": 0.15, "reliability": 0.1}
            for key in missing_keys:
                weights[key] = default_weights.get(key, 0.1)
        
        total_score = sum(breakdown[criterion] * weights[criterion] 
                         for criterion in breakdown)
        
        return {
            "total": total_score,
            "breakdown": breakdown
        }
    
    def _get_max_budget(self, budget_preference: str) -> float:
        """Get maximum budget based on preference"""
        budgets = {"low": 20, "medium": 50, "high": 100}
        return budgets.get(budget_preference, 50)
    
    def _calculate_comfort_score(self, route: Dict, preferences: Dict) -> float:
        """Calculate comfort score based on route characteristics"""
        base_score = 0.5
        
        # Adjust based on transit mode
        transit_modes = route.get("transit_modes", [])
        for mode in transit_modes:
            if mode in ["train", "metro"]:
                base_score += 0.2
            elif mode in ["bus"]:
                base_score += 0.1
            elif mode in ["walk"]:
                base_score -= 0.1
        
        # Adjust for number of transfers
        transfers = route.get("transfers", 0)
        base_score -= transfers * 0.1
        
        return max(0, min(1, base_score))
    
    def _calculate_convenience_score(self, route: Dict, preferences: Dict) -> float:
        """Calculate convenience score"""
        base_score = 0.5
        
        # Walking distance factor
        walking_distance = route.get("walking_distance", 0.5)
        max_walking = preferences.get("max_walking_distance", 1.0)
        if walking_distance <= max_walking:
            base_score += 0.3
        else:
            base_score -= 0.2
        
        # Transfer penalty
        transfers = route.get("transfers", 0)
        base_score -= transfers * 0.15
        
        # Direct route bonus
        if transfers == 0:
            base_score += 0.2
        
        return max(0, min(1, base_score))
    
    def _calculate_reliability_score(self, route: Dict) -> float:
        """Calculate reliability score based on mode and conditions"""
        base_score = 0.7
        
        transit_modes = route.get("transit_modes", [])
        for mode in transit_modes:
            if mode == "train":
                base_score += 0.2
            elif mode == "metro":
                base_score += 0.3
            elif mode == "bus":
                base_score += 0.1
        
        # Weather impact (if available)
        if route.get("weather_impact"):
            base_score -= 0.1
        
        return max(0, min(1, base_score))

class LastMileOptimizerTool(BaseTool):
    name: str = "last_mile_optimizer"
    description: str = "Optimize last mile connections for transit routes"
    
    def _run(self, route: Dict, destination: str, user_preferences: Dict) -> Dict:
        """
        Analyze and optimize last mile options
        """
        try:
            transit_end_point = route.get("end_location", {})
            
            # Calculate distance to final destination
            last_mile_distance = self._calculate_distance(
                transit_end_point, destination
            )
            
            # Generate last mile options
            options = self._generate_last_mile_options(
                last_mile_distance, user_preferences
            )
            
            # Rank options
            ranked_options = self._rank_last_mile_options(
                options, user_preferences
            )
            
            return {
                "status": "success",
                "last_mile_distance": last_mile_distance,
                "options": ranked_options,
                "recommendation": ranked_options[0] if ranked_options else None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_distance(self, point1: Dict, point2: str) -> float:
        """Calculate distance between two points (simplified)"""
        # In real implementation, use proper geo calculations
        # This is a simplified version
        return 0.8  # Default 0.8 km
    
    def _generate_last_mile_options(self, distance: float, 
                                   preferences: Dict) -> List[Dict]:
        """Generate possible last mile options"""
        options = []
        
        # Walking option
        if distance <= getattr(preferences, "max_walking_distance", 1.5):
            walk_time = distance * 12  
            options.append({
                "mode": "walking",
                "duration": walk_time,
                "cost": 0,
                "distance": distance,
                "comfort": 0.3,
                "reliability": 0.9
            })
        
        # Uber option
        uber_time = distance * 3 + 5  # 3 min per km + 5 min wait
        uber_cost = max(8, distance * 2.5)  # Minimum fare or per km rate
        options.append({
            "mode": "uber",
            "duration": uber_time,
            "cost": uber_cost,
            "distance": distance,
            "comfort": 0.8,
            "reliability": 0.7
        })
        
        # Bike share (if available)
        if distance <= 3.0:
            bike_time = distance * 4  # ~4 minutes per km
            options.append({
                "mode": "bike_share",
                "duration": bike_time,
                "cost": 3,
                "distance": distance,
                "comfort": 0.6,
                "reliability": 0.8
            })
        
        return options
    
    def _rank_last_mile_options(self, options: List[Dict], 
                               preferences: Dict) -> List[Dict]:
        """Rank last mile options based on preferences"""
        time_weight = getattr(preferences, "time_vs_cost_weight", 0.5)
        cost_weight = 1 - time_weight
        
        for option in options:
            # Normalize time and cost scores
            time_score = max(0, (30 - option["duration"]) / 30)
            cost_score = max(0, (15 - option["cost"]) / 15)
            
            # Calculate composite score
            option["score"] = (
                time_score * time_weight * 0.4 +
                cost_score * cost_weight * 0.4 +
                option["comfort"] * 0.1 +
                option["reliability"] * 0.1
            )
        
        return sorted(options, key=lambda x: x["score"], reverse=True)

class PreferenceLearningTool(BaseTool):
    name: str = "preference_learning"
    description: str = "Learn and adapt user preferences from behavior"
    
    def _run(self, user_history: List[Dict], current_preferences: Dict, 
             recent_selections: List[Dict]) -> Dict:
        """
        Analyze user behavior and adapt preferences
        """
        try:
            # Analyze patterns in user selections
            patterns = self._analyze_selection_patterns(user_history)
            
            # Update preferences based on patterns
            updated_preferences = self._adapt_preferences(
                current_preferences, patterns, recent_selections
            )
            
            # Calculate confidence scores for preferences
            confidence_scores = self._calculate_confidence_scores(
                user_history, updated_preferences
            )
            
            return {
                "status": "success",
                "updated_preferences": updated_preferences,
                "confidence_scores": confidence_scores,
                "detected_patterns": patterns,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_selection_patterns(self, history: List[Dict]) -> Dict:
        """Analyze patterns in user's historical selections"""
        patterns = {
            "preferred_modes": {},
            "time_vs_cost_tendency": 0,
            "walking_tolerance": 0,
            "transfer_tolerance": 0,
            "cost_sensitivity": 0
        }
        
        if not history:
            return patterns
        
        for selection in history:
            # Count mode preferences
            mode = selection.get("selected_mode")
            if mode:
                patterns["preferred_modes"][mode] = (
                    patterns["preferred_modes"].get(mode, 0) + 1
                )
            
            # Analyze time vs cost choices
            if "selected_for_time" in selection:
                if selection["selected_for_time"]:
                    patterns["time_vs_cost_tendency"] += 1
                else:
                    patterns["time_vs_cost_tendency"] -= 1
        
        # Normalize tendencies
        history_count = len(history)
        patterns["time_vs_cost_tendency"] /= max(1, history_count)
        
        return patterns
    
    def _adapt_preferences(self, current_prefs: Dict, patterns: Dict, 
                          recent_selections: List[Dict]) -> Dict:
        """Adapt preferences based on detected patterns"""
        updated_prefs = current_prefs.copy()
        learning_rate = 0.15
        
        # Update time vs cost weight
        time_tendency = patterns.get("time_vs_cost_tendency", 0)
        current_weight = getattr(updated_prefs, "time_vs_cost_weight", 0.5)
        new_weight = current_weight + (time_tendency * learning_rate)
        updated_prefs["time_vs_cost_weight"] = max(0, min(1, new_weight))
        
        # Update preferred modes based on frequency
        preferred_modes = patterns.get("preferred_modes", {})
        if preferred_modes:
            most_used = max(preferred_modes.items(), key=lambda x: x[1])
            if most_used[0] not in getattr(updated_prefs, "preferred_transit_modes", []):
                if not hasattr(updated_prefs, "preferred_transit_modes"):
                    updated_prefs["preferred_transit_modes"] = []
                updated_prefs["preferred_transit_modes"].append(most_used[0])
        
        return updated_prefs
    
    def _calculate_confidence_scores(self, history: List[Dict], 
                                   preferences: Dict) -> Dict:
        """Calculate confidence scores for each preference"""
        history_count = len(history)
        
        # Base confidence on amount of historical data
        base_confidence = min(0.9, history_count / 20)  # Max confidence at 20+ selections
        
        confidence_scores = {
            "time_vs_cost_weight": base_confidence,
            "preferred_modes": base_confidence * 0.8,
            "walking_tolerance": base_confidence * 0.6,
            "overall": base_confidence
        }
        
        return confidence_scores