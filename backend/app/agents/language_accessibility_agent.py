from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timedelta, timezone
import uuid

from app.agents.base_agent import BaseAgent
from app.models.accessibility import (
    AccessibilityProfile, TransportAccessibility, AccessibilityAlert,
    LanguageTranslation, AccessibilityRecommendation, EmergencyAccessibilityInfo,
    AccessibilityFeedback, Language, AccessibilityNeed, DisabilityType,
    TransportMode
)
from app.models.transport_data import Location
from app.core.database import db


class LanguageAccessibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="language_accessibility_agent",
            name="Language & Accessibility Agent",
            priority_weight=0.8
        )
        self.accessibility_data = self._initialize_accessibility_data()
        self.translations = self._initialize_translations()
        self.emergency_info = self._initialize_emergency_info()
        
    def _initialize_accessibility_data(self) -> Dict[str, Any]:
        """Initialize accessibility data for Sri Lankan transport operators"""
        return {
            "SLTB": {
                "wheelchair_accessible": True,
                "low_floor_entry": True,
                "audio_announcements": True,
                "visual_displays": False,
                "staff_assistance_available": True,
                "priority_seating": True,
                "designated_wheelchair_spaces": 2,
                "multilingual_announcements": [Language.SINHALA, Language.ENGLISH],
                "accessibility_rating": 3.2,
                "braille_signage": False,
                "mobile_app_accessible": False
            },
            "CTB": {
                "wheelchair_accessible": False,
                "low_floor_entry": False,
                "audio_announcements": True,
                "visual_displays": False,
                "staff_assistance_available": True,
                "priority_seating": True,
                "designated_wheelchair_spaces": 0,
                "multilingual_announcements": [Language.SINHALA, Language.TAMIL, Language.ENGLISH],
                "accessibility_rating": 2.1,
                "braille_signage": False,
                "mobile_app_accessible": False
            },
            "Sri Lanka Railways": {
                "wheelchair_accessible": True,
                "low_floor_entry": False,
                "audio_announcements": True,
                "visual_displays": True,
                "staff_assistance_available": True,
                "priority_seating": True,
                "designated_wheelchair_spaces": 1,
                "multilingual_announcements": [Language.SINHALA, Language.TAMIL, Language.ENGLISH],
                "accessibility_rating": 3.7,
                "braille_signage": True,
                "platform_level_boarding": False,
                "elevator_access": True,
                "mobile_app_accessible": True
            },
            "PickMe": {
                "wheelchair_accessible": True,
                "low_floor_entry": True,
                "audio_announcements": False,
                "visual_displays": True,
                "staff_assistance_available": True,
                "priority_seating": False,
                "designated_wheelchair_spaces": 1,
                "multilingual_announcements": [Language.SINHALA, Language.ENGLISH],
                "accessibility_rating": 4.1,
                "mobile_app_accessible": True,
                "wheelchair_specific_vehicles": True
            },
            "Uber": {
                "wheelchair_accessible": True,
                "low_floor_entry": True,
                "audio_announcements": False,
                "visual_displays": True,
                "staff_assistance_available": False,
                "priority_seating": False,
                "designated_wheelchair_spaces": 1,
                "multilingual_announcements": [Language.ENGLISH],
                "accessibility_rating": 3.8,
                "mobile_app_accessible": True,
                "wheelchair_specific_vehicles": True
            }
        }
    
    def _initialize_translations(self) -> Dict[str, Dict[Language, str]]:
        """Initialize common transport-related translations"""
        return {
            "welcome": {
                Language.ENGLISH: "Welcome to Sri Lankan Transit Companion",
                Language.SINHALA: "ශ්‍රී ලංකා ප්‍රවාහන සහයකයාට සාදරයෙන් පිළිගනිමු",
                Language.TAMIL: "இலங்கை போக்குவரத்து உதவியாளருக்கு வரவேற்கிறோம்"
            },
            "boarding_assistance": {
                Language.ENGLISH: "Boarding assistance available upon request",
                Language.SINHALA: "ඉල්ලීම පරිදි නැගීමේ සහාය ලබා ගත හැක",
                Language.TAMIL: "கோரிக்கையின் பேரில் ஏறுதல் உதவி கிடைக்கும்"
            },
            "wheelchair_accessible": {
                Language.ENGLISH: "Wheelchair accessible vehicle",
                Language.SINHALA: "රෝද පුටු ප්‍රවේශ්‍ය වාහනය",
                Language.TAMIL: "சக்கர நாற்காலி அணுகக்கூடிய வாகனம்"
            },
            "priority_seating": {
                Language.ENGLISH: "Priority seating for elderly and disabled passengers",
                Language.SINHALA: "වැඩිහිටි සහ ආබාධිත මගීන් සඳහා ප්‍රමුඛ ආසන",
                Language.TAMIL: "முதியவர்கள் மற்றும் ஊனமுற்ற பயணிகளுக்கு முன்னுரிமை இருக்கைகள்"
            },
            "audio_announcement": {
                Language.ENGLISH: "Audio announcements available",
                Language.SINHALA: "ශ්‍රව්‍ය නිවේදන ලබා ගත හැක",
                Language.TAMIL: "ஒலி அறிவிப்புகள் கிடைக்கும்"
            },
            "emergency_help": {
                Language.ENGLISH: "Emergency assistance: Press the emergency button or call 119",
                Language.SINHALA: "හදිසි සහාය: හදිසි බොත්තම ඔබන්න හෝ 119 අමතන්න",
                Language.TAMIL: "அவசர உதவி: அவசர பொத்தானை அழுத்தவும் அல்லது 119 ஐ அழைக்கவும்"
            },
            "next_stop": {
                Language.ENGLISH: "Next stop",
                Language.SINHALA: "ඊළඟ නැවතුම",
                Language.TAMIL: "அடுத்த நிறுத்தம்"
            }
        }
    
    def _initialize_emergency_info(self) -> Dict[str, Any]:
        """Initialize emergency accessibility information"""
        return {
            "general_emergency": {
                "hotline": "119",
                "disability_support": "011-2696211",
                "text_emergency": "119 (SMS)",
                "sign_language_service": False
            },
            "transport_emergencies": {
                "railway": {
                    "emergency_contacts": ["011-2421281", "011-2448048"],
                    "wheelchair_evacuation": True,
                    "audio_evacuation_alerts": True,
                    "visual_evacuation_alerts": True
                },
                "bus": {
                    "emergency_contacts": ["011-2587636"],
                    "wheelchair_evacuation": False,
                    "audio_evacuation_alerts": True,
                    "visual_evacuation_alerts": False
                }
            }
        }

    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process accessibility and language requests"""
        try:
            request_type = payload.get("request_type")
            data = payload.get("data", {})
            
            if request_type == "get_accessibility_info":
                return await self._get_accessibility_info(data)
            elif request_type == "translate_text":
                return await self._translate_text(data)
            elif request_type == "assess_accessibility":
                return await self._assess_route_accessibility(data)
            elif request_type == "get_accessibility_alerts":
                return await self._get_accessibility_alerts(data)
            elif request_type == "create_accessibility_profile":
                return await self._create_accessibility_profile(data)
            elif request_type == "get_emergency_info":
                return await self._get_emergency_accessibility_info(data)
            elif request_type == "submit_accessibility_feedback":
                return await self._submit_accessibility_feedback(data)
            else:
                return {"success": False, "error": f"Unknown request type: {request_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_accessibility_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get accessibility information for transport operators"""
        operator = payload.get("operator")
        transport_mode = payload.get("transport_mode")
        
        if operator and operator in self.accessibility_data:
            accessibility_info = self.accessibility_data[operator].copy()
            
            # Create TransportAccessibility model
            transport_accessibility = TransportAccessibility(
                transport_mode=TransportMode(transport_mode) if transport_mode else TransportMode.BUS,
                operator=operator,
                **accessibility_info
            )
            
            # Store in database
            await db.database.transport_accessibility.update_one(
                {"operator": operator, "transport_mode": transport_mode},
                {"$set": transport_accessibility.dict()},
                upsert=True
            )
            
            return {
                "success": True,
                "accessibility_info": transport_accessibility.dict()
            }
        
        return {"success": False, "error": "Operator not found"}

    async def _translate_text(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Translate text between supported languages"""
        text = payload.get("text", "")
        from_lang = Language(payload.get("from_language", "english"))
        to_lang = Language(payload.get("to_language", "sinhala"))
        context = payload.get("context", "general")
        
        # Check if we have a predefined translation
        for key, translations in self.translations.items():
            if text.lower() in translations.get(from_lang, "").lower():
                translated_text = translations.get(to_lang, text)
                
                # Create translation record
                translation = LanguageTranslation(
                    translation_id=str(uuid.uuid4()),
                    original_language=from_lang,
                    target_language=to_lang,
                    original_text=text,
                    translated_text=translated_text,
                    context=context,
                    confidence_score=0.95
                )
                
                # Store translation
                await db.database.language_translations.insert_one(translation.dict())
                
                return {
                    "success": True,
                    "translation": translation.dict()
                }
        
        # Fallback: Return original text with note
        translation = LanguageTranslation(
            translation_id=str(uuid.uuid4()),
            original_language=from_lang,
            target_language=to_lang,
            original_text=text,
            translated_text=f"[Translation not available] {text}",
            context=context,
            confidence_score=0.1
        )
        
        await db.database.language_translations.insert_one(translation.dict())
        
        return {
            "success": True,
            "translation": translation.dict(),
            "note": "Translation service limited - expanding coverage"
        }

    async def _assess_route_accessibility(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assess accessibility of a specific route for a user"""
        route_id = payload.get("route_id")
        user_id = payload.get("user_id")
        accessibility_needs = payload.get("accessibility_needs", [])
        
        # Get user's accessibility profile
        user_profile = await db.database.accessibility_profiles.find_one({"user_id": user_id})
        
        if not user_profile:
            # Create basic profile from payload
            profile_data = {
                "user_id": user_id,
                "accessibility_needs": [AccessibilityNeed(need) for need in accessibility_needs],
                "primary_language": Language(payload.get("language", "english"))
            }
            user_profile = AccessibilityProfile(**profile_data)
            await db.database.accessibility_profiles.insert_one(user_profile.dict())
        
        # Get route information (mock data for demonstration)
        operators = payload.get("operators", ["SLTB", "CTB"])
        accessibility_scores = {}
        recommendations = []
        
        for operator in operators:
            if operator in self.accessibility_data:
                operator_data = self.accessibility_data[operator]
                score = self._calculate_accessibility_score(operator_data, accessibility_needs)
                accessibility_scores[operator] = score
                
                if score < 5.0:
                    recommendations.extend(self._generate_accessibility_recommendations(operator, operator_data, accessibility_needs))
        
        # Create recommendation object
        recommendation = AccessibilityRecommendation(
            recommendation_id=str(uuid.uuid4()),
            user_id=user_id,
            route_id=route_id,
            accessibility_score=max(accessibility_scores.values()) if accessibility_scores else 0.0,
            accessibility_breakdown=accessibility_scores,
            boarding_recommendations=recommendations,
            assistance_notification_time=30 if "mobility_assistance" in accessibility_needs else None
        )
        
        # Store recommendation
        await db.database.accessibility_recommendations.insert_one(recommendation.dict())
        
        return {
            "success": True,
            "accessibility_assessment": recommendation.dict()
        }

    def _calculate_accessibility_score(self, operator_data: Dict[str, Any], needs: List[str]) -> float:
        """Calculate accessibility score based on needs and operator capabilities"""
        max_score = 10.0
        score = operator_data.get("accessibility_rating", 5.0)
        
        # Adjust score based on specific needs
        for need in needs:
            if need == "wheelchair" and not operator_data.get("wheelchair_accessible", False):
                score -= 3.0
            elif need == "visual_impairment" and not operator_data.get("audio_announcements", False):
                score -= 2.0
            elif need == "hearing_impairment" and not operator_data.get("visual_displays", False):
                score -= 2.0
            elif need == "mobility_assistance" and not operator_data.get("staff_assistance_available", False):
                score -= 1.5
        
        return max(0.0, min(max_score, score))

    def _generate_accessibility_recommendations(self, operator: str, operator_data: Dict[str, Any], needs: List[str]) -> List[str]:
        """Generate specific accessibility recommendations"""
        recommendations = []
        
        if "wheelchair" in needs:
            if not operator_data.get("wheelchair_accessible", False):
                recommendations.append(f"Consider alternative operator - {operator} not wheelchair accessible")
            else:
                recommendations.append("Call ahead to ensure wheelchair space availability")
        
        if "visual_impairment" in needs:
            if operator_data.get("audio_announcements", False):
                recommendations.append("Audio announcements available - sit near speakers")
            else:
                recommendations.append("Request staff assistance for stop announcements")
        
        if "hearing_impairment" in needs:
            if operator_data.get("visual_displays", False):
                recommendations.append("Visual displays available for route information")
            else:
                recommendations.append("Download route map and track progress manually")
        
        if operator_data.get("staff_assistance_available", False):
            recommendations.append("Staff assistance available - inform conductor of your needs")
        
        return recommendations

    async def _get_accessibility_alerts(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get current accessibility alerts"""
        transport_mode = payload.get("transport_mode")
        location = payload.get("location")
        
        # Generate some sample alerts
        alerts = [
            AccessibilityAlert(
                alert_id=str(uuid.uuid4()),
                transport_mode=TransportMode.TRAIN,
                operator="Sri Lanka Railways",
                alert_type="equipment_failure",
                accessibility_impact=[AccessibilityNeed.WHEELCHAIR],
                severity="medium",
                title={
                    Language.ENGLISH: "Elevator out of service at Colombo Fort",
                    Language.SINHALA: "කොළඹ කොටුවේ විදුලි සෝපානය ක්‍රියා නොකරයි",
                    Language.TAMIL: "கொழும்பு கோட்டையில் லிப்ட் இயங்கவில்லை"
                },
                description={
                    Language.ENGLISH: "Platform elevator temporarily unavailable. Staff assistance available for wheelchair users.",
                    Language.SINHALA: "වේදිකා විදුලි සෝපානය තාවකාලිකව නොමැත. රෝද පුටු භාවිතා කරන්නන් සඳහා කාර්ය මණ්ඩල සහාය ලබා ගත හැක.",
                    Language.TAMIL: "மேடை லிப்ட் தற்காலிகமாக கிடைக்கவில்லை. சக்கர நாற்காலி பயனர்களுக்கு ஊழியர் உதவி கிடைக்கும்."
                },
                start_time=datetime.now(timezone.utc),
                estimated_end_time=datetime.now(timezone.utc) + timedelta(hours=6)
            ),
            AccessibilityAlert(
                alert_id=str(uuid.uuid4()),
                transport_mode=TransportMode.BUS,
                operator="SLTB",
                alert_type="service_disruption",
                accessibility_impact=[AccessibilityNeed.VISUAL_IMPAIRMENT],
                severity="low",
                title={
                    Language.ENGLISH: "Audio announcement system maintenance",
                    Language.SINHALA: "ශ්‍රව්‍ය නිවේදන පද්ධතිය නඩත්තුව",
                    Language.TAMIL: "ஒலி அறிவிப்பு அமைப்பு பராமரிப்பு"
                },
                description={
                    Language.ENGLISH: "Audio announcements may be intermittent on Route 138. Conductors will provide verbal updates.",
                    Language.SINHALA: "138 මාර්ගයේ ශ්‍රව්‍ය නිවේදන කඩිකඩීව පැමිණිය හැක. කොන්දොස්තරවරුන් වාචික යාවත්කාලීන කිරීම් සපයන්නේ ය.",
                    Language.TAMIL: "பாதை 138 இல் ஒலி அறிவிப்புகள் இடைவிடாமல் இருக்கலாம். நடத்துநர்கள் வாய்மொழி புதுப்பிப்புகளை வழங்குவார்கள்."
                },
                start_time=datetime.now(timezone.utc) - timedelta(hours=2),
                estimated_end_time=datetime.now(timezone.utc) + timedelta(hours=4)
            )
        ]
        
        # Store alerts in database
        for alert in alerts:
            await db.database.accessibility_alerts.update_one(
                {"alert_id": alert.alert_id},
                {"$set": alert.dict()},
                upsert=True
            )
        
        return {
            "success": True,
            "alerts": [alert.dict() for alert in alerts],
            "alert_count": len(alerts)
        }

    async def _create_accessibility_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update accessibility profile"""
        user_id = payload.get("user_id")
        
        # Create profile from payload
        profile_data = {
            "user_id": user_id,
            "primary_language": Language(payload.get("primary_language", "english")),
            "accessibility_needs": [AccessibilityNeed(need) for need in payload.get("accessibility_needs", [])],
            "disability_types": [DisabilityType(dt) for dt in payload.get("disability_types", [])],
            "uses_wheelchair": payload.get("uses_wheelchair", False),
            "uses_walking_aid": payload.get("uses_walking_aid", False),
            "uses_guide_dog": payload.get("uses_guide_dog", False),
            "prefers_audio_announcements": payload.get("prefers_audio_announcements", False),
            "needs_visual_alerts": payload.get("needs_visual_alerts", False),
            "uses_screen_reader": payload.get("uses_screen_reader", False),
            "requires_boarding_assistance": payload.get("requires_boarding_assistance", False),
            "requires_navigation_assistance": payload.get("requires_navigation_assistance", False),
            "needs_simplified_instructions": payload.get("needs_simplified_instructions", False)
        }
        
        profile = AccessibilityProfile(**profile_data)
        
        # Store in database
        await db.database.accessibility_profiles.update_one(
            {"user_id": user_id},
            {"$set": profile.dict()},
            upsert=True
        )
        
        return {
            "success": True,
            "profile": profile.dict()
        }

    async def _get_emergency_accessibility_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get emergency accessibility information"""
        transport_mode = payload.get("transport_mode", "general")
        language = Language(payload.get("language", "english"))
        
        # Get emergency info for the specific transport mode
        if transport_mode in self.emergency_info.get("transport_emergencies", {}):
            emergency_data = self.emergency_info["transport_emergencies"][transport_mode]
        else:
            emergency_data = self.emergency_info["general_emergency"]
        
        # Create emergency info object
        emergency_info = EmergencyAccessibilityInfo(
            info_id=str(uuid.uuid4()),
            transport_mode=TransportMode(transport_mode) if transport_mode != "general" else TransportMode.BUS,
            operator="General",
            emergency_procedures={
                language: [
                    self.translations["emergency_help"][language],
                    f"Emergency hotline: {emergency_data.get('hotline', '119')}",
                    f"Disability support: {emergency_data.get('disability_support', 'Not available')}"
                ]
            },
            evacuation_assistance={
                AccessibilityNeed.WHEELCHAIR: ["Staff assistance available for evacuation", "Designated wheelchair evacuation routes"],
                AccessibilityNeed.VISUAL_IMPAIRMENT: ["Audio evacuation alerts", "Staff guidance to exits"],
                AccessibilityNeed.HEARING_IMPAIRMENT: ["Visual evacuation alerts", "Vibrating alert devices where available"]
            },
            emergency_contacts=[
                {"type": "General Emergency", "number": "119"},
                {"type": "Police", "number": "118"},
                {"type": "Disability Support", "number": "011-2696211"}
            ],
            emergency_communication_methods=["audio", "visual", "text"],
            emergency_equipment_locations={
                "first_aid_kits": ["Front car", "Middle car", "Staff office"],
                "emergency_phones": ["Platform 1", "Platform 2", "Main hall"],
                "defibrillators": ["Station office", "Platform 1"]
            },
            accessible_emergency_exits=["Main entrance", "Platform exit 1", "Platform exit 2"]
        )
        
        # Store in database
        await db.database.emergency_accessibility_info.update_one(
            {"transport_mode": transport_mode, "operator": "General"},
            {"$set": emergency_info.dict()},
            upsert=True
        )
        
        return {
            "success": True,
            "emergency_info": emergency_info.dict()
        }

    async def _submit_accessibility_feedback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit accessibility feedback"""
        feedback_data = {
            "feedback_id": str(uuid.uuid4()),
            "user_id": payload.get("user_id"),
            "transport_mode": TransportMode(payload.get("transport_mode", "bus")),
            "operator": payload.get("operator"),
            "route_id": payload.get("route_id"),
            "accessibility_rating": payload.get("accessibility_rating", 3),
            "specific_ratings": payload.get("specific_ratings", {}),
            "accessibility_features_used": [AccessibilityNeed(need) for need in payload.get("accessibility_features_used", [])],
            "issues_encountered": payload.get("issues_encountered", []),
            "positive_experiences": payload.get("positive_experiences", []),
            "suggested_improvements": payload.get("suggested_improvements", []),
            "trip_date": datetime.fromisoformat(payload.get("trip_date")) if payload.get("trip_date") else datetime.now(timezone.utc),
            "time_of_day": payload.get("time_of_day", "morning"),
            "crowd_level": payload.get("crowd_level", "normal"),
            "feedback_text": payload.get("feedback_text")
        }
        
        feedback = AccessibilityFeedback(**feedback_data)
        
        # Store feedback
        await db.database.accessibility_feedback.insert_one(feedback.dict())
        
        return {
            "success": True,
            "feedback": feedback.dict(),
            "message": "Thank you for your accessibility feedback!"
        }