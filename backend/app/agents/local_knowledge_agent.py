from app.agents.base_agent import BaseAgent
from app.models.local_knowledge import (
    LocalKnowledgeEntry, CulturalGuidance, TouristAttraction,
    LocalEvent, SafetyInformation, LocalRecommendation,
    LocalKnowledgeResponse, LocalKnowledgeQuery,
    CreateKnowledgeRequest, UpdateKnowledgeRequest,
    CulturalInsightRequest, TouristGuidanceRequest,
    KnowledgeType, ContentCategory, Language, UserType
)
from app.models.transport_data import Location, TransportMode
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime, timedelta
import random
import uuid


class LocalKnowledgeAgent(BaseAgent):
    """
    Local Knowledge Agent - Community Intelligence Integration
    
    Primary Functions:
    - Cultural insights and local tips
    - Popular destinations and routes  
    - Cultural event impacts on transportation
    - Tourist-friendly guidance
    - Local safety information and emergency contacts
    """
    
    def __init__(self):
        super().__init__(
            agent_id="local_knowledge_agent",
            name="Local Knowledge Agent",
            priority_weight=0.7  # Medium-high priority for user experience
        )
        
        # In-memory knowledge storage (in production, use database)
        self.knowledge_entries: Dict[str, LocalKnowledgeEntry] = {}
        self.cultural_guidance_cache: Dict[str, CulturalGuidance] = {}
        self.tourist_attractions: List[TouristAttraction] = []
        self.local_events: List[LocalEvent] = []
        self.safety_info_cache: Dict[str, SafetyInformation] = {}
        self.recommendations: Dict[str, List[LocalRecommendation]] = {}
        
        # Knowledge scoring weights
        self.scoring_weights = {
            "importance": 0.4,
            "reliability": 0.3,
            "recency": 0.2,
            "user_relevance": 0.1
        }
        
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for local knowledge requests"""
        
        request_type = payload.get("request_type", "")
        data = payload.get("data", {})
        
        if request_type == "get_local_knowledge":
            return await self._get_local_knowledge(data)
        elif request_type == "create_knowledge_entry":
            return await self._create_knowledge_entry(data)
        elif request_type == "update_knowledge_entry":
            return await self._update_knowledge_entry(data)
        elif request_type == "get_cultural_insights":
            return await self._get_cultural_insights(data)
        elif request_type == "get_tourist_guidance":
            return await self._get_tourist_guidance(data)
        elif request_type == "get_safety_information":
            return await self._get_safety_information(data)
        elif request_type == "get_local_events":
            return await self._get_local_events(data)
        elif request_type == "get_recommendations":
            return await self._get_recommendations(data)
        else:
            return {
                "success": False,
                "error": f"Unknown request type: {request_type}",
                "data": {}
            }
    
    async def _get_local_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive local knowledge for a location"""
        try:
            query = LocalKnowledgeQuery(**data)
            
            # Get relevant knowledge entries
            knowledge_entries = await self._find_relevant_entries(query)
            
            # Get cultural guidance if requested
            cultural_guidance = None
            if query.include_cultural_info and query.location:
                cultural_guidance = await self._get_cultural_guidance_for_location(query.location)
            
            # Get tourist attractions if requested
            tourist_attractions = []
            if query.include_tourist_attractions and query.location:
                tourist_attractions = await self._find_nearby_attractions(query.location, query.radius_km)
            
            # Get local events if requested
            local_events = []
            if query.include_local_events and query.location:
                local_events = await self._find_upcoming_events(query.location, query.radius_km)
            
            # Get safety information if requested
            safety_info = None
            if query.include_safety_info and query.location:
                safety_info = await self._get_safety_info_for_location(query.location)
            
            # Get recommendations
            recommendations = await self._get_location_recommendations(query)
            
            response = LocalKnowledgeResponse(
                knowledge_entries=knowledge_entries,
                cultural_guidance=cultural_guidance,
                tourist_attractions=tourist_attractions,
                local_events=local_events,
                safety_information=safety_info,
                recommendations=recommendations,
                total_count=len(knowledge_entries),
                query_location=query.location,
                language=query.language
            )
            
            return {
                "success": True,
                "data": {
                    "local_knowledge": response.model_dump(),
                    "query_processed": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get local knowledge: {str(e)}",
                "data": {}
            }
    
    async def _create_knowledge_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new local knowledge entry"""
        try:
            request = CreateKnowledgeRequest(**data)
            
            # Generate unique entry ID
            entry_id = f"LKE_{uuid.uuid4().hex[:8].upper()}"
            
            # Create knowledge entry
            entry = LocalKnowledgeEntry(
                id=entry_id,
                title=request.title,
                description=request.description,
                knowledge_type=request.knowledge_type,
                category=request.category,
                location=request.location,
                relevant_radius_km=request.relevant_radius_km,
                languages=request.languages,
                target_user_types=request.target_user_types,
                source=request.source
            )
            
            # Store entry
            self.knowledge_entries[entry_id] = entry
            
            return {
                "success": True,
                "data": {
                    "entry_id": entry_id,
                    "knowledge_entry": entry.model_dump(),
                    "message": f"Local knowledge entry {entry_id} created successfully"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create knowledge entry: {str(e)}",
                "data": {}
            }
    
    async def _update_knowledge_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing knowledge entry"""
        try:
            request = UpdateKnowledgeRequest(**data)
            
            if request.entry_id not in self.knowledge_entries:
                return {
                    "success": False,
                    "error": "Knowledge entry not found",
                    "data": {}
                }
            
            entry = self.knowledge_entries[request.entry_id]
            
            # Update fields
            if request.title:
                entry.title = request.title
            if request.description:
                entry.description = request.description
            if request.importance_score is not None:
                entry.importance_score = request.importance_score
            if request.reliability_score is not None:
                entry.reliability_score = request.reliability_score
            if request.last_verified:
                entry.last_verified = request.last_verified
            
            entry.updated_at = datetime.utcnow()
            
            return {
                "success": True,
                "data": {
                    "knowledge_entry": entry.model_dump(),
                    "message": f"Knowledge entry {request.entry_id} updated successfully"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update knowledge entry: {str(e)}",
                "data": {}
            }
    
    async def _get_cultural_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get cultural insights for a specific location and user type"""
        try:
            request = CulturalInsightRequest(**data)
            
            # Get cultural guidance for location
            cultural_guidance = await self._get_cultural_guidance_for_location(request.location)
            
            # Get relevant cultural knowledge entries
            cultural_entries = []
            for entry in self.knowledge_entries.values():
                if (entry.category == ContentCategory.CULTURE and
                    self._is_location_relevant(entry.location, request.location, entry.relevant_radius_km) and
                    (not entry.target_user_types or request.user_type in entry.target_user_types) and
                    request.language in entry.languages):
                    cultural_entries.append(entry)
            
            # Sort by relevance
            cultural_entries.sort(key=lambda x: x.importance_score * x.reliability_score, reverse=True)
            
            return {
                "success": True,
                "data": {
                    "cultural_guidance": cultural_guidance.model_dump() if cultural_guidance else None,
                    "cultural_entries": [entry.model_dump() for entry in cultural_entries],
                    "location": request.location.model_dump(),
                    "user_type": request.user_type,
                    "language": request.language
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get cultural insights: {str(e)}",
                "data": {}
            }
    
    async def _get_tourist_guidance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive tourist guidance for a journey"""
        try:
            request = TouristGuidanceRequest(**data)
            
            # Get attractions along the route
            route_attractions = []
            
            # Check attractions near origin
            origin_attractions = await self._find_nearby_attractions(request.origin, 10.0)
            route_attractions.extend(origin_attractions)
            
            # Check attractions near destination
            dest_attractions = await self._find_nearby_attractions(request.destination, 10.0)
            route_attractions.extend(dest_attractions)
            
            # Remove duplicates
            seen_attractions = set()
            unique_attractions = []
            for attraction in route_attractions:
                if attraction.name not in seen_attractions:
                    unique_attractions.append(attraction)
                    seen_attractions.add(attraction.name)
            
            # Get safety information for both locations
            origin_safety = await self._get_safety_info_for_location(request.origin)
            dest_safety = await self._get_safety_info_for_location(request.destination)
            
            # Get cultural guidance
            cultural_guidance = await self._get_cultural_guidance_for_location(request.destination)
            
            return {
                "success": True,
                "data": {
                    "route": {
                        "origin": request.origin.model_dump(),
                        "destination": request.destination.model_dump()
                    },
                    "attractions": [attraction.model_dump() for attraction in unique_attractions],
                    "cultural_guidance": cultural_guidance.model_dump() if cultural_guidance else None,
                    "safety_information": {
                        "origin": origin_safety.model_dump() if origin_safety else None,
                        "destination": dest_safety.model_dump() if dest_safety else None
                    },
                    "user_type": request.user_type,
                    "language": request.language
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get tourist guidance: {str(e)}",
                "data": {}
            }
    
    async def _get_safety_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get safety information for a location"""
        try:
            location = Location(**data.get("location", {}))
            
            safety_info = await self._get_safety_info_for_location(location)
            
            return {
                "success": True,
                "data": {
                    "safety_information": safety_info.model_dump() if safety_info else None,
                    "location": location.model_dump()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get safety information: {str(e)}",
                "data": {}
            }
    
    async def _get_local_events(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get upcoming local events for a location"""
        try:
            location = Location(**data.get("location", {}))
            radius_km = data.get("radius_km", 10.0)
            
            events = await self._find_upcoming_events(location, radius_km)
            
            return {
                "success": True,
                "data": {
                    "local_events": [event.model_dump() for event in events],
                    "location": location.model_dump(),
                    "radius_km": radius_km,
                    "events_count": len(events)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get local events: {str(e)}",
                "data": {}
            }
    
    async def _get_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get local recommendations for a location"""
        try:
            query = LocalKnowledgeQuery(**data)
            
            recommendations = await self._get_location_recommendations(query)
            
            return {
                "success": True,
                "data": {
                    "recommendations": [rec.model_dump() for rec in recommendations],
                    "location": query.location.model_dump() if query.location else None,
                    "recommendations_count": len(recommendations)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get recommendations: {str(e)}",
                "data": {}
            }
    
    async def _find_relevant_entries(self, query: LocalKnowledgeQuery) -> List[LocalKnowledgeEntry]:
        """Find relevant knowledge entries based on query criteria"""
        relevant_entries = []
        
        for entry in self.knowledge_entries.values():
            # Check location relevance
            if query.location and not self._is_location_relevant(
                entry.location, query.location, query.radius_km
            ):
                continue
            
            # Check knowledge type filter
            if query.knowledge_types and entry.knowledge_type not in query.knowledge_types:
                continue
            
            # Check category filter
            if query.categories and entry.category not in query.categories:
                continue
            
            # Check user type relevance
            if query.user_type and entry.target_user_types and query.user_type not in entry.target_user_types:
                continue
            
            # Check language support
            if query.language not in entry.languages:
                continue
            
            relevant_entries.append(entry)
        
        # Sort by relevance score
        relevant_entries.sort(key=lambda x: self._calculate_relevance_score(x, query), reverse=True)
        
        return relevant_entries[:20]  # Limit to top 20 results
    
    async def _get_cultural_guidance_for_location(self, location: Location) -> Optional[CulturalGuidance]:
        """Get cultural guidance for a specific location"""
        location_key = f"{location.latitude},{location.longitude}"
        
        if location_key in self.cultural_guidance_cache:
            return self.cultural_guidance_cache[location_key]
        
        # Generate cultural guidance based on location
        # This would typically come from a database or external service
        guidance = CulturalGuidance(
            location=location,
            cultural_norms=[
                "Remove shoes when entering temples and homes",
                "Dress modestly, especially at religious sites",
                "Use your right hand for eating and greeting",
                "Show respect to elders and religious figures"
            ],
            dress_code="Conservative clothing recommended for temples and formal occasions",
            religious_considerations=[
                "Buddha statues are sacred - no inappropriate photos",
                "Silence in meditation areas",
                "Clockwise walking around stupas"
            ],
            local_customs=[
                "Ayubowan (may you live long) is a traditional greeting",
                "Tea culture is very important - accept offered tea",
                "Bargaining is common in markets"
            ],
            language_tips={
                "hello": "Ayubowan (ay-yu-bo-wan)",
                "thank_you": "Istuti (is-too-tee)",
                "excuse_me": "Samavenna (sa-ma-ven-na)"
            },
            greeting_etiquette="Place palms together and bow slightly",
            tipping_guidelines="10% in restaurants, round up for services"
        )
        
        self.cultural_guidance_cache[location_key] = guidance
        return guidance
    
    async def _find_nearby_attractions(self, location: Location, radius_km: float) -> List[TouristAttraction]:
        """Find tourist attractions near a location"""
        nearby_attractions = []
        
        for attraction in self.tourist_attractions:
            distance = self._calculate_distance(location, attraction.location)
            if distance <= radius_km:
                nearby_attractions.append(attraction)
        
        # Sort by distance
        nearby_attractions.sort(key=lambda x: self._calculate_distance(location, x.location))
        
        return nearby_attractions[:10]  # Limit to 10 closest attractions
    
    async def _find_upcoming_events(self, location: Location, radius_km: float) -> List[LocalEvent]:
        """Find upcoming local events near a location"""
        upcoming_events = []
        current_time = datetime.utcnow()
        
        for event in self.local_events:
            # Check if event is upcoming
            if event.start_date < current_time:
                continue
            
            # Check distance
            distance = self._calculate_distance(location, event.location)
            if distance <= radius_km:
                upcoming_events.append(event)
        
        # Sort by start date
        upcoming_events.sort(key=lambda x: x.start_date)
        
        return upcoming_events[:5]  # Limit to next 5 events
    
    async def _get_safety_info_for_location(self, location: Location) -> Optional[SafetyInformation]:
        """Get safety information for a location"""
        location_key = f"{location.latitude},{location.longitude}"
        
        if location_key in self.safety_info_cache:
            return self.safety_info_cache[location_key]
        
        # Generate safety information
        safety_info = SafetyInformation(
            location=location,
            safety_level="safe",
            safety_tips=[
                "Keep valuables secure and avoid displaying expensive items",
                "Use registered taxis or ride-sharing apps",
                "Stay in well-lit areas at night",
                "Keep copies of important documents"
            ],
            emergency_contacts=[
                {"service": "Police", "number": "119"},
                {"service": "Fire & Ambulance", "number": "110"},
                {"service": "Tourist Police", "number": "+94-11-2421052"}
            ],
            common_risks=[
                "Petty theft in crowded areas",
                "Monsoon flooding during rainy season",
                "Traffic congestion and road safety"
            ],
            recommended_precautions=[
                "Carry emergency contacts",
                "Inform someone of your travel plans",
                "Have local currency for emergencies"
            ],
            tourist_police_contact="+94-11-2421052"
        )
        
        self.safety_info_cache[location_key] = safety_info
        return safety_info
    
    async def _get_location_recommendations(self, query: LocalKnowledgeQuery) -> List[LocalRecommendation]:
        """Get recommendations for a location"""
        if not query.location:
            return []
        
        location_key = f"{query.location.latitude},{query.location.longitude}"
        
        if location_key in self.recommendations:
            return self.recommendations[location_key]
        
        # Generate sample recommendations
        recommendations = []
        
        # Add sample recommendations based on knowledge types
        if not query.knowledge_types or KnowledgeType.FOOD_RECOMMENDATIONS in query.knowledge_types:
            recommendations.append(LocalRecommendation(
                id=f"REC_{uuid.uuid4().hex[:8].upper()}",
                location=query.location,
                recommendation_type=KnowledgeType.FOOD_RECOMMENDATIONS,
                title="Local Rice & Curry Restaurant",
                description="Authentic Sri Lankan rice and curry with fresh vegetables and traditional spices",
                rating=4.5,
                price_range="budget",
                operating_hours="11:00 AM - 10:00 PM",
                special_notes=["Vegetarian options available", "Try the fish curry"]
            ))
        
        if not query.knowledge_types or KnowledgeType.SHOPPING_AREAS in query.knowledge_types:
            recommendations.append(LocalRecommendation(
                id=f"REC_{uuid.uuid4().hex[:8].upper()}",
                location=query.location,
                recommendation_type=KnowledgeType.SHOPPING_AREAS,
                title="Local Craft Market",
                description="Traditional handicrafts, textiles, and souvenirs from local artisans",
                rating=4.2,
                price_range="moderate",
                operating_hours="9:00 AM - 6:00 PM",
                special_notes=["Bargaining expected", "Quality batik and wood carvings"]
            ))
        
        self.recommendations[location_key] = recommendations
        return recommendations
    
    def _calculate_relevance_score(self, entry: LocalKnowledgeEntry, query: LocalKnowledgeQuery) -> float:
        """Calculate relevance score for a knowledge entry"""
        score = 0.0
        
        # Importance and reliability
        score += entry.importance_score * self.scoring_weights["importance"]
        score += entry.reliability_score * self.scoring_weights["reliability"]
        
        # Recency score (newer entries get higher scores)
        days_old = (datetime.utcnow() - entry.updated_at).days
        recency_score = max(0, 1.0 - (days_old / 365))  # Decay over a year
        score += recency_score * self.scoring_weights["recency"]
        
        # User relevance
        user_relevance = 1.0 if not entry.target_user_types else 0.5
        if query.user_type and entry.target_user_types and query.user_type in entry.target_user_types:
            user_relevance = 1.0
        score += user_relevance * self.scoring_weights["user_relevance"]
        
        return score
    
    def _is_location_relevant(self, entry_location: Location, query_location: Location, max_distance_km: float) -> bool:
        """Check if a location is within the relevant radius"""
        distance = self._calculate_distance(entry_location, query_location)
        return distance <= max_distance_km
    
    def _calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate approximate distance between two locations (simplified)"""
        lat_diff = abs(loc1.latitude - loc2.latitude)
        lon_diff = abs(loc1.longitude - loc2.longitude)
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion
    
    async def on_start(self):
        """Initialize agent on startup"""
        print(f"[{self.name}] Initializing local knowledge database...")
        
        # Create sample knowledge entries
        await self._create_sample_knowledge()
        
        # Create sample tourist attractions
        await self._create_sample_attractions()
        
        # Create sample events
        await self._create_sample_events()
        
        print(f"[{self.name}] Local knowledge database initialized with {len(self.knowledge_entries)} entries")
    
    async def _create_sample_knowledge(self):
        """Create sample knowledge entries for testing"""
        
        # Temple etiquette entry
        temple_entry = LocalKnowledgeEntry(
            id="LKE_TEMPLE01",
            title="Temple Visiting Etiquette",
            description="Important guidelines for visiting Buddhist temples in Sri Lanka",
            knowledge_type=KnowledgeType.CULTURAL_INFO,
            category=ContentCategory.CULTURE,
            location=Location(latitude=7.2906, longitude=80.6337, address="Kandy, Central Province"),
            relevant_radius_km=50.0,
            languages=[Language.ENGLISH, Language.SINHALA],
            target_user_types=[UserType.TOURIST, UserType.BUSINESS_TRAVELER],
            importance_score=0.9,
            reliability_score=0.95,
            source="cultural_expert"
        )
        self.knowledge_entries[temple_entry.id] = temple_entry
        
        # Local transport tip
        transport_entry = LocalKnowledgeEntry(
            id="LKE_TRANSPORT01",
            title="Using Local Buses in Colombo",
            description="Tips for navigating Colombo's bus system including routes, payment, and safety",
            knowledge_type=KnowledgeType.LOCAL_TIPS,
            category=ContentCategory.TRANSPORTATION,
            location=Location(latitude=6.9271, longitude=79.8612, address="Colombo, Western Province"),
            relevant_radius_km=25.0,
            languages=[Language.ENGLISH, Language.SINHALA, Language.TAMIL],
            target_user_types=[UserType.TOURIST, UserType.LOCAL_COMMUTER],
            importance_score=0.8,
            reliability_score=0.9,
            source="local_commuter"
        )
        self.knowledge_entries[transport_entry.id] = transport_entry
    
    async def _create_sample_attractions(self):
        """Create sample tourist attractions"""
        
        # Temple of the Tooth
        tooth_temple = TouristAttraction(
            name="Temple of the Tooth Relic (Sri Dalada Maligawa)",
            location=Location(latitude=7.2942, longitude=80.6351, address="Kandy"),
            description="Sacred Buddhist temple housing a tooth relic of Buddha",
            category="temple",
            entry_fee=1500.0,
            opening_hours="5:30 AM - 8:00 PM",
            best_time_to_visit="Early morning or evening for puja ceremonies",
            cultural_significance="Most sacred Buddhist site in Sri Lanka",
            visitor_tips=[
                "Dress modestly - cover shoulders and knees",
                "Remove shoes and hats before entering",
                "Photography may be restricted in certain areas",
                "Visit during puja times (6:30 AM, 12:30 PM, 7:30 PM) for ceremonies"
            ],
            languages_supported=[Language.ENGLISH, Language.SINHALA]
        )
        self.tourist_attractions.append(tooth_temple)
        
        # Colombo National Museum
        museum = TouristAttraction(
            name="Colombo National Museum",
            location=Location(latitude=6.9147, longitude=79.8618, address="Colombo 7"),
            description="Sri Lanka's largest museum with extensive collection of cultural artifacts",
            category="museum",
            entry_fee=500.0,
            opening_hours="9:00 AM - 5:00 PM (Closed on Fridays)",
            best_time_to_visit="Morning hours for cooler weather",
            visitor_tips=[
                "Allow 2-3 hours for full visit",
                "Guided tours available",
                "Photography fee may apply"
            ],
            languages_supported=[Language.ENGLISH, Language.SINHALA]
        )
        self.tourist_attractions.append(museum)
    
    async def _create_sample_events(self):
        """Create sample local events"""
        
        # Vesak Festival
        vesak_event = LocalEvent(
            id="EVT_VESAK2025",
            name="Vesak Festival",
            description="Buddhist festival celebrating the birth, enlightenment, and death of Buddha",
            location=Location(latitude=6.9271, longitude=79.8612, address="Colombo"),
            start_date=datetime(2025, 5, 12),
            end_date=datetime(2025, 5, 14),
            event_type="festival",
            transport_impact="Heavy traffic and road closures expected. Additional bus services will be provided.",
            cultural_significance="Most important Buddhist festival in Sri Lanka",
            visitor_guidelines=[
                "Dress respectfully",
                "Participate respectfully in religious activities",
                "Try traditional Vesak foods and lanterns"
            ],
            contact_info="Sri Lanka Tourism Development Authority: +94-11-2426900"
        )
        self.local_events.append(vesak_event)
        
        # Kandy Esala Perahera
        perahera_event = LocalEvent(
            id="EVT_PERAHERA2025",
            name="Esala Perahera",
            description="Grand procession featuring elephants, dancers, and drummers in Kandy",
            location=Location(latitude=7.2942, longitude=80.6351, address="Kandy"),
            start_date=datetime(2025, 8, 5),
            end_date=datetime(2025, 8, 15),
            event_type="ceremony",
            transport_impact="Road closures during procession hours. Special bus services available.",
            cultural_significance="One of Asia's most spectacular Buddhist festivals",
            visitor_guidelines=[
                "Book accommodation well in advance",
                "Arrive early for good viewing spots",
                "Respect the sacred nature of the procession"
            ]
        )
        self.local_events.append(perahera_event)