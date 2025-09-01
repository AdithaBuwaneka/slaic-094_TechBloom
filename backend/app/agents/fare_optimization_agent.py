from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.database import db
from app.models.transport import TransportMode, FareStructure
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class FareOptimization(BaseModel):
    """Optimized fare recommendations with cost breakdown."""
    cheapest_route: str = Field(description="The most cost-effective route option")
    total_cost: float = Field(description="Total estimated cost in LKR")
    cost_breakdown: List[str] = Field(description="Detailed breakdown of costs")
    savings_opportunities: List[str] = Field(description="Available discounts and savings")
    payment_methods: List[str] = Field(description="Recommended payment methods")
    pass_recommendations: List[str] = Field(description="Travel pass recommendations if applicable")
    alternative_options: List[Dict] = Field(description="Alternative cost options")

class FareOptimizationAgent:
    """
    Agent that identifies the lowest-cost travel combinations, including 
    passes, discounts, and offers for Sri Lankan public transport.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Sri Lankan fare structures and discount schemes
        self.fare_structures = {
            "sltb_bus": {
                "base_fare": 15.0,
                "per_km": 2.5,
                "ac_surcharge": 50.0,
                "express_surcharge": 25.0
            },
            "private_bus": {
                "base_fare": 20.0,
                "per_km": 3.0,
                "ac_surcharge": 75.0
            },
            "train": {
                "third_class": {"base": 10.0, "per_km": 1.5},
                "second_class": {"base": 20.0, "per_km": 2.5},
                "first_class": {"base": 40.0, "per_km": 4.0},
                "observation_car": {"base": 100.0, "per_km": 8.0}
            }
        }
        
        self.discounts = {
            "student": 0.5,  # 50% discount
            "senior": 0.5,   # 50% discount for 65+
            "disabled": 0.5, # 50% discount
            "child": 0.5,    # 50% discount for under 12
            "group": 0.1     # 10% discount for groups of 10+
        }
        
        prompt_template = """You are a fare optimization expert for Sri Lanka's public transport system.
        
        Calculate the most cost-effective travel options for this journey:
        
        Journey Details:
        Origin: {origin}
        Destination: {destination}
        Distance: {distance_km} km
        Travel Date: {travel_date}
        Passenger Type: {passenger_type}
        
        Available Routes:
        {available_routes}
        
        User Preferences:
        Budget: {budget_preference}
        Comfort Level: {comfort_preference}
        Travel Frequency: {travel_frequency}
        
        Consider:
        1. Sri Lankan transport fare structures
        2. Available discounts (student, senior, disabled, group)
        3. Travel passes for frequent travelers
        4. Seasonal offers and promotions
        5. Multi-modal journey cost optimization
        6. Time-based fare variations
        
        Provide detailed cost analysis and money-saving recommendations.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        self.structured_llm = prompt | self.llm.with_structured_output(FareOptimization)
    
    async def optimize_fare(
        self,
        origin: str,
        destination: str, 
        available_routes: List[Dict],
        passenger_type: str = "adult",
        budget_preference: Optional[float] = None,
        comfort_preference: str = "standard",
        travel_frequency: str = "occasional"
    ) -> FareOptimization:
        """
        Calculate optimized fare recommendations for the given journey.
        """
        try:
            # Calculate distance (mock calculation)
            distance_km = await self._estimate_distance(origin, destination)
            
            # Calculate fares for all available routes
            route_costs = []
            for route in available_routes:
                cost = await self._calculate_route_cost(route, distance_km, passenger_type)
                route_costs.append({
                    "route": route,
                    "cost": cost
                })
            
            # Get fare optimization recommendations
            optimization = await self.structured_llm.ainvoke({
                "origin": origin,
                "destination": destination,
                "distance_km": distance_km,
                "travel_date": datetime.now().strftime("%Y-%m-%d"),
                "passenger_type": passenger_type,
                "available_routes": route_costs,
                "budget_preference": budget_preference or "flexible",
                "comfort_preference": comfort_preference,
                "travel_frequency": travel_frequency
            })
            
            return optimization
            
        except Exception as e:
            print(f"Error in fare optimization: {e}")
            return FareOptimization(
                cheapest_route="Standard bus route",
                total_cost=100.0,
                cost_breakdown=["Base fare: LKR 100"],
                savings_opportunities=["Student discount available"],
                payment_methods=["Cash", "QR code"],
                pass_recommendations=["Consider monthly pass for frequent travel"],
                alternative_options=[]
            )
    
    async def _calculate_route_cost(self, route: Dict, distance_km: float, passenger_type: str) -> Dict:
        """
        Calculate the cost for a specific route.
        """
        try:
            transport_mode = route.get("transport_mode", "bus").lower()
            base_cost = 0
            
            if transport_mode == "bus":
                operator = route.get("operator", "sltb").lower()
                if "sltb" in operator:
                    structure = self.fare_structures["sltb_bus"]
                else:
                    structure = self.fare_structures["private_bus"]
                
                base_cost = structure["base_fare"] + (distance_km * structure["per_km"])
                
                # Add surcharges
                if route.get("ac_bus", False):
                    base_cost += structure.get("ac_surcharge", 0)
                if route.get("express", False):
                    base_cost += structure.get("express_surcharge", 0)
            
            elif transport_mode == "train":
                class_type = route.get("class", "third_class")
                structure = self.fare_structures["train"].get(class_type, self.fare_structures["train"]["third_class"])
                base_cost = structure["base"] + (distance_km * structure["per_km"])
            
            # Apply discounts
            discount_multiplier = 1.0
            if passenger_type in self.discounts:
                discount_multiplier = 1.0 - self.discounts[passenger_type]
            
            final_cost = base_cost * discount_multiplier
            
            return {
                "base_cost": round(base_cost, 2),
                "discount_applied": self.discounts.get(passenger_type, 0),
                "final_cost": round(final_cost, 2),
                "currency": "LKR"
            }
            
        except Exception as e:
            print(f"Error calculating route cost: {e}")
            return {"base_cost": 100.0, "final_cost": 100.0, "currency": "LKR"}
    
    async def _estimate_distance(self, origin: str, destination: str) -> float:
        """
        Estimate distance between origin and destination.
        """
        # Mock distance calculation based on common Sri Lankan routes
        route_distances = {
            ("colombo", "kandy"): 115.0,
            ("colombo", "galle"): 119.0,
            ("kandy", "nuwara eliya"): 65.0,
            ("colombo", "negombo"): 37.0,
            ("colombo", "mount lavinia"): 12.0,
            ("kandy", "matale"): 26.0,
            ("galle", "matara"): 32.0
        }
        
        origin_key = origin.lower()
        destination_key = destination.lower()
        
        # Check both directions
        for (o, d), distance in route_distances.items():
            if (o in origin_key and d in destination_key) or (d in origin_key and o in destination_key):
                return distance
        
        # Default estimate based on rough calculation
        return 50.0
    
    async def get_travel_passes(self, user_profile: Dict) -> List[Dict]:
        """
        Recommend travel passes based on user's travel patterns.
        """
        try:
            passes = []
            
            # Monthly bus passes
            if user_profile.get("frequent_transport", []).get("bus", 0) > 15:
                passes.append({
                    "type": "Monthly Bus Pass",
                    "cost": 2500.0,
                    "validity": "30 days",
                    "coverage": "All SLTB routes",
                    "savings": "Up to 40% for daily commuters"
                })
            
            # Train season tickets
            if user_profile.get("frequent_routes", []):
                for route in user_profile["frequent_routes"]:
                    if "train" in route.lower():
                        passes.append({
                            "type": "Train Season Ticket",
                            "cost": 1800.0,
                            "validity": "30 days",
                            "coverage": f"Specific route: {route}",
                            "savings": "Up to 50% for regular travelers"
                        })
            
            # Student passes
            if user_profile.get("passenger_type") == "student":
                passes.append({
                    "type": "Student Travel Pass",
                    "cost": 1500.0,
                    "validity": "30 days", 
                    "coverage": "All public transport",
                    "savings": "Additional 25% off student discounts"
                })
            
            return passes
            
        except Exception as e:
            print(f"Error getting travel passes: {e}")
            return []
    
    async def check_promotional_offers(self) -> List[Dict]:
        """
        Check for current promotional offers and discounts.
        """
        try:
            # This would typically query a promotions database
            current_offers = [
                {
                    "title": "Festival Season Discount",
                    "description": "20% off all train tickets during Vesak season",
                    "valid_until": "2024-05-15",
                    "transport_modes": ["train"],
                    "discount_percentage": 20
                },
                {
                    "title": "Weekend Family Pass",
                    "description": "Family groups of 4+ get 15% discount on weekends",
                    "valid_until": "2024-12-31",
                    "transport_modes": ["bus", "train"],
                    "discount_percentage": 15,
                    "conditions": ["weekend", "family_group"]
                },
                {
                    "title": "Digital Payment Bonus",
                    "description": "5% cashback for QR code payments",
                    "valid_until": "2024-12-31", 
                    "transport_modes": ["bus"],
                    "discount_percentage": 5,
                    "conditions": ["digital_payment"]
                }
            ]
            
            # Filter active offers
            current_date = datetime.now()
            active_offers = []
            for offer in current_offers:
                valid_until = datetime.strptime(offer["valid_until"], "%Y-%m-%d")
                if valid_until > current_date:
                    active_offers.append(offer)
            
            return active_offers
            
        except Exception as e:
            print(f"Error checking promotional offers: {e}")
            return []
    
    async def calculate_group_discounts(self, group_size: int, route_cost: float) -> Dict:
        """
        Calculate discounts for group travel.
        """
        try:
            if group_size < 10:
                return {
                    "discount_applicable": False,
                    "individual_cost": route_cost,
                    "total_cost": route_cost * group_size,
                    "savings": 0
                }
            
            # Group discount of 10% for groups of 10+
            discount_rate = 0.1
            if group_size >= 20:
                discount_rate = 0.15  # 15% for larger groups
            
            discounted_cost = route_cost * (1 - discount_rate)
            total_cost = discounted_cost * group_size
            savings = (route_cost * group_size) - total_cost
            
            return {
                "discount_applicable": True,
                "discount_rate": discount_rate * 100,
                "individual_cost": round(discounted_cost, 2),
                "total_cost": round(total_cost, 2),
                "savings": round(savings, 2),
                "group_size": group_size
            }
            
        except Exception as e:
            print(f"Error calculating group discounts: {e}")
            return {"discount_applicable": False, "individual_cost": route_cost}
    
    async def get_payment_method_benefits(self) -> Dict[str, Dict]:
        """
        Get benefits associated with different payment methods.
        """
        return {
            "cash": {
                "advantages": ["Widely accepted", "No technology dependency"],
                "disadvantages": ["No discounts", "Need exact change"],
                "discount": 0
            },
            "qr_payment": {
                "advantages": ["5% cashback", "Contactless", "Transaction history"],
                "disadvantages": ["Requires smartphone", "Internet dependency"],
                "discount": 5
            },
            "travel_card": {
                "advantages": ["10% discount", "Faster boarding", "Auto-recharge"],
                "disadvantages": ["Initial card cost", "Need to top up"],
                "discount": 10
            },
            "mobile_app": {
                "advantages": ["Pre-booking", "Real-time tracking", "Digital receipts"],
                "disadvantages": ["App dependency", "Internet required"],
                "discount": 3
            }
        }