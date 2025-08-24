from app.agents.base_agent import BaseAgent
from app.models.disruption_management import (
    DisruptionAlert, DisruptionType, SeverityLevel, DisruptionStatus,
    ImpactAssessment, ContingencyPlan, DisruptionResponse,
    AffectedArea, CreateDisruptionRequest, UpdateDisruptionRequest,
    DisruptionQuery, DisruptionMonitoringRequest
)
from app.models.transport_data import TransportMode, Location
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime, timedelta
import random
import uuid


class DisruptionManagementAgent(BaseAgent):
    """
    Disruption Management Agent - Proactive Service Monitoring
    
    Primary Functions:
    - Real-time service status tracking
    - Predictive disruption modeling
    - Weather impact assessment
    - Dynamic re-routing suggestions
    - Contingency planning with backup options
    """
    
    def __init__(self):
        super().__init__(
            agent_id="disruption_management_agent",
            name="Disruption Management Agent",
            priority_weight=0.95  # Very high priority for safety and service
        )
        
        # In-memory disruption storage (in production, use database)
        self.active_disruptions: Dict[str, DisruptionAlert] = {}
        self.disruption_history: List[DisruptionAlert] = []
        
        # Monitoring configurations
        self.monitoring_intervals = {
            DisruptionType.EMERGENCY: 30,     # 30 seconds
            DisruptionType.ACCIDENT: 60,      # 1 minute
            DisruptionType.WEATHER: 300,      # 5 minutes
            DisruptionType.STRIKE: 600,       # 10 minutes
            DisruptionType.DELAY: 120,        # 2 minutes
        }
        
        # Severity escalation thresholds
        self.escalation_thresholds = {
            "delay_minutes": {30: SeverityLevel.LOW, 60: SeverityLevel.MEDIUM, 120: SeverityLevel.HIGH},
            "affected_routes": {1: SeverityLevel.LOW, 5: SeverityLevel.MEDIUM, 10: SeverityLevel.HIGH},
            "passenger_impact": {100: SeverityLevel.LOW, 500: SeverityLevel.MEDIUM, 1000: SeverityLevel.HIGH}
        }
        
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for disruption management requests"""
        
        request_type = payload.get("request_type", "")
        data = payload.get("data", {})
        
        if request_type == "create_disruption":
            return await self._create_disruption(data)
        elif request_type == "update_disruption":
            return await self._update_disruption(data)
        elif request_type == "get_disruptions":
            return await self._get_disruptions(data)
        elif request_type == "assess_impact":
            return await self._assess_impact(data)
        elif request_type == "get_contingency_plans":
            return await self._get_contingency_plans(data)
        elif request_type == "monitor_route":
            return await self._monitor_route(data)
        elif request_type == "resolve_disruption":
            return await self._resolve_disruption(data)
        else:
            return {
                "success": False,
                "error": f"Unknown request type: {request_type}",
                "data": {}
            }
    
    async def _create_disruption(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new disruption alert"""
        try:
            request = CreateDisruptionRequest(**data)
            
            # Generate unique disruption ID
            disruption_id = f"DISR_{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate estimated end time
            estimated_end_time = None
            if request.estimated_duration_hours:
                estimated_end_time = datetime.utcnow() + timedelta(hours=request.estimated_duration_hours)
            
            # Create disruption alert
            disruption = DisruptionAlert(
                id=disruption_id,
                title=request.title,
                description=request.description,
                disruption_type=request.disruption_type,
                severity=request.severity,
                status=DisruptionStatus.ACTIVE,
                transport_modes=request.transport_modes,
                affected_areas=request.affected_areas,
                start_time=datetime.utcnow(),
                estimated_end_time=estimated_end_time,
                source=request.source,
                confidence_score=0.9
            )
            
            # Store disruption
            self.active_disruptions[disruption_id] = disruption
            
            # Assess immediate impact
            impact = await self._calculate_impact_assessment(disruption)
            
            return {
                "success": True,
                "data": {
                    "disruption_id": disruption_id,
                    "disruption": disruption.model_dump(),
                    "impact_assessment": impact.model_dump() if impact else None,
                    "message": f"Disruption {disruption_id} created successfully"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create disruption: {str(e)}",
                "data": {}
            }
    
    async def _update_disruption(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing disruption"""
        try:
            request = UpdateDisruptionRequest(**data)
            
            if request.disruption_id not in self.active_disruptions:
                return {
                    "success": False,
                    "error": "Disruption not found",
                    "data": {}
                }
            
            disruption = self.active_disruptions[request.disruption_id]
            
            # Update fields
            if request.status:
                disruption.status = request.status
            if request.severity:
                disruption.severity = request.severity
            if request.description:
                disruption.description = request.description
            if request.estimated_end_time:
                disruption.estimated_end_time = request.estimated_end_time
            if request.actual_end_time:
                disruption.actual_end_time = request.actual_end_time
                if request.status != DisruptionStatus.RESOLVED:
                    disruption.status = DisruptionStatus.RESOLVED
            
            disruption.updated_at = datetime.utcnow()
            
            # Move to history if resolved
            if disruption.status == DisruptionStatus.RESOLVED:
                self.disruption_history.append(disruption)
                del self.active_disruptions[request.disruption_id]
            
            return {
                "success": True,
                "data": {
                    "disruption": disruption.model_dump(),
                    "message": f"Disruption {request.disruption_id} updated successfully"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update disruption: {str(e)}",
                "data": {}
            }
    
    async def _get_disruptions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query disruptions based on criteria"""
        try:
            query = DisruptionQuery(**data)
            
            # Filter active disruptions
            filtered_disruptions = []
            
            for disruption in self.active_disruptions.values():
                if self._matches_query(disruption, query):
                    filtered_disruptions.append(disruption)
            
            # Include planned disruptions if requested
            if query.include_planned:
                # Add any planned disruptions (mock for now)
                pass
            
            # Sort by severity and time
            filtered_disruptions.sort(key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.severity],
                x.start_time
            ), reverse=True)
            
            return {
                "success": True,
                "data": {
                    "disruptions": [d.model_dump() for d in filtered_disruptions],
                    "count": len(filtered_disruptions),
                    "query_time": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get disruptions: {str(e)}",
                "data": {}
            }
    
    async def _assess_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess impact of a specific disruption"""
        try:
            disruption_id = data.get("disruption_id")
            
            if disruption_id not in self.active_disruptions:
                return {
                    "success": False,
                    "error": "Disruption not found",
                    "data": {}
                }
            
            disruption = self.active_disruptions[disruption_id]
            impact = await self._calculate_impact_assessment(disruption)
            
            return {
                "success": True,
                "data": {
                    "impact_assessment": impact.model_dump()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to assess impact: {str(e)}",
                "data": {}
            }
    
    async def _get_contingency_plans(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get contingency plans for disruption types"""
        try:
            disruption_type = DisruptionType(data.get("disruption_type", "delay"))
            severity = SeverityLevel(data.get("severity", "medium"))
            
            plans = await self._generate_contingency_plans(disruption_type, severity)
            
            return {
                "success": True,
                "data": {
                    "contingency_plans": [plan.model_dump() for plan in plans]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get contingency plans: {str(e)}",
                "data": {}
            }
    
    async def _monitor_route(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up monitoring for a specific route"""
        try:
            request = DisruptionMonitoringRequest(**data)
            
            # Check for existing disruptions on route
            relevant_disruptions = []
            for disruption in self.active_disruptions.values():
                if self._affects_route(disruption, request.origin, request.destination):
                    relevant_disruptions.append(disruption)
            
            return {
                "success": True,
                "data": {
                    "monitoring_id": f"MON_{uuid.uuid4().hex[:8].upper()}",
                    "route": {
                        "origin": request.origin.model_dump(),
                        "destination": request.destination.model_dump(),
                        "planned_departure": request.planned_departure.isoformat()
                    },
                    "current_disruptions": [d.model_dump() for d in relevant_disruptions],
                    "monitoring_duration_hours": request.monitor_duration_hours,
                    "next_check": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to set up monitoring: {str(e)}",
                "data": {}
            }
    
    async def _resolve_disruption(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a disruption"""
        try:
            disruption_id = data.get("disruption_id")
            resolution_notes = data.get("resolution_notes", "")
            
            if disruption_id not in self.active_disruptions:
                return {
                    "success": False,
                    "error": "Disruption not found",
                    "data": {}
                }
            
            disruption = self.active_disruptions[disruption_id]
            disruption.status = DisruptionStatus.RESOLVED
            disruption.actual_end_time = datetime.utcnow()
            disruption.updated_at = datetime.utcnow()
            
            # Add resolution notes to description
            if resolution_notes:
                disruption.description += f"\n\nResolution: {resolution_notes}"
            
            # Move to history
            self.disruption_history.append(disruption)
            del self.active_disruptions[disruption_id]
            
            return {
                "success": True,
                "data": {
                    "message": f"Disruption {disruption_id} resolved successfully",
                    "resolution_time": disruption.actual_end_time.isoformat(),
                    "duration_minutes": int((disruption.actual_end_time - disruption.start_time).total_seconds() / 60)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to resolve disruption: {str(e)}",
                "data": {}
            }
    
    async def _calculate_impact_assessment(self, disruption: DisruptionAlert) -> Optional[ImpactAssessment]:
        """Calculate impact assessment for a disruption"""
        try:
            # Simulate impact calculation based on disruption characteristics
            base_delay = {
                DisruptionType.DELAY: 15,
                DisruptionType.CANCELLATION: 45,
                DisruptionType.ROUTE_CHANGE: 25,
                DisruptionType.MECHANICAL_ISSUE: 35,
                DisruptionType.WEATHER: 20,
                DisruptionType.STRIKE: 120,
                DisruptionType.ACCIDENT: 60,
                DisruptionType.TRAFFIC_JAM: 30,
                DisruptionType.ROAD_CLOSURE: 40,
                DisruptionType.EMERGENCY: 90
            }.get(disruption.disruption_type, 20)
            
            severity_multiplier = {
                SeverityLevel.LOW: 0.5,
                SeverityLevel.MEDIUM: 1.0,
                SeverityLevel.HIGH: 1.5,
                SeverityLevel.CRITICAL: 2.0
            }[disruption.severity]
            
            estimated_delay = int(base_delay * severity_multiplier)
            affected_passengers = len(disruption.affected_areas) * random.randint(50, 500)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(disruption)
            
            return ImpactAssessment(
                disruption_id=disruption.id,
                estimated_delay_minutes=estimated_delay,
                affected_passenger_count=affected_passengers,
                alternative_routes_available=disruption.disruption_type != DisruptionType.STRIKE,
                additional_cost_impact=random.randint(50, 300) if disruption.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL] else None,
                accessibility_impact="Limited wheelchair access" if "station" in disruption.description.lower() else None,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Error calculating impact: {e}")
            return None
    
    async def _generate_contingency_plans(self, disruption_type: DisruptionType, severity: SeverityLevel) -> List[ContingencyPlan]:
        """Generate contingency plans for disruption scenarios"""
        
        plans = []
        
        if disruption_type == DisruptionType.DELAY:
            plans.append(ContingencyPlan(
                disruption_type=disruption_type,
                severity=severity,
                actions=[
                    "Monitor real-time updates",
                    "Consider alternative departure times",
                    "Check for express services",
                    "Prepare backup transportation"
                ],
                alternative_routes=["Express bus service", "Alternative rail route"],
                estimated_additional_time=15 if severity == SeverityLevel.LOW else 30,
                estimated_additional_cost=50.0
            ))
        
        elif disruption_type == DisruptionType.STRIKE:
            plans.append(ContingencyPlan(
                disruption_type=disruption_type,
                severity=severity,
                actions=[
                    "Use private transportation",
                    "Consider ride-sharing options",
                    "Work from home if possible",
                    "Plan multi-day accommodation if needed"
                ],
                alternative_routes=["Private bus operators", "Taxi services", "Ride-sharing"],
                estimated_additional_time=60,
                estimated_additional_cost=500.0,
                emergency_contacts=[
                    {"type": "Transport Authority", "phone": "+94-11-2345678"},
                    {"type": "Tourist Police", "phone": "+94-11-2421052"}
                ]
            ))
        
        elif disruption_type == DisruptionType.WEATHER:
            plans.append(ContingencyPlan(
                disruption_type=disruption_type,
                severity=severity,
                actions=[
                    "Check weather updates frequently",
                    "Carry rain protection",
                    "Allow extra travel time",
                    "Consider postponing non-essential travel"
                ],
                alternative_routes=["Covered walkways to stations", "Underground passages"],
                estimated_additional_time=20,
                special_instructions="Heavy monsoon conditions may cause flooding. Stay updated on weather alerts."
            ))
        
        return plans
    
    async def _generate_recommendations(self, disruption: DisruptionAlert) -> List[str]:
        """Generate specific recommendations for a disruption"""
        recommendations = []
        
        if disruption.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            recommendations.append("Consider postponing non-essential travel")
            recommendations.append("Allow at least 50% extra travel time")
        
        if DisruptionType.WEATHER in [disruption.disruption_type]:
            recommendations.append("Carry rain protection and warm clothing")
            recommendations.append("Monitor weather updates")
        
        if len(disruption.affected_areas) > 1:
            recommendations.append("Multiple areas affected - consider alternative routes")
        
        recommendations.extend([
            "Monitor real-time updates",
            "Have backup transportation options ready",
            "Keep emergency contact numbers available"
        ])
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _matches_query(self, disruption: DisruptionAlert, query: DisruptionQuery) -> bool:
        """Check if disruption matches query criteria"""
        
        # Check active status
        if query.active_only and disruption.status != DisruptionStatus.ACTIVE:
            return False
        
        # Check transport modes
        if query.transport_modes:
            if not any(mode in disruption.transport_modes for mode in query.transport_modes):
                return False
        
        # Check severity levels
        if query.severity_levels:
            if disruption.severity not in query.severity_levels:
                return False
        
        # Check disruption types
        if query.disruption_types:
            if disruption.disruption_type not in query.disruption_types:
                return False
        
        # Check location proximity
        if query.location and query.radius_km:
            within_radius = False
            for area in disruption.affected_areas:
                distance = self._calculate_distance(query.location, area.location)
                if distance <= query.radius_km:
                    within_radius = True
                    break
            if not within_radius:
                return False
        
        return True
    
    def _affects_route(self, disruption: DisruptionAlert, origin: Location, destination: Location) -> bool:
        """Check if disruption affects a specific route"""
        
        for area in disruption.affected_areas:
            # Check if origin or destination is within affected area
            origin_distance = self._calculate_distance(origin, area.location)
            dest_distance = self._calculate_distance(destination, area.location)
            
            if origin_distance <= area.radius_km or dest_distance <= area.radius_km:
                return True
        
        return False
    
    def _calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate approximate distance between two locations (simplified)"""
        # Simplified distance calculation - in production use proper geospatial functions
        lat_diff = abs(loc1.latitude - loc2.latitude)
        lon_diff = abs(loc1.longitude - loc2.longitude)
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion
    
    async def on_start(self):
        """Initialize agent on startup"""
        print(f"[{self.name}] Starting disruption monitoring...")
        
        # Create some sample disruptions for testing
        await self._create_sample_disruptions()
        
    async def _create_sample_disruptions(self):
        """Create sample disruptions for testing"""
        
        # Sample disruption 1: Bus delay in Colombo
        sample_data_1 = {
            "title": "Bus Service Delays - Galle Road",
            "description": "Heavy traffic causing 15-20 minute delays on Route 100 (Colombo-Mount Lavinia)",
            "disruption_type": DisruptionType.DELAY,
            "severity": SeverityLevel.MEDIUM,
            "transport_modes": [TransportMode.BUS],
            "affected_areas": [{
                "location": {"latitude": 6.9271, "longitude": 79.8612, "address": "Galle Road, Colombo"},
                "radius_km": 5.0,
                "affected_routes": ["Route 100", "Route 101"]
            }],
            "estimated_duration_hours": 2,
            "source": "traffic_monitoring_system"
        }
        
        await self._create_disruption(sample_data_1)
        
        # Sample disruption 2: Train cancellation
        sample_data_2 = {
            "title": "Train Service Cancellation - Kandy Line",
            "description": "Signal failure at Peradeniya Junction. Trains 6007 and 6009 cancelled.",
            "disruption_type": DisruptionType.CANCELLATION,
            "severity": SeverityLevel.HIGH,
            "transport_modes": [TransportMode.TRAIN],
            "affected_areas": [{
                "location": {"latitude": 7.2906, "longitude": 80.6337, "address": "Peradeniya Junction"},
                "radius_km": 10.0,
                "affected_routes": ["Main Line", "Kandy Commuter"]
            }],
            "estimated_duration_hours": 4,
            "source": "sri_lanka_railways"
        }
        
        await self._create_disruption(sample_data_2)