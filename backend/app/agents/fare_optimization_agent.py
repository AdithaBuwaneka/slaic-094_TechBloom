from app.agents.base_agent import BaseAgent
from app.models.fare_optimization import (
    FareRule, Discount, FareCalculation, GroupBooking, SeasonPass, 
    FareOptimizationResult, CostBreakdown, FarePrediction, BulkPurchaseOption,
    DiscountType, PaymentMethod
)
from app.models.transport_data import Location, TransportMode
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import math
from datetime import datetime, timedelta, date
import random
from decimal import Decimal


class FareOptimizationAgent(BaseAgent):
    """
    Fare Optimization Agent - Cost-Effective Travel Planning
    
    Primary Functions:
    - Granular fare calculation across modes
    - Discount eligibility assessment
    - Hidden cost identification (parking, transfers)
    - Monthly and annual savings projections
    - Lowest-cost route identification
    - Bulk purchase recommendations
    - Student and group discount applications
    - Dynamic pricing consideration
    """
    
    def __init__(self):
        super().__init__(
            agent_id="fare_optimization_agent",
            name="Fare Optimization Agent",
            priority_weight=0.6  # Important for cost-conscious users
        )
        
        # Mock fare rules database (in production would be from external APIs)
        self.fare_rules = self._initialize_fare_rules()
        self.discounts = self._initialize_discounts()
        self.season_passes = self._initialize_season_passes()
        
        # Sri Lankan transport operators and their pricing
        self.operators = {
            "SLTB": {"base_fare": 15.0, "per_km": 2.5, "booking_fee": 0.0},
            "CTB": {"base_fare": 12.0, "per_km": 2.0, "booking_fee": 0.0},
            "Sri Lanka Railways": {"base_fare": 25.0, "per_km": 1.8, "booking_fee": 5.0},
            "Private Bus": {"base_fare": 20.0, "per_km": 3.0, "booking_fee": 0.0},
            "Three Wheeler": {"base_fare": 50.0, "per_km": 80.0, "booking_fee": 0.0},
            "Uber/PickMe": {"base_fare": 100.0, "per_km": 120.0, "booking_fee": 10.0}
        }
        
    def _initialize_fare_rules(self) -> Dict[str, FareRule]:
        """Initialize fare rules for different transport modes and operators"""
        rules = {}
        
        # Bus fare rules
        rules["sltb_bus"] = FareRule(
            rule_id="sltb_bus_001",
            transport_mode=TransportMode.BUS,
            operator="SLTB",
            base_fare=15.0,
            per_km_rate=2.5,
            peak_hour_multiplier=1.0,
            off_peak_multiplier=0.9,
            weekend_multiplier=1.0,
            valid_from=datetime.utcnow() - timedelta(days=30),
            booking_fee=0.0
        )
        
        # Train fare rules
        rules["railways_train"] = FareRule(
            rule_id="railways_001",
            transport_mode=TransportMode.TRAIN,
            operator="Sri Lanka Railways",
            base_fare=25.0,
            per_km_rate=1.8,
            peak_hour_multiplier=1.0,
            off_peak_multiplier=0.8,
            weekend_multiplier=0.9,
            valid_from=datetime.utcnow() - timedelta(days=60),
            booking_fee=5.0
        )
        
        # Private bus rules
        rules["private_bus"] = FareRule(
            rule_id="pvt_bus_001",
            transport_mode=TransportMode.BUS,
            operator="Private Bus",
            base_fare=20.0,
            per_km_rate=3.0,
            peak_hour_multiplier=1.2,
            off_peak_multiplier=1.0,
            weekend_multiplier=1.1,
            valid_from=datetime.utcnow() - timedelta(days=15),
            booking_fee=0.0
        )
        
        return rules
        
    def _initialize_discounts(self) -> Dict[str, Discount]:
        """Initialize available discounts"""
        discounts = {}
        
        # Student discount
        discounts["student_discount"] = Discount(
            discount_id="student_001",
            discount_type=DiscountType.STUDENT,
            name="Student Discount",
            description="50% discount for students with valid ID",
            percentage_off=0.5,
            max_age=25,
            required_documents=["student_id", "university_card"],
            transport_modes=[TransportMode.BUS, TransportMode.TRAIN],
            auto_apply=False,
            stackable=False
        )
        
        # Senior citizen discount
        discounts["senior_discount"] = Discount(
            discount_id="senior_001",
            discount_type=DiscountType.SENIOR,
            name="Senior Citizen Discount",
            description="30% discount for senior citizens (60+)",
            percentage_off=0.3,
            min_age=60,
            required_documents=["national_id"],
            transport_modes=[TransportMode.BUS, TransportMode.TRAIN],
            auto_apply=True,
            stackable=True
        )
        
        # Group discount
        discounts["group_discount"] = Discount(
            discount_id="group_001",
            discount_type=DiscountType.GROUP,
            name="Group Discount",
            description="20% discount for groups of 10 or more",
            percentage_off=0.2,
            min_group_size=10,
            transport_modes=[TransportMode.BUS, TransportMode.TRAIN],
            requires_registration=True,
            stackable=False
        )
        
        # Off-peak discount
        discounts["off_peak"] = Discount(
            discount_id="off_peak_001",
            discount_type=DiscountType.OFF_PEAK,
            name="Off-Peak Discount",
            description="15% discount during off-peak hours",
            percentage_off=0.15,
            valid_hours=["10:00-16:00", "20:00-06:00"],
            transport_modes=[TransportMode.TRAIN],
            auto_apply=True,
            stackable=True
        )
        
        return discounts
        
    def _initialize_season_passes(self) -> Dict[str, SeasonPass]:
        """Initialize season pass options"""
        passes = {}
        
        # Monthly bus pass
        passes["monthly_bus"] = SeasonPass(
            pass_id="monthly_bus_001",
            pass_name="Monthly Bus Pass",
            pass_type="monthly",
            transport_modes=[TransportMode.BUS],
            zones=["colombo", "western_province"],
            pass_price=2500.0,
            equivalent_individual_trips=60,
            individual_trip_cost=50.0,
            break_even_trips=50,
            potential_savings=500.0,
            savings_percentage=16.7,
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=30),
            validity_days=30
        )
        
        # Annual train pass
        passes["annual_train"] = SeasonPass(
            pass_id="annual_train_001",
            pass_name="Annual Train Pass",
            pass_type="annual",
            transport_modes=[TransportMode.TRAIN],
            zones=["national"],
            pass_price=15000.0,
            equivalent_individual_trips=400,
            individual_trip_cost=60.0,
            break_even_trips=250,
            potential_savings=9000.0,
            savings_percentage=37.5,
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=365),
            validity_days=365
        )
        
        return passes
        
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for fare optimization requests"""
        
        request_type = payload.get("request_type", "")
        data = payload.get("data", {})
        
        if request_type == "calculate_fare":
            return await self._calculate_fare(data)
        elif request_type == "optimize_fare":
            return await self._optimize_fare(data)
        elif request_type == "find_discounts":
            return await self._find_applicable_discounts(data)
        elif request_type == "analyze_season_passes":
            return await self._analyze_season_passes(data)
        elif request_type == "group_booking_analysis":
            return await self._analyze_group_booking(data)
        elif request_type == "bulk_purchase_options":
            return await self._analyze_bulk_purchase_options(data)
        elif request_type == "payment_optimization":
            return await self._optimize_payment_methods(data)
        elif request_type == "fare_prediction":
            return await self._predict_fare_trends(data)
        else:
            return {
                "status": "unknown_request",
                "message": f"Unknown request type: {request_type}",
                "supported_requests": [
                    "calculate_fare", "optimize_fare", "find_discounts",
                    "analyze_season_passes", "group_booking_analysis",
                    "bulk_purchase_options", "payment_optimization", "fare_prediction"
                ]
            }
            
    async def _calculate_fare(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed fare for a specific route"""
        
        try:
            # Extract route details
            transport_mode = TransportMode(data.get("transport_mode", "bus"))
            operator = data.get("operator", "SLTB")
            distance_km = data.get("distance_km", 10.0)
            departure_time = datetime.fromisoformat(data.get("departure_time", datetime.utcnow().isoformat()))
            
            # Get fare rule
            rule_key = f"{operator.lower().replace(' ', '_')}_{transport_mode.value}"
            if rule_key not in self.fare_rules:
                rule_key = list(self.fare_rules.keys())[0]  # Default rule
                
            fare_rule = self.fare_rules[rule_key]
            
            # Calculate base components
            base_fare = fare_rule.base_fare
            distance_charge = distance_km * fare_rule.per_km_rate if fare_rule.per_km_rate else 0.0
            
            # Time-based multipliers
            hour = departure_time.hour
            multiplier = 1.0
            if hour in [7, 8, 17, 18]:  # Peak hours
                multiplier = fare_rule.peak_hour_multiplier
            elif hour < 6 or hour > 22:  # Night
                multiplier = fare_rule.night_multiplier
            else:  # Off-peak
                multiplier = fare_rule.off_peak_multiplier
                
            # Weekend multiplier
            if departure_time.weekday() >= 5:  # Saturday/Sunday
                multiplier *= fare_rule.weekend_multiplier
                
            # Calculate subtotal
            subtotal = (base_fare + distance_charge) * multiplier
            
            # Add fees
            booking_fee = fare_rule.booking_fee
            service_charge = subtotal * 0.02  # 2% service charge
            taxes = subtotal * 0.05  # 5% tax
            
            # Create fare calculation
            calculation = FareCalculation(
                calculation_id=f"fare_calc_{datetime.utcnow().isoformat()}",
                route_id=data.get("route_id", "unknown"),
                transport_mode=transport_mode,
                operator=operator,
                origin=Location(**data["origin"]) if "origin" in data else Location(latitude=0, longitude=0),
                destination=Location(**data["destination"]) if "destination" in data else Location(latitude=0, longitude=0),
                distance_km=distance_km,
                duration_minutes=int(distance_km / 30 * 60),  # Assume 30 kmh average
                departure_time=departure_time,
                base_fare=base_fare,
                distance_charge=distance_charge,
                booking_fee=booking_fee,
                service_charge=service_charge,
                taxes=taxes,
                subtotal=subtotal + booking_fee + service_charge + taxes,
                final_fare=subtotal + booking_fee + service_charge + taxes
            )
            
            # Cost breakdown
            breakdown = [
                CostBreakdown(
                    category="base_fare",
                    description="Base fare",
                    amount=base_fare,
                    percentage_of_total=base_fare / calculation.final_fare * 100,
                    calculation_method="fixed"
                ),
                CostBreakdown(
                    category="distance_charge",
                    description=f"Distance charge ({distance_km:.1f} km)",
                    amount=distance_charge,
                    percentage_of_total=distance_charge / calculation.final_fare * 100,
                    calculation_method="per_km",
                    rate=fare_rule.per_km_rate,
                    quantity=distance_km
                ),
                CostBreakdown(
                    category="fees",
                    description="Service charges and taxes",
                    amount=booking_fee + service_charge + taxes,
                    percentage_of_total=(booking_fee + service_charge + taxes) / calculation.final_fare * 100,
                    calculation_method="percentage"
                )
            ]
            
            return {
                "status": "success",
                "fare_calculation": calculation.dict(),
                "cost_breakdown": [b.dict() for b in breakdown],
                "multipliers_applied": {
                    "time_multiplier": multiplier,
                    "peak_hour": hour in [7, 8, 17, 18],
                    "weekend": departure_time.weekday() >= 5
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fare calculation failed: {str(e)}"
            }
            
    async def _optimize_fare(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize fare across all available options"""
        
        try:
            # Extract user preferences
            user_id = data.get("user_id")
            origin = Location(**data["origin"])
            destination = Location(**data["destination"])
            travel_date = datetime.fromisoformat(data.get("travel_date", datetime.utcnow().isoformat()))
            group_size = data.get("group_size", 1)
            user_profile = data.get("user_profile", {})
            
            # Calculate distance
            distance_km = self._calculate_distance(origin, destination)
            
            # Calculate fares for all transport modes
            all_fare_options = []
            
            for mode in [TransportMode.BUS, TransportMode.TRAIN]:
                for operator in ["SLTB", "Sri Lanka Railways", "Private Bus"]:
                    if (mode == TransportMode.TRAIN and "Railways" not in operator) or \
                       (mode == TransportMode.BUS and "Railways" in operator):
                        continue
                        
                    fare_calc = await self._calculate_single_fare(
                        mode, operator, distance_km, travel_date, origin, destination
                    )
                    if fare_calc:
                        all_fare_options.append(fare_calc)
                        
            # Find cheapest and best value options
            cheapest = min(all_fare_options, key=lambda x: x.final_fare) if all_fare_options else None
            
            # Best value = lowest cost per comfort point
            best_value = None
            if all_fare_options:
                comfort_scores = {
                    TransportMode.TRAIN: 0.8,
                    TransportMode.BUS: 0.6,
                    TransportMode.WALKING: 0.3,
                    TransportMode.TAXI: 0.9
                }
                best_value = min(all_fare_options, 
                               key=lambda x: x.final_fare / comfort_scores.get(x.transport_mode, 0.5))
                
            # Apply discounts
            available_discounts = await self._get_applicable_discounts(user_profile, travel_date, group_size)
            
            # Apply discounts to cheapest option
            if cheapest and available_discounts:
                cheapest = await self._apply_discounts(cheapest, available_discounts[:1])  # Apply best discount
                
            # Season pass analysis
            season_pass_recs = await self._get_season_pass_recommendations(user_profile, distance_km)
            
            # Group booking analysis
            group_analysis = None
            if group_size > 1:
                group_analysis = await self._calculate_group_booking(cheapest, group_size)
                
            # Create optimization result
            result = FareOptimizationResult(
                optimization_id=f"opt_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                origin=origin,
                destination=destination,
                travel_date=travel_date,
                group_size=group_size,
                user_profile=user_profile,
                all_fare_options=all_fare_options,
                cheapest_option=cheapest,
                best_value_option=best_value,
                recommended_option=best_value or cheapest,
                available_discounts=available_discounts,
                season_pass_recommendations=season_pass_recs,
                group_booking_analysis=group_analysis,
                total_potential_savings=self._calculate_potential_savings(cheapest, available_discounts),
                savings_opportunities=self._generate_savings_opportunities(cheapest, available_discounts, season_pass_recs)
            )
            
            return {
                "status": "success",
                "optimization_result": result.dict(),
                "summary": {
                    "cheapest_fare": cheapest.final_fare if cheapest else 0,
                    "total_options": len(all_fare_options),
                    "discounts_available": len(available_discounts),
                    "potential_savings": result.total_potential_savings
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fare optimization failed: {str(e)}"
            }
            
    async def _calculate_single_fare(self, mode: TransportMode, operator: str, 
                                   distance_km: float, departure_time: datetime,
                                   origin: Location, destination: Location) -> Optional[FareCalculation]:
        """Calculate fare for a single transport option"""
        
        try:
            operator_info = self.operators.get(operator, self.operators["SLTB"])
            
            base_fare = operator_info["base_fare"]
            distance_charge = distance_km * operator_info["per_km"]
            booking_fee = operator_info["booking_fee"]
            
            subtotal = base_fare + distance_charge + booking_fee
            taxes = subtotal * 0.05
            final_fare = subtotal + taxes
            
            return FareCalculation(
                calculation_id=f"calc_{mode.value}_{operator}_{datetime.utcnow().isoformat()}",
                route_id=f"{origin.latitude},{origin.longitude}_to_{destination.latitude},{destination.longitude}",
                transport_mode=mode,
                operator=operator,
                origin=origin,
                destination=destination,
                distance_km=distance_km,
                duration_minutes=int(distance_km / 25 * 60),  # 25 kmh average
                departure_time=departure_time,
                base_fare=base_fare,
                distance_charge=distance_charge,
                booking_fee=booking_fee,
                taxes=taxes,
                subtotal=subtotal,
                final_fare=final_fare
            )
            
        except Exception as e:
            return None
            
    async def _find_applicable_discounts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find discounts applicable to user and journey"""
        
        try:
            user_profile = data.get("user_profile", {})
            travel_date = datetime.fromisoformat(data.get("travel_date", datetime.utcnow().isoformat()))
            group_size = data.get("group_size", 1)
            transport_modes = data.get("transport_modes", ["bus", "train"])
            
            applicable_discounts = await self._get_applicable_discounts(user_profile, travel_date, group_size)
            
            # Filter by transport modes
            filtered_discounts = []
            for discount in applicable_discounts:
                if not discount.transport_modes or any(TransportMode(mode) in discount.transport_modes for mode in transport_modes):
                    filtered_discounts.append(discount)
                    
            # Calculate potential savings for each discount
            discount_analysis = []
            base_fare = 100.0  # Example base fare
            
            for discount in filtered_discounts:
                savings = 0.0
                if discount.percentage_off:
                    savings = base_fare * discount.percentage_off
                elif discount.fixed_amount_off:
                    savings = discount.fixed_amount_off
                    
                discount_analysis.append({
                    "discount": discount.dict(),
                    "potential_savings": savings,
                    "requirements": self._get_discount_requirements(discount),
                    "how_to_apply": self._get_application_instructions(discount)
                })
                
            return {
                "status": "success",
                "applicable_discounts": len(filtered_discounts),
                "discount_analysis": discount_analysis,
                "total_potential_savings": sum(d["potential_savings"] for d in discount_analysis),
                "recommendations": [
                    "Apply student discount if eligible",
                    "Travel during off-peak hours for additional savings",
                    "Consider group booking for larger parties"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Discount analysis failed: {str(e)}"
            }
            
    async def _analyze_season_passes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze season pass options and ROI"""
        
        try:
            user_profile = data.get("user_profile", {})
            monthly_trips = data.get("estimated_monthly_trips", 20)
            typical_trip_cost = data.get("typical_trip_cost", 50.0)
            
            season_pass_analysis = []
            
            for pass_id, season_pass in self.season_passes.items():
                # Calculate ROI
                monthly_individual_cost = monthly_trips * typical_trip_cost
                monthly_pass_cost = season_pass.pass_price if season_pass.pass_type == "monthly" else season_pass.pass_price / 12
                
                monthly_savings = monthly_individual_cost - monthly_pass_cost
                roi_percentage = (monthly_savings / monthly_pass_cost) * 100 if monthly_pass_cost > 0 else 0
                
                recommendation = "recommended" if monthly_savings > 0 else "not_recommended"
                if monthly_trips < season_pass.break_even_trips / (12 if season_pass.pass_type == "annual" else 1):
                    recommendation = "not_recommended"
                    
                analysis = {
                    "season_pass": season_pass.dict(),
                    "roi_analysis": {
                        "monthly_individual_cost": monthly_individual_cost,
                        "monthly_pass_cost": monthly_pass_cost,
                        "monthly_savings": monthly_savings,
                        "roi_percentage": roi_percentage,
                        "break_even_trips_per_month": season_pass.break_even_trips / (12 if season_pass.pass_type == "annual" else 1),
                        "recommendation": recommendation
                    }
                }
                season_pass_analysis.append(analysis)
                
            # Sort by savings potential
            season_pass_analysis.sort(key=lambda x: x["roi_analysis"]["monthly_savings"], reverse=True)
            
            return {
                "status": "success",
                "season_pass_analysis": season_pass_analysis,
                "best_option": season_pass_analysis[0] if season_pass_analysis else None,
                "summary": {
                    "total_options": len(season_pass_analysis),
                    "recommended_passes": len([a for a in season_pass_analysis if a["roi_analysis"]["recommendation"] == "recommended"]),
                    "max_monthly_savings": max([a["roi_analysis"]["monthly_savings"] for a in season_pass_analysis], default=0)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Season pass analysis failed: {str(e)}"
            }
            
    async def _analyze_group_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze group booking options and savings"""
        
        try:
            group_size = data.get("group_size", 1)
            individual_fare = data.get("individual_fare", 100.0)
            group_type = data.get("group_type", "general")
            
            if group_size <= 1:
                return {
                    "status": "not_applicable",
                    "message": "Group booking requires 2 or more people"
                }
                
            # Calculate group discounts based on size
            group_discount_percentage = 0.0
            if group_size >= 20:
                group_discount_percentage = 0.25  # 25% for 20+
            elif group_size >= 10:
                group_discount_percentage = 0.20  # 20% for 10-19
            elif group_size >= 5:
                group_discount_percentage = 0.10  # 10% for 5-9
            elif group_size >= 2:
                group_discount_percentage = 0.05  # 5% for 2-4
                
            # Additional discounts for specific group types
            if group_type == "student":
                group_discount_percentage += 0.10
            elif group_type == "corporate":
                group_discount_percentage += 0.05
                
            total_individual_cost = group_size * individual_fare
            group_discount_amount = total_individual_cost * group_discount_percentage
            group_fare_total = total_individual_cost - group_discount_amount
            
            # Buy X get Y free for large groups
            free_seats = 0
            if group_size >= 10:
                free_seats = group_size // 10  # 1 free for every 10
                
            group_booking = GroupBooking(
                group_id=f"group_{datetime.utcnow().isoformat()}",
                group_size=group_size,
                group_type=group_type,
                individual_fare_per_person=individual_fare,
                group_discount_percentage=group_discount_percentage,
                group_discount_amount=group_discount_amount,
                total_individual_cost=total_individual_cost,
                group_fare_total=group_fare_total,
                total_savings=group_discount_amount + (free_seats * individual_fare),
                free_seats=free_seats,
                additional_services=["group_seating", "priority_boarding"] if group_size >= 10 else []
            )
            
            return {
                "status": "success",
                "group_booking": group_booking.dict(),
                "savings_summary": {
                    "discount_savings": group_discount_amount,
                    "free_seat_savings": free_seats * individual_fare,
                    "total_savings": group_booking.total_savings,
                    "savings_per_person": group_booking.total_savings / group_size,
                    "final_cost_per_person": group_booking.group_fare_total / group_size
                },
                "recommendations": [
                    f"Group booking saves Rs.{group_booking.total_savings:.0f} total",
                    f"Each person saves Rs.{group_booking.total_savings / group_size:.0f}",
                    "Book in advance for better group rates"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Group booking analysis failed: {str(e)}"
            }
            
    async def _analyze_bulk_purchase_options(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze bulk purchase and prepaid options"""
        
        try:
            typical_trip_cost = data.get("typical_trip_cost", 50.0)
            monthly_trips = data.get("monthly_trips", 20)
            user_profile = data.get("user_profile", {})
            
            bulk_options = []
            
            # 10-trip package
            option_10 = BulkPurchaseOption(
                option_id="bulk_10",
                option_name="10-Trip Package",
                option_type="bulk_tickets",
                number_of_trips=10,
                individual_trip_cost=typical_trip_cost,
                bulk_price=typical_trip_cost * 10 * 0.95,  # 5% discount
                discount_per_trip=typical_trip_cost * 0.05,
                total_savings=typical_trip_cost * 10 * 0.05,
                savings_percentage=5.0,
                valid_for_days=90,
                transferable=False,
                refundable=True,
                break_even_usage=10,
                recommended_for_frequency="weekly",
                risk_assessment="low"
            )
            bulk_options.append(option_10)
            
            # 30-trip package
            option_30 = BulkPurchaseOption(
                option_id="bulk_30",
                option_name="30-Trip Package",
                option_type="bulk_tickets",
                number_of_trips=30,
                individual_trip_cost=typical_trip_cost,
                bulk_price=typical_trip_cost * 30 * 0.85,  # 15% discount
                discount_per_trip=typical_trip_cost * 0.15,
                total_savings=typical_trip_cost * 30 * 0.15,
                savings_percentage=15.0,
                valid_for_days=180,
                transferable=True,
                refundable=True,
                break_even_usage=30,
                recommended_for_frequency="daily",
                risk_assessment="low",
                bonus_features=["priority_booking", "flexible_dates"]
            )
            bulk_options.append(option_30)
            
            # Prepaid balance option
            prepaid_balance = BulkPurchaseOption(
                option_id="prepaid_balance",
                option_name="Prepaid Travel Balance",
                option_type="prepaid_balance",
                number_of_trips=0,  # Variable
                individual_trip_cost=typical_trip_cost,
                bulk_price=5000.0,  # Rs. 5000 balance
                discount_per_trip=0.0,
                total_savings=500.0,  # 10% bonus credit
                savings_percentage=10.0,
                valid_for_days=365,
                transferable=False,
                refundable=True,
                break_even_usage=0,
                recommended_for_frequency="occasional",
                risk_assessment="medium",
                bonus_features=["no_expiry", "auto_top_up", "multiple_modes"]
            )
            bulk_options.append(prepaid_balance)
            
            # Analyze which options suit the user
            recommendations = []
            for option in bulk_options:
                if monthly_trips >= option.number_of_trips and option.number_of_trips > 0:
                    recommendations.append(option)
                elif option.option_type == "prepaid_balance":
                    recommendations.append(option)
                    
            return {
                "status": "success",
                "bulk_options": [opt.dict() for opt in bulk_options],
                "recommendations": [opt.dict() for opt in recommendations],
                "analysis": {
                    "best_savings": max([opt.savings_percentage for opt in bulk_options]),
                    "suitable_options": len(recommendations),
                    "monthly_usage": monthly_trips,
                    "advice": [
                        "Bulk purchases offer 5-15% savings",
                        "Consider your travel frequency before buying",
                        "Prepaid balance offers flexibility across modes"
                    ]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Bulk purchase analysis failed: {str(e)}"
            }
            
    async def _optimize_payment_methods(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize payment methods for additional savings"""
        
        try:
            total_fare = data.get("total_fare", 100.0)
            
            payment_methods = [
                {
                    "method": "Digital Wallet",
                    "discount_percentage": 2.0,
                    "discount_amount": total_fare * 0.02,
                    "convenience_fee": 0.0,
                    "net_savings": total_fare * 0.02,
                    "benefits": ["Cashback", "Quick payment", "Transaction history"]
                },
                {
                    "method": "Bank Card",
                    "discount_percentage": 1.0,
                    "discount_amount": total_fare * 0.01,
                    "convenience_fee": 5.0,
                    "net_savings": total_fare * 0.01 - 5.0,
                    "benefits": ["Secure", "Widely accepted"]
                },
                {
                    "method": "Cash",
                    "discount_percentage": 0.0,
                    "discount_amount": 0.0,
                    "convenience_fee": 0.0,
                    "net_savings": 0.0,
                    "benefits": ["No fees", "Universal acceptance"]
                },
                {
                    "method": "Corporate Account",
                    "discount_percentage": 5.0,
                    "discount_amount": total_fare * 0.05,
                    "convenience_fee": 0.0,
                    "net_savings": total_fare * 0.05,
                    "benefits": ["Bulk discounts", "Automated billing", "Tax benefits"],
                    "requirements": ["Corporate registration"]
                }
            ]
            
            # Sort by net savings
            payment_methods.sort(key=lambda x: x["net_savings"], reverse=True)
            
            return {
                "status": "success",
                "payment_methods": payment_methods,
                "best_option": payment_methods[0],
                "total_potential_savings": max([pm["net_savings"] for pm in payment_methods]),
                "recommendations": [
                    "Use digital wallet for 2% cashback",
                    "Avoid bank cards for small amounts due to fees",
                    "Corporate accounts offer the best discounts"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Payment method optimization failed: {str(e)}"
            }
            
    async def _predict_fare_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict fare trends and optimal booking times"""
        
        try:
            route_id = data.get("route_id", "unknown")
            current_fare = data.get("current_fare", 100.0)
            
            # Mock prediction (in real implementation would use ML models)
            seasonal_factor = 0.1 * random.uniform(-1, 1)  # ±10% seasonal variation
            demand_factor = 0.05 * random.uniform(-1, 1)   # ±5% demand variation
            
            prediction = FarePrediction(
                prediction_id=f"pred_{datetime.utcnow().isoformat()}",
                route_id=route_id,
                current_fare=current_fare,
                predicted_fare_1_week=current_fare * (1 + seasonal_factor * 0.1),
                predicted_fare_1_month=current_fare * (1 + seasonal_factor * 0.3),
                predicted_fare_3_months=current_fare * (1 + seasonal_factor + demand_factor),
                price_trend="stable" if abs(seasonal_factor) < 0.05 else ("increasing" if seasonal_factor > 0 else "decreasing"),
                confidence_level=0.75,
                demand_factors=["Holiday season", "School reopening"] if seasonal_factor > 0.05 else [],
                seasonal_factors=["Peak tourist season"] if seasonal_factor > 0 else ["Off-season"],
                operational_factors=["Fuel price changes"],
                best_time_to_book="immediately" if seasonal_factor > 0 else "wait_1_week",
                price_alerts_recommended=abs(seasonal_factor) > 0.05,
                advance_booking_savings=max(0, -seasonal_factor * current_fare * 0.5)
            )
            
            return {
                "status": "success",
                "fare_prediction": prediction.dict(),
                "recommendations": [
                    "Book now if prices are predicted to increase",
                    "Wait for better rates if trend is decreasing",
                    "Set price alerts for volatile routes"
                ],
                "confidence": prediction.confidence_level
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fare prediction failed: {str(e)}"
            }
            
    def _calculate_distance(self, origin: Location, destination: Location) -> float:
        """Calculate distance between two locations using Haversine formula"""
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(origin.latitude), math.radians(origin.longitude)
        lat2, lon2 = math.radians(destination.latitude), math.radians(destination.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
        
    async def _get_applicable_discounts(self, user_profile: Dict[str, Any], 
                                      travel_date: datetime, group_size: int) -> List[Discount]:
        """Get discounts applicable to user and journey"""
        
        applicable = []
        
        for discount_id, discount in self.discounts.items():
            # Check age criteria
            user_age = user_profile.get("age", 30)
            if discount.min_age and user_age < discount.min_age:
                continue
            if discount.max_age and user_age > discount.max_age:
                continue
                
            # Check group size
            if discount.min_group_size and group_size < discount.min_group_size:
                continue
                
            # Check day of week
            if discount.valid_days:
                day_name = travel_date.strftime("%A").lower()
                if day_name not in discount.valid_days:
                    continue
                    
            # Check time of day for off-peak discounts
            if discount.valid_hours:
                current_hour = travel_date.strftime("%H:%M")
                time_valid = False
                for time_range in discount.valid_hours:
                    start, end = time_range.split("-")
                    if start <= current_hour <= end:
                        time_valid = True
                        break
                if not time_valid:
                    continue
                    
            applicable.append(discount)
            
        return applicable
        
    async def _apply_discounts(self, fare_calc: FareCalculation, 
                             discounts: List[Discount]) -> FareCalculation:
        """Apply discounts to fare calculation"""
        
        total_discount = 0.0
        applied_discounts = []
        
        for discount in discounts:
            if discount.percentage_off:
                discount_amount = fare_calc.subtotal * discount.percentage_off
            elif discount.fixed_amount_off:
                discount_amount = discount.fixed_amount_off
            else:
                discount_amount = 0.0
                
            total_discount += discount_amount
            applied_discounts.append({
                "discount_id": discount.discount_id,
                "discount_name": discount.name,
                "discount_amount": discount_amount,
                "discount_type": discount.discount_type
            })
            
            if not discount.stackable:
                break  # Only apply first non-stackable discount
                
        fare_calc.discounts_applied = applied_discounts
        fare_calc.total_discount_amount = total_discount
        fare_calc.final_fare = max(0, fare_calc.subtotal - total_discount)
        
        return fare_calc
        
    async def _get_season_pass_recommendations(self, user_profile: Dict[str, Any], 
                                             distance_km: float) -> List[SeasonPass]:
        """Get season pass recommendations based on user profile"""
        
        recommendations = []
        estimated_monthly_trips = user_profile.get("monthly_trips", 20)
        
        for pass_id, season_pass in self.season_passes.items():
            # Simple recommendation logic
            if estimated_monthly_trips >= season_pass.break_even_trips / 2:
                recommendations.append(season_pass)
                
        return recommendations
        
    async def _calculate_group_booking(self, fare_calc: FareCalculation, 
                                     group_size: int) -> GroupBooking:
        """Calculate group booking savings"""
        
        group_discount_percentage = 0.1 if group_size >= 5 else 0.05
        individual_cost = fare_calc.final_fare
        total_individual = individual_cost * group_size
        group_discount = total_individual * group_discount_percentage
        
        return GroupBooking(
            group_id=f"group_{datetime.utcnow().isoformat()}",
            group_size=group_size,
            group_type="general",
            individual_fare_per_person=individual_cost,
            group_discount_percentage=group_discount_percentage,
            group_discount_amount=group_discount,
            total_individual_cost=total_individual,
            group_fare_total=total_individual - group_discount,
            total_savings=group_discount
        )
        
    def _calculate_potential_savings(self, cheapest_fare: Optional[FareCalculation], 
                                   discounts: List[Discount]) -> float:
        """Calculate total potential savings"""
        
        if not cheapest_fare:
            return 0.0
            
        max_discount = 0.0
        for discount in discounts:
            if discount.percentage_off:
                discount_amount = cheapest_fare.subtotal * discount.percentage_off
            elif discount.fixed_amount_off:
                discount_amount = discount.fixed_amount_off
            else:
                discount_amount = 0.0
                
            max_discount = max(max_discount, discount_amount)
            
        return max_discount
        
    def _generate_savings_opportunities(self, cheapest_fare: Optional[FareCalculation],
                                      discounts: List[Discount],
                                      season_passes: List[SeasonPass]) -> List[str]:
        """Generate savings opportunity recommendations"""
        
        opportunities = []
        
        if discounts:
            opportunities.append(f"Apply available discounts to save up to {max([d.percentage_off or 0 for d in discounts]) * 100:.0f}%")
            
        if season_passes:
            opportunities.append("Consider season passes for regular travel")
            
        opportunities.extend([
            "Travel during off-peak hours for lower fares",
            "Book in advance for early bird discounts",
            "Use digital payment methods for cashback"
        ])
        
        return opportunities
        
    def _get_discount_requirements(self, discount: Discount) -> List[str]:
        """Get discount requirements for user"""
        
        requirements = []
        
        if discount.required_documents:
            requirements.append(f"Required documents: {', '.join(discount.required_documents)}")
            
        if discount.min_age:
            requirements.append(f"Minimum age: {discount.min_age}")
            
        if discount.min_group_size:
            requirements.append(f"Minimum group size: {discount.min_group_size}")
            
        if discount.requires_registration:
            requirements.append("Registration required")
            
        return requirements
        
    def _get_application_instructions(self, discount: Discount) -> List[str]:
        """Get instructions for applying discount"""
        
        instructions = []
        
        if discount.auto_apply:
            instructions.append("Automatically applied at booking")
        else:
            instructions.append("Manual application required")
            instructions.append(f"Use discount code: {discount.discount_id.upper()}")
            
        if discount.required_documents:
            instructions.append("Present required documents during travel")
            
        return instructions