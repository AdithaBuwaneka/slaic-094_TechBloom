import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class IntelligentDisruptionService:
    """
    Intelligent disruption monitoring service using Gemini 2.0 Flash LLM
    to analyze disruptions and recommend alternative routes based on user preferences,
    cost, duration, and other factors.
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY environment variable is not set")
        
        # Configure Google Generative AI
        genai.configure(api_key=self.api_key)
        
        # Initialize the Gemini 2.0 Flash model
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print(" Gemini model initialized successfully for disruption monitoring")
        except Exception as e:
            print(f" Error initializing Gemini : {str(e)}")
            # Fallback to Gemini 1.5 Flash if 2.0 is not available
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print(" Fallback to Gemini 1.5 Flash model initialized successfully")
            except Exception as e2:
                print(f" Error initializing fallback model: {str(e2)}")
                raise
    
    def analyze_disruption_and_recommend_routes(self, 
                                              disruptions: List[Dict],
                                              available_routes: List[Dict],
                                              user_preferences: Optional[Dict],
                                              source: str,
                                              destination: str) -> Dict[str, Any]:
        """
        Analyze disruptions and recommend the best alternative routes using AI
        
        Args:
            disruptions: List of active disruptions
            available_routes: List of routes from transit_route_aggregation agent
            user_preferences: User's travel preferences
            source: Origin location
            destination: Destination location
        
        Returns:
            Dictionary with analysis results and recommendations
        """
        try:
            # Prepare data for LLM analysis
            analysis_data = self._prepare_analysis_data(
                disruptions, available_routes, user_preferences, source, destination
            )
            
            # Create intelligent prompt for route recommendation
            prompt = self._create_route_recommendation_prompt(analysis_data)
            
            # Generate recommendation using Gemini 2.0 Flash
            response = self.model.generate_content(prompt)
            
            # Process the AI response
            recommendation_result = self._process_ai_recommendation(response, available_routes)
            
            return {
                "status": "success",
                "disruption_analysis": recommendation_result["analysis"],
                "recommended_routes": recommendation_result["recommendations"],
                "reasoning": recommendation_result["reasoning"],
                "confidence_score": recommendation_result["confidence"],
                "timestamp": datetime.now().isoformat(),
                "model_used": "gemini-2.0-flash-exp"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_analysis_data(self, 
                              disruptions: List[Dict],
                              available_routes: List[Dict],
                              user_preferences: Optional[Dict],
                              source: str,
                              destination: str) -> Dict[str, Any]:
        """Prepare data for LLM analysis"""
        
        # Extract route information
        route_summaries = []
        for i, route in enumerate(available_routes):
            route_summary = {
                "route_id": route.get("route_id", f"route_{i}"),
                "duration_minutes": route.get("duration", 0),
                "distance_km": route.get("distance", 0),
                "transit_modes": route.get("transit_modes", []),
                "transfers": route.get("transfers", 0),
                "walking_distance_km": route.get("walking_distance", 0),
                "estimated_cost_lkr": route.get("fare_estimate", 0),
                "steps_count": len(route.get("steps", [])),
                "category": route.get("category", "unknown")
            }
            route_summaries.append(route_summary)
        
        # Extract disruption information
        disruption_summaries = []
        for disruption in disruptions:
            disruption_summary = {
                "disruption_id": disruption.get("disruption_id", "unknown"),
                "location": disruption.get("location", "unknown"),
                "type": disruption.get("type", "unknown"),
                "severity": disruption.get("severity", "medium"),
                "description": disruption.get("description", "No description available")
            }
            disruption_summaries.append(disruption_summary)
        
        # Extract user preferences
        user_prefs_summary = {}
        if user_preferences:
            user_prefs_summary = {
                "preferred_transit_modes": getattr(user_preferences, "preferred_transit_modes", ["bus", "train"]),
                "max_walking_distance_km": getattr(user_preferences, "max_walking_distance", 1.0),
                "budget_preference": getattr(user_preferences, "budget_preference", "medium"),
                "time_vs_cost_weight": getattr(user_preferences, "time_vs_cost_weight", 0.5),
                "comfort_preference": getattr(user_preferences, "comfort_preference", 0.7),
                "accessibility_needs": getattr(user_preferences, "accessibility_needs", [])
            }
        else:
            user_prefs_summary = {
                "preferred_transit_modes": ["bus", "train"],
                "max_walking_distance_km": 1.0,
                "budget_preference": "medium",
                "time_vs_cost_weight": 0.5,
                "comfort_preference": 0.7,
                "accessibility_needs": []
            }
        
        return {
            "source": source,
            "destination": destination,
            "disruptions": disruption_summaries,
            "available_routes": route_summaries,
            "user_preferences": user_prefs_summary,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _create_route_recommendation_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Create an intelligent prompt for route recommendation"""
        
        prompt = f"""
You are an intelligent travel disruption analyst and route recommendation system. Your task is to analyze transit disruptions and recommend the best alternative routes based on user preferences, cost, duration, and other factors.

TRAVEL CONTEXT:
- Route: {analysis_data['source']} to {analysis_data['destination']}
- Analysis Time: {analysis_data['analysis_timestamp']}

ACTIVE DISRUPTIONS:
{self._format_disruptions_for_prompt(analysis_data['disruptions'])}

AVAILABLE ROUTES:
{self._format_routes_for_prompt(analysis_data['available_routes'])}

USER PREFERENCES:
{self._format_preferences_for_prompt(analysis_data['user_preferences'])}

ANALYSIS REQUIREMENTS:
1. Analyze the impact of each disruption on the available routes
2. Consider user preferences for transit modes, walking distance, cost, and time
3. Evaluate routes based on:
   - Duration (shorter is better)
   - Cost (lower is better, but consider user budget preference)
   - Walking distance (should not exceed user's max walking distance)
   - Number of transfers (fewer is generally better)
   - Transit modes (prefer user's preferred modes)
   - Comfort and reliability
4. Provide a confidence score (0-100) for your recommendations
5. Explain your reasoning clearly

RESPONSE FORMAT:
Provide your analysis in the following JSON format:
{{
    "disruption_impact_analysis": {{
        "high_impact_routes": ["route_ids_affected_by_disruptions"],
        "medium_impact_routes": ["route_ids_with_minor_impact"],
        "unaffected_routes": ["route_ids_not_affected"]
    }},
    "route_rankings": [
        {{
            "route_id": "route_id",
            "rank": 1,
            "score": 85.5,
            "reasoning": "Brief explanation of why this route is recommended",
            "pros": ["advantage1", "advantage2"],
            "cons": ["disadvantage1", "disadvantage2"],
            "estimated_impact_from_disruptions": "low/medium/high"
        }}
    ],
    "top_recommendation": {{
        "route_id": "best_route_id",
        "confidence_score": 90,
        "primary_reasons": ["reason1", "reason2", "reason3"],
        "alternative_if_unavailable": "second_best_route_id"
    }},
    "summary": "2-3 sentence summary of the disruption situation and recommendation"
}}

IMPORTANT:
- Be practical and consider real-world travel constraints
- Prioritize user safety and comfort
- Consider the severity of disruptions
- Provide actionable recommendations
- If all routes are severely impacted, suggest waiting or alternative travel times
"""
        
        return prompt
    
    def _format_disruptions_for_prompt(self, disruptions: List[Dict]) -> str:
        """Format disruptions for the prompt"""
        if not disruptions:
            return "No active disruptions reported."
        
        formatted = []
        for disruption in disruptions:
            formatted.append(f"""
- Disruption ID: {disruption['disruption_id']}
  Location: {disruption['location']}
  Type: {disruption['type']}
  Severity: {disruption['severity']}
  Description: {disruption['description']}
""")
        return "\n".join(formatted)
    
    def _format_routes_for_prompt(self, routes: List[Dict]) -> str:
        """Format routes for the prompt"""
        if not routes:
            return "No routes available."

        formatted = []
        for route in routes:
            # Handle None values safely
            cost_lkr = route['estimated_cost_lkr'] if route['estimated_cost_lkr'] is not None else 0
            distance_km = route['distance_km'] if route['distance_km'] is not None else 0
            walking_distance_km = route['walking_distance_km'] if route['walking_distance_km'] is not None else 0

            formatted.append(f"""
- Route ID: {route['route_id']}
  Duration: {route['duration_minutes']} minutes
  Distance: {distance_km:.1f} km
  Transit Modes: {', '.join(route['transit_modes']) if route['transit_modes'] else 'None'}
  Transfers: {route['transfers']}
  Walking Distance: {walking_distance_km:.1f} km
  Estimated Cost: {cost_lkr:.0f} LKR
  Steps: {route['steps_count']}
  Category: {route['category']}
""")
        return "\n".join(formatted)
    
    def _format_preferences_for_prompt(self, preferences: Dict) -> str:
        """Format user preferences for the prompt"""
        return f"""
- Preferred Transit Modes: {', '.join(preferences['preferred_transit_modes'])}
- Max Walking Distance: {preferences['max_walking_distance_km']} km
- Budget Preference: {preferences['budget_preference']}
- Time vs Cost Weight: {preferences['time_vs_cost_weight']} (0=prefer cost, 1=prefer time)
- Comfort Preference: {preferences['comfort_preference']} (0=basic, 1=premium)
- Accessibility Needs: {', '.join(preferences['accessibility_needs']) if preferences['accessibility_needs'] else 'None'}
"""
    
    def _process_ai_recommendation(self, response, available_routes: List[Dict]) -> Dict[str, Any]:
        """Process the AI response and extract recommendations"""
        try:
            # Extract text from the response
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                response_text = response.candidates[0].content.parts[0].text.strip()
            else:
                response_text = str(response)
            
            # Try to parse JSON response
            try:
                # Find JSON in the response (in case there's extra text)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    ai_result = json.loads(json_text)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse JSON from AI response: {e}")
                # Fallback: create a basic recommendation
                ai_result = self._create_fallback_recommendation(available_routes, response_text)
            
            # Process the AI result
            return {
                "analysis": ai_result.get("disruption_impact_analysis", {}),
                "recommendations": ai_result.get("route_rankings", []),
                "reasoning": ai_result.get("summary", "AI analysis completed"),
                "confidence": ai_result.get("top_recommendation", {}).get("confidence_score", 50)
            }
            
        except Exception as e:
            print(f"Error processing AI recommendation: {str(e)}")
            # Return fallback recommendation
            return {
                "analysis": {"error": "Failed to process AI response"},
                "recommendations": self._create_fallback_recommendation(available_routes, str(e)),
                "reasoning": f"Fallback analysis due to processing error: {str(e)}",
                "confidence": 30
            }
    
    def _create_fallback_recommendation(self, available_routes: List[Dict], error_context: str) -> List[Dict]:
        """Create a fallback recommendation when AI processing fails"""
        if not available_routes:
            return []
        
        # Simple fallback: rank by duration and cost
        fallback_rankings = []
        for i, route in enumerate(available_routes):
            # Simple scoring: lower duration and cost = higher score
            duration_score = max(0, 100 - (route.get("duration", 60) / 2))  # 2 points per minute
            cost_score = max(0, 100 - (route.get("fare_estimate", 0) / 5))  # 5 points per LKR
            walking_penalty = min(50, route.get("walking_distance", 0) * 20)  # Penalty for walking
            transfer_penalty = route.get("transfers", 0) * 10  # Penalty for transfers
            
            total_score = duration_score + cost_score - walking_penalty - transfer_penalty
            total_score = max(0, min(100, total_score))  # Clamp between 0-100
            
            fallback_rankings.append({
                "route_id": route.get("route_id", f"route_{i}"),
                "rank": i + 1,
                "score": total_score,
                "reasoning": f"Fallback recommendation based on duration and cost analysis",
                "pros": ["Available route", "Basic analysis completed"],
                "cons": ["AI analysis unavailable", "Limited optimization"],
                "estimated_impact_from_disruptions": "unknown"
            })
        
        # Sort by score (highest first)
        fallback_rankings.sort(key=lambda x: x["score"], reverse=True)
        
        # Update ranks
        for i, ranking in enumerate(fallback_rankings):
            ranking["rank"] = i + 1
        
        return fallback_rankings
    
    def get_route_recommendation_summary(self, recommendation_result: Dict[str, Any]) -> str:
        """Generate a user-friendly summary of the recommendation"""
        try:
            if recommendation_result["status"] != "success":
                return f"Unable to provide recommendation: {recommendation_result.get('error', 'Unknown error')}"
            
            recommendations = recommendation_result.get("recommended_routes", [])
            if not recommendations:
                return "No route recommendations available."
            
            top_route = recommendations[0]
            confidence = recommendation_result.get("confidence_score", 0)
            
            summary = f"""
 Disruption Alert: {len(recommendation_result.get('disruption_analysis', {}).get('high_impact_routes', []))} routes affected

 Recommended Route: {top_route.get('route_id', 'Unknown')}
   Confidence: {confidence}%
   Reason: {top_route.get('reasoning', 'No reasoning provided')}

 Key Advantages:
{chr(10).join(f'   • {pro}' for pro in top_route.get('pros', [])[:3])}

 Considerations:
{chr(10).join(f'   • {con}' for con in top_route.get('cons', [])[:2])}
"""
            
            return summary.strip()
            
        except Exception as e:
            return f"Error generating recommendation summary: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    # Test the service
    try:
        service = IntelligentDisruptionService()
        print("Intelligent Disruption Service initialized successfully")
        
        # Test with sample data
        test_disruptions = [
            {
                "disruption_id": "dis_001",
                "location": "Colombo Fort",
                "type": "strike",
                "severity": "high",
                "description": "Bus drivers on strike, no services available"
            }
        ]
        
        test_routes = [
            {
                "route_id": "transit_0",
                "duration": 45,
                "distance": 12.5,
                "transit_modes": ["bus"],
                "transfers": 0,
                "walking_distance": 0.3,
                "fare_estimate": 150,
                "steps": [],
                "category": "transit"
            },
            {
                "route_id": "transit_1",
                "duration": 60,
                "distance": 15.0,
                "transit_modes": ["train"],
                "transfers": 1,
                "walking_distance": 0.8,
                "fare_estimate": 200,
                "steps": [],
                "category": "transit"
            }
        ]
        
        test_preferences = {
            "preferred_transit_modes": ["bus", "train"],
            "max_walking_distance_km": 1.0,
            "budget_preference": "medium",
            "time_vs_cost_weight": 0.6,
            "comfort_preference": 0.7,
            "accessibility_needs": []
        }
        
        result = service.analyze_disruption_and_recommend_routes(
            test_disruptions,
            test_routes,
            test_preferences,
            "Colombo",
            "Kandy"
        )
        
        print("\n Analysis Result:")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Confidence: {result['confidence_score']}%")
            print(f"Recommendations: {len(result['recommended_routes'])} routes")
            
            summary = service.get_route_recommendation_summary(result)
            print(f"\nSummary:\n{summary}")
        
    except Exception as e:
        print(f" Error testing Intelligent Disruption Service: {str(e)}")
