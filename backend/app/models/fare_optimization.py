from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from enum import Enum
from decimal import Decimal

from app.models.transport_data import TransportMode, Location


class DiscountType(str, Enum):
    STUDENT = "student"
    SENIOR = "senior"
    DISABLED = "disabled"
    GROUP = "group"
    BULK = "bulk"
    SEASON_PASS = "season_pass"
    CORPORATE = "corporate"
    FREQUENT_TRAVELER = "frequent_traveler"
    OFF_PEAK = "off_peak"
    EARLY_BIRD = "early_bird"
    PROMOTIONAL = "promotional"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    MOBILE = "mobile"
    SEASON_TICKET = "season_ticket"
    PREPAID = "prepaid"
    CORPORATE_ACCOUNT = "corporate_account"


class FareRule(BaseModel):
    rule_id: str
    transport_mode: TransportMode
    operator: str
    distance_km: Optional[float] = None
    zone_based: bool = False
    zones: List[str] = []
    
    # Base fare structure
    base_fare: float
    per_km_rate: Optional[float] = None
    zone_fare_matrix: Dict[str, float] = {}  # {"zone1-zone2": fare}
    
    # Time-based pricing
    peak_hour_multiplier: float = 1.0
    off_peak_multiplier: float = 1.0
    weekend_multiplier: float = 1.0
    night_multiplier: float = 1.0
    
    # Validity
    valid_from: datetime
    valid_until: Optional[datetime] = None
    
    # Additional charges
    booking_fee: float = 0.0
    convenience_fee: float = 0.0
    cancellation_fee: float = 0.0


class Discount(BaseModel):
    discount_id: str
    discount_type: DiscountType
    name: str
    description: str
    
    # Discount structure
    percentage_off: Optional[float] = None  # 0.0-1.0
    fixed_amount_off: Optional[float] = None
    buy_x_get_y_free: Optional[Tuple[int, int]] = None
    
    # Eligibility criteria
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    required_documents: List[str] = []
    min_group_size: Optional[int] = None
    min_purchase_amount: Optional[float] = None
    frequency_requirement: Optional[int] = None  # trips per month
    
    # Validity constraints
    valid_days: List[str] = []  # ["monday", "tuesday", ...]
    valid_hours: List[str] = []  # ["09:00-17:00"]
    blackout_dates: List[date] = []
    transport_modes: List[TransportMode] = []
    
    # Usage limits
    max_uses_per_day: Optional[int] = None
    max_uses_per_month: Optional[int] = None
    max_uses_total: Optional[int] = None
    
    # Meta information
    requires_registration: bool = False
    auto_apply: bool = False
    stackable: bool = False
    
    created_date: datetime = Field(default_factory=datetime.utcnow)
    expires_date: Optional[datetime] = None


class FareCalculation(BaseModel):
    calculation_id: str
    route_id: str
    transport_mode: TransportMode
    operator: str
    
    # Journey details
    origin: Location
    destination: Location
    distance_km: float
    duration_minutes: int
    departure_time: datetime
    
    # Base fare breakdown
    base_fare: float
    distance_charge: float = 0.0
    time_charge: float = 0.0
    zone_charge: float = 0.0
    
    # Additional charges
    booking_fee: float = 0.0
    convenience_fee: float = 0.0
    fuel_surcharge: float = 0.0
    service_charge: float = 0.0
    taxes: float = 0.0
    
    # Total before discounts
    subtotal: float
    
    # Applied discounts
    discounts_applied: List[Dict[str, Any]] = []
    total_discount_amount: float = 0.0
    
    # Final fare
    final_fare: float
    
    # Payment method impact
    payment_method: Optional[PaymentMethod] = None
    payment_method_discount: float = 0.0
    payment_method_fee: float = 0.0
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class GroupBooking(BaseModel):
    group_id: str
    group_size: int
    group_type: str  # "family", "student", "corporate", "tour"
    
    # Individual fare details
    individual_fare_per_person: float
    group_discount_percentage: float = 0.0
    group_discount_amount: float = 0.0
    
    # Group pricing
    total_individual_cost: float
    group_fare_total: float
    total_savings: float
    
    # Special group benefits
    free_seats: int = 0  # Buy X get Y free
    group_leader_discount: float = 0.0
    additional_services: List[str] = []  # ["priority_boarding", "group_seating"]


class SeasonPass(BaseModel):
    pass_id: str
    pass_name: str
    pass_type: str  # "monthly", "quarterly", "annual"
    
    # Coverage
    transport_modes: List[TransportMode]
    zones: List[str] = []
    routes: List[str] = []
    unlimited_travel: bool = True
    trip_limit: Optional[int] = None
    
    # Pricing
    pass_price: float
    equivalent_individual_trips: int
    individual_trip_cost: float
    break_even_trips: int
    potential_savings: float
    savings_percentage: float
    
    # Validity
    valid_from: datetime
    valid_until: datetime
    validity_days: int
    
    # Usage tracking
    trips_used: int = 0
    current_savings: float = 0.0


class FareOptimizationResult(BaseModel):
    optimization_id: str
    user_id: Optional[str] = None
    
    # Request details
    origin: Location
    destination: Location
    travel_date: datetime
    group_size: int = 1
    user_profile: Dict[str, Any] = {}
    
    # All available fare options
    all_fare_options: List[FareCalculation] = []
    
    # Optimized recommendations
    cheapest_option: Optional[FareCalculation] = None
    best_value_option: Optional[FareCalculation] = None  # Best price/comfort ratio
    recommended_option: Optional[FareCalculation] = None
    
    # Discount opportunities
    available_discounts: List[Discount] = []
    missed_discounts: List[Dict[str, Any]] = []  # Discounts user could qualify for
    
    # Season pass analysis
    season_pass_recommendations: List[SeasonPass] = []
    
    # Group booking options
    group_booking_analysis: Optional[GroupBooking] = None
    
    # Payment optimization
    payment_method_recommendations: List[Dict[str, Any]] = []
    
    # Savings summary
    total_potential_savings: float = 0.0
    savings_opportunities: List[str] = []
    
    # Long-term analysis
    monthly_travel_cost_estimate: Optional[float] = None
    annual_travel_cost_estimate: Optional[float] = None
    season_pass_roi_analysis: Dict[str, Any] = {}
    
    optimization_timestamp: datetime = Field(default_factory=datetime.utcnow)
    optimization_confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class CostBreakdown(BaseModel):
    """Detailed cost breakdown for transparency"""
    
    category: str  # "base_fare", "taxes", "fees", "discounts"
    description: str
    amount: float
    percentage_of_total: float
    is_optional: bool = False
    
    # Breakdown details
    calculation_method: str = "fixed"  # "fixed", "percentage", "per_km", "per_zone"
    rate: Optional[float] = None
    quantity: Optional[float] = None
    
    notes: List[str] = []


class FarePrediction(BaseModel):
    """Predicted fare changes and optimization suggestions"""
    
    prediction_id: str
    route_id: str
    
    # Current vs predicted pricing
    current_fare: float
    predicted_fare_1_week: float
    predicted_fare_1_month: float
    predicted_fare_3_months: float
    
    # Price trend analysis
    price_trend: str  # "increasing", "decreasing", "stable", "volatile"
    confidence_level: float = Field(ge=0.0, le=1.0)
    
    # Factors affecting price
    demand_factors: List[str] = []
    seasonal_factors: List[str] = []
    operational_factors: List[str] = []
    
    # Recommendations
    best_time_to_book: str
    price_alerts_recommended: bool = False
    advance_booking_savings: float = 0.0
    
    prediction_date: datetime = Field(default_factory=datetime.utcnow)


class BulkPurchaseOption(BaseModel):
    """Bulk purchase and prepaid options analysis"""
    
    option_id: str
    option_name: str
    option_type: str  # "bulk_tickets", "prepaid_balance", "trip_package"
    
    # Purchase details
    number_of_trips: int
    individual_trip_cost: float
    bulk_price: float
    discount_per_trip: float
    total_savings: float
    savings_percentage: float
    
    # Validity and restrictions
    valid_for_days: int
    transferable: bool = False
    refundable: bool = False
    blackout_dates: List[date] = []
    
    # Value analysis
    break_even_usage: int  # Minimum trips needed to break even
    recommended_for_frequency: str  # "daily", "weekly", "occasional"
    risk_assessment: str  # "low", "medium", "high"
    
    # Additional benefits
    bonus_features: List[str] = []  # ["priority_booking", "flexible_dates"]