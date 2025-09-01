from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from typing import List, Optional, Dict, Any

class MultilingualResponse(BaseModel):
    """Multilingual and accessibility-enhanced response."""
    primary_language_response: str = Field(description="Response in the user's preferred language")
    english_response: str = Field(description="Response in English for fallback")
    sinhala_response: str = Field(description="Response in Sinhala")
    tamil_response: str = Field(description="Response in Tamil")
    audio_description: str = Field(description="Detailed audio-friendly description")
    visual_accessibility_notes: str = Field(description="Visual accessibility adaptations needed")
    simplified_version: str = Field(description="Simplified version for cognitive accessibility")

class LanguageAccessibilityAgent:
    """
    Agent that offers multilingual, voice-assisted, and visually adaptive interfaces.
    Ensures inclusivity for differently abled users and non-locals.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Supported languages in Sri Lanka
        self.supported_languages = {
            "en": "English",
            "si": "Sinhala", 
            "ta": "Tamil",
            "auto": "Auto-detect"
        }
        
        prompt_template = """You are a multilingual accessibility expert for Sri Lanka's public transport system.
        
        Convert the following transport information into accessible, multilingual formats:
        
        Original Information:
        {original_content}
        
        User Preferences:
        - Preferred Language: {preferred_language}
        - Accessibility Needs: {accessibility_needs}
        - User Type: {user_type} (local/tourist/differently_abled)
        
        Provide responses that are:
        1. Culturally appropriate for Sri Lankan context
        2. Accessible for visual, hearing, or cognitive impairments
        3. Tourist-friendly with local context
        4. Clear and actionable
        
        Include proper Sinhala and Tamil translations that are natural and contextual.
        For audio descriptions, include landmarks, sounds, and spatial references.
        For visual accessibility, describe colors, layouts, and important visual cues.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        self.structured_llm = prompt | self.llm.with_structured_output(MultilingualResponse)
    
    async def translate_response(
        self, 
        content: str, 
        preferred_language: str = "en",
        accessibility_needs: List[str] = None,
        user_type: str = "local"
    ) -> MultilingualResponse:
        """
        Translate and adapt content for multilingual and accessibility needs.
        """
        try:
            if accessibility_needs is None:
                accessibility_needs = []
            
            response = await self.structured_llm.ainvoke({
                "original_content": content,
                "preferred_language": preferred_language,
                "accessibility_needs": accessibility_needs,
                "user_type": user_type
            })
            
            return response
            
        except Exception as e:
            print(f"Error in translation/accessibility adaptation: {e}")
            return MultilingualResponse(
                primary_language_response=content,
                english_response=content,
                sinhala_response="සිස්ටම් දෝෂයක්",
                tamil_response="கணினி பிழை",
                audio_description=f"Audio description: {content}",
                visual_accessibility_notes="Standard display format",
                simplified_version=content
            )
    
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of input text.
        """
        try:
            detection_prompt = f"""Detect the language of this text and respond with the language code:
            
            Text: "{text}"
            
            Respond with only one of: en (English), si (Sinhala), ta (Tamil), mixed (multiple languages)
            """
            
            response = await self.llm.ainvoke(detection_prompt)
            detected = response.content.strip().lower()
            
            if detected in ["en", "si", "ta", "mixed"]:
                return detected
            return "en"  # Default to English
            
        except Exception as e:
            print(f"Error in language detection: {e}")
            return "en"
    
    def generate_audio_instructions(self, route_info: Dict) -> str:
        """
        Generate detailed audio instructions for visually impaired users.
        """
        try:
            instructions = []
            
            if route_info.get("transport_mode") == "bus":
                instructions.append(f"Take bus number {route_info.get('route_number', 'unknown')}")
                instructions.append(f"from {route_info.get('origin', 'your location')}")
                instructions.append(f"to {route_info.get('destination', 'your destination')}")
                
                if route_info.get("stops"):
                    instructions.append(f"The bus will make {len(route_info['stops'])} stops")
                    instructions.append("Listen for the conductor's announcements")
                
            elif route_info.get("transport_mode") == "train":
                instructions.append(f"Board the {route_info.get('train_type', '')} train")
                instructions.append(f"on the {route_info.get('line', '')} line")
                instructions.append("Listen for station announcements in Sinhala, Tamil, and English")
            
            # Add landmark-based directions
            if route_info.get("landmarks"):
                instructions.append("Key landmarks along the route:")
                for landmark in route_info["landmarks"]:
                    instructions.append(f"- {landmark}")
            
            # Add safety instructions
            instructions.append("Please hold the handrails and announce your destination clearly")
            
            return " ".join(instructions)
            
        except Exception as e:
            print(f"Error generating audio instructions: {e}")
            return "Audio instructions temporarily unavailable."
    
    def generate_visual_accessibility_format(self, content: Dict) -> Dict:
        """
        Format content for visual accessibility (high contrast, large text, etc.).
        """
        try:
            accessible_format = {
                "high_contrast": True,
                "large_text": True,
                "simplified_layout": True,
                "color_codes": {
                    "bus": "#FFD700",  # Gold for buses
                    "train": "#4169E1",  # Royal blue for trains
                    "walk": "#32CD32",  # Lime green for walking
                    "disruption": "#FF4500",  # Orange red for disruptions
                    "delay": "#FFA500"  # Orange for delays
                },
                "icons": {
                    "bus": "🚌",
                    "train": "🚆", 
                    "walk": "🚶",
                    "time": "🕐",
                    "cost": "💰",
                    "disruption": "⚠️"
                },
                "text_alternatives": {
                    "route_summary": content.get("summary", "Route information"),
                    "duration": f"Journey time: {content.get('duration', 'unknown')}",
                    "cost": f"Estimated cost: {content.get('cost', 'contact operator')}"
                }
            }
            
            return accessible_format
            
        except Exception as e:
            print(f"Error generating visual accessibility format: {e}")
            return {"high_contrast": True, "large_text": True}
    
    async def generate_tourist_friendly_response(self, content: str, origin: str, destination: str) -> str:
        """
        Generate tourist-friendly explanations with cultural context.
        """
        try:
            tourist_prompt = f"""Create a tourist-friendly explanation for this Sri Lankan public transport information:
            
            {content}
            
            Journey: {origin} to {destination}
            
            Include:
            1. Cultural context and etiquette
            2. Practical tips for foreigners
            3. What to expect (sounds, crowds, payment methods)
            4. Safety considerations
            5. Local customs to be aware of
            6. Emergency contacts or phrases
            
            Make it welcoming but informative for first-time visitors to Sri Lanka.
            """
            
            response = await self.llm.ainvoke(tourist_prompt)
            return response.content
            
        except Exception as e:
            print(f"Error generating tourist-friendly response: {e}")
            return f"Tourist information: Travel from {origin} to {destination}. Please ask locals for assistance if needed."
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Return list of supported languages.
        """
        return self.supported_languages
    
    async def generate_emergency_phrases(self, language: str = "en") -> Dict[str, str]:
        """
        Generate emergency phrases in the specified language.
        """
        try:
            emergency_phrases = {
                "en": {
                    "help": "Help me please",
                    "lost": "I am lost",
                    "sick": "I need medical help",
                    "police": "Please call the police", 
                    "hospital": "Take me to a hospital",
                    "embassy": "I need to contact my embassy",
                    "no_understand": "I don't understand",
                    "speak_english": "Do you speak English?"
                },
                "si": {
                    "help": "කරුණාකර මට උදව් කරන්න",
                    "lost": "මම අතරමං වී ඇත",
                    "sick": "මට වෛද්‍ය ආධාර අවශ්‍යයි",
                    "police": "කරුණාකර පොලීසියට කතා කරන්න",
                    "hospital": "මාව රෝහලකට ගෙන යන්න",
                    "embassy": "මගේ තානාපති කාර්යාලය සම්බන්ධ කර ගන්න",
                    "no_understand": "මට තේරෙන්නේ නැහැ",
                    "speak_english": "ඔබ ඉංග්‍රීසි කතා කරනවාද?"
                },
                "ta": {
                    "help": "தயவுசெய்து எனக்கு உதவுங்கள்",
                    "lost": "நான் வழி தெரியாமல் இருக்கிறேன்",
                    "sick": "எனக்கு மருத்துவ உதவி தேவை",
                    "police": "தயவுசெய்து காவல்துறையை அழைக்கவும்",
                    "hospital": "என்னை மருத்துவமனைக்கு அழைத்துச் செல்லுங்கள்",
                    "embassy": "எனது தூதரகத்தை தொடர்பு கொள்ள வேண்டும்",
                    "no_understand": "எனக்குப் புரியவில்லை",
                    "speak_english": "நீங்கள் ஆங்கிலம் பேசுவீர்களா?"
                }
            }
            
            return emergency_phrases.get(language, emergency_phrases["en"])
            
        except Exception as e:
            print(f"Error generating emergency phrases: {e}")
            return {"help": "Help", "lost": "Lost", "sick": "Sick"}
    
    async def process_voice_input(self, audio_text: str, user_language: str = "en") -> Dict:
        """
        Process voice input and return structured response.
        """
        try:
            # Detect language if not specified
            if user_language == "auto":
                user_language = await self.detect_language(audio_text)
            
            voice_prompt = f"""Process this voice input from a Sri Lankan public transport user:
            
            Voice Input: "{audio_text}"
            Detected Language: {user_language}
            
            Extract:
            1. Intent (search_route, get_help, report_issue, ask_question)
            2. Origin location (if mentioned)
            3. Destination location (if mentioned)
            4. Transport preference (if mentioned)
            5. Urgency level (low/medium/high)
            6. Special needs (accessibility, language help, etc.)
            
            Respond in JSON format.
            """
            
            response = await self.llm.ainvoke(voice_prompt)
            
            # Parse the response (would need proper JSON parsing in production)
            return {
                "intent": "search_route",
                "origin": "",
                "destination": "",
                "transport_preference": "",
                "urgency": "medium",
                "special_needs": [],
                "language": user_language,
                "raw_response": response.content
            }
            
        except Exception as e:
            print(f"Error processing voice input: {e}")
            return {
                "intent": "unknown",
                "error": "Voice processing temporarily unavailable",
                "language": user_language
            }