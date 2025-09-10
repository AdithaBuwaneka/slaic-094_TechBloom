# Multilingual Support Service for Sri Lankan Languages
# Basic implementation for SLAIC 2025 Language & Accessibility requirements

from typing import Dict, Any, Optional
from enum import Enum

class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    SINHALA = "si" 
    TAMIL = "ta"

class MultilingualService:
    """
    Basic multilingual support service for Sri Lankan languages
    Supports English, Sinhala, and Tamil as required by SLAIC 2025
    """
    
    def __init__(self):
        self.translations = self._load_translations()
        self.default_language = SupportedLanguage.ENGLISH
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load basic translations for common transit terms"""
        return {
            # Welcome messages
            "welcome": {
                "en": "Welcome to Transit Companion",
                "si": "ගමනාගමන සහකරුට සාදරයෙන් පිළිගනිමු", 
                "ta": "போக்குவரத்து துணைவனுக்கு வரவேற்கிறோம்"
            },
            
            # Transportation modes
            "bus": {
                "en": "Bus",
                "si": "බස්",
                "ta": "பேருந்து"
            },
            "train": {
                "en": "Train", 
                "si": "දුම්රිය",
                "ta": "ரயில்"
            },
            "tuk_tuk": {
                "en": "Tuk-tuk",
                "si": "ත්‍රිරෝද රථය",
                "ta": "முச்சக்கர வண்டி"
            },
            
            # Common directions
            "start": {
                "en": "Starting point",
                "si": "ආරම්භක ස්ථානය", 
                "ta": "தொடக்க இடம்"
            },
            "destination": {
                "en": "Destination",
                "si": "ගමනාන්තය",
                "ta": "இலக்கு"
            },
            "route": {
                "en": "Route",
                "si": "මාර්ගය",
                "ta": "வழி"
            },
            
            # Status messages
            "on_time": {
                "en": "On time",
                "si": "නියමිත වේලාවට",
                "ta": "சரியான நேரத்தில்"
            },
            "delayed": {
                "en": "Delayed", 
                "si": "ප්‍රමාද වී ඇත",
                "ta": "தாமதமாக"
            },
            "cancelled": {
                "en": "Cancelled",
                "si": "අවලංගු කර ඇත", 
                "ta": "ரத்து செய்யப்பட்டது"
            },
            
            # Time and fare
            "departure_time": {
                "en": "Departure time",
                "si": "පිටත් වන වේලාව",
                "ta": "புறப்படும் நேரம்"
            },
            "fare": {
                "en": "Fare",
                "si": "ගාස්තුව", 
                "ta": "கட்டணம்"
            },
            "duration": {
                "en": "Duration",
                "si": "කාලසීමාව",
                "ta": "காலம்"
            },
            
            # Common locations in Sri Lanka
            "colombo": {
                "en": "Colombo",
                "si": "කොළඹ",
                "ta": "கொழும்பு"
            },
            "kandy": {
                "en": "Kandy", 
                "si": "මහනුවර",
                "ta": "கண்டி"
            },
            "galle": {
                "en": "Galle",
                "si": "ගාල්ල",
                "ta": "காலி"
            },
            "anuradhapura": {
                "en": "Anuradhapura",
                "si": "අනුරාධපුරය",
                "ta": "அனுராதபுரம்"
            },
            
            # Error messages
            "error_route_not_found": {
                "en": "Route not found",
                "si": "මාර්ගය හමු නොවීය",
                "ta": "வழி கிடைக்கவில்லை"
            },
            "error_service_unavailable": {
                "en": "Service temporarily unavailable", 
                "si": "සේවාව තාවකාලිකව ලබා ගත නොහැක",
                "ta": "சேவை தற்காலிகமாக கிடைக்கவில்லை"
            }
        }
    
    def translate(self, key: str, language: str = None) -> str:
        """
        Translate a key to the specified language
        
        Args:
            key: Translation key
            language: Target language code (en, si, ta)
            
        Returns:
            Translated string or original key if translation not found
        """
        if language is None:
            language = self.default_language
            
        if key in self.translations:
            return self.translations[key].get(language, self.translations[key].get("en", key))
        
        return key
    
    def translate_response(self, response_data: Dict[str, Any], language: str = None) -> Dict[str, Any]:
        """
        Translate common fields in API responses
        
        Args:
            response_data: Response dictionary to translate
            language: Target language code
            
        Returns:
            Translated response data
        """
        if language is None or language == "en":
            return response_data
            
        translated_response = response_data.copy()
        
        # Translate common fields if they exist
        if "message" in translated_response:
            translated_response["message"] = self.translate(translated_response["message"], language)
            
        if "status" in translated_response:
            translated_response["status"] = self.translate(translated_response["status"], language)
            
        # Translate transportation data if present
        if "data" in translated_response and isinstance(translated_response["data"], list):
            for item in translated_response["data"]:
                if isinstance(item, dict):
                    # Translate route names containing city names
                    if "route" in item or "route_name" in item:
                        route_field = "route" if "route" in item else "route_name"
                        original_route = item[route_field]
                        translated_route = self._translate_route_name(original_route, language)
                        item[route_field] = translated_route
                    
                    # Translate status fields
                    if "status" in item:
                        item["status"] = self.translate(item["status"], language)
        
        return translated_response
    
    def _translate_route_name(self, route_name: str, language: str) -> str:
        """
        Translate route names containing city names
        
        Args:
            route_name: Original route name (e.g., "Colombo - Kandy")
            language: Target language code
            
        Returns:
            Translated route name
        """
        translated_route = route_name
        
        # Replace city names in route descriptions
        city_translations = {
            "Colombo": self.translate("colombo", language),
            "Kandy": self.translate("kandy", language), 
            "Galle": self.translate("galle", language),
            "Anuradhapura": self.translate("anuradhapura", language)
        }
        
        for english_city, translated_city in city_translations.items():
            translated_route = translated_route.replace(english_city, translated_city)
        
        return translated_route
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages with their names"""
        return {
            "en": "English",
            "si": "සිංහල (Sinhala)", 
            "ta": "தமிழ் (Tamil)"
        }
    
    def validate_language(self, language: str) -> bool:
        """Validate if language code is supported"""
        return language in [lang.value for lang in SupportedLanguage]

# Initialize global service instance
multilingual_service = MultilingualService()