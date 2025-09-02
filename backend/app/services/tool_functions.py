import googlemaps
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from langchain.tools import BaseTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import os
import time

from dotenv import load_dotenv
from pydantic import PrivateAttr

# Load environment variables at the top
load_dotenv()

class GoogleMapsAPITool(BaseTool):
    name: str = "google_maps_api"
    description: str = "Get route information from Google Maps API"
    
    def _run(self, origin: str, destination: str, mode: str = "driving", 
             alternatives: bool = True, departure_time: Optional[datetime] = None) -> Dict:
        """
        Get routes from Google Maps
        """
        # Initialize Google Maps client when needed
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
        
        gmaps = googlemaps.Client(key=api_key)
        
        try:
            if mode == "transit":
                result = gmaps.directions(
                    origin=origin,
                    destination=destination,
                    mode="transit",
                    alternatives=alternatives,
                    departure_time=departure_time or datetime.now()
                )
            else:
                result = gmaps.directions(
                    origin=origin,
                    destination=destination,
                    mode=mode,
                    alternatives=alternatives
                )
            
            return {
                "status": "success",
                "routes": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class SerperWebSearchTool(BaseTool):
    name: str = "serper_web_search"
    description: str = "Search web for local knowledge and route information"
    _search: GoogleSerperAPIWrapper = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search = GoogleSerperAPIWrapper(
            serper_api_key=os.getenv('SERPER_API_KEY')
        )
    
    def _run(self, query: str, location: Optional[str] = None) -> Dict:
        """
        Search for local knowledge about routes and areas
        """
        try:
            # Enhance query with location if provided
            enhanced_query = f"{query} {location}" if location else query
            
            # Get search results
            results = self._search.run(enhanced_query)
            
            # Also search for traffic and disruption info
            traffic_query = f"traffic conditions disruptions {location or query}"
            traffic_results = self._search.run(traffic_query)
            
            return {
                "status": "success",
                "general_info": results,
                "traffic_info": traffic_results,
                "timestamp": datetime.now().isoformat(),
                "query": enhanced_query
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class FareDatabaseTool(BaseTool):
    name: str = "fare_database"
    description: str = "Query fare information from database"
    _client: MongoClient = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MongoDB client with retry logic and error handling"""
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if not connection_string:
            print("⚠️  MONGODB_CONNECTION_STRING not set. Fare database tool will be disabled.")
            return
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempting MongoDB connection (attempt {attempt + 1}/{max_retries})...")
                
                # Set connection timeout to prevent long DNS resolution
                self._client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=10000,  # 10 second timeout
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    maxPoolSize=1,  # Minimal connection pool for tool usage
                    retryWrites=True
                )
                
                # Test the connection
                self._client.admin.command('ping')
                print("✅ MongoDB connection established successfully")
                break
                
            except Exception as e:
                print(f"❌ MongoDB connection attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("❌ All MongoDB connection attempts failed. Fare database tool will be disabled.")
                    self._client = None
    
    def _run(self, mode: str, source: str, destination: str, vehicle_type: str = None) -> Dict:
        """
        Query fare information from database for a specific route
        """
        if not self._client:
            return {
                "status": "error",
                "error": "MongoDB connection not available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Create a query string from the parameters
            query = f"{mode} fare from {source} to {destination}"
            if vehicle_type:
                query += f" via {vehicle_type}"
            
            # Your database query logic here
            # For now, return a mock response with the expected structure
            return {
                "status": "success",
                "fares": [
                    {
                        "base_fare": 5.0,
                        "vehicle_type": vehicle_type or mode,
                        "source": source,
                        "destination": destination
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def __del__(self):
        """Clean up MongoDB connection"""
        if self._client:
            try:
                self._client.close()
            except:
                pass

class UserPreferenceTool(BaseTool):
    name: str = "user_preference"
    description: str = "Manage user preferences in MongoDB"
    _client: MongoClient = PrivateAttr()
    _db: Any = PrivateAttr()
    _preferences_collection: Any = PrivateAttr()
    _history_collection: Any = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
        self._db = self._client['transit_companion_db']
        self._preferences_collection = self._db['user_preferences']
        self._history_collection = self._db['user_history']
    
    def _run(self, user_id: str, action: str = "get", preferences: Optional[Dict] = None, 
             current_selection: Optional[Dict] = None) -> Dict:
        """
        Main entry point for the tool - implements the abstract _run method
        """
        if action == "get":
            return self.get_preferences(user_id)
        elif action == "update" and preferences and current_selection:
            return self.update_preferences(user_id, preferences, current_selection)
        else:
            return {
                "status": "error",
                "error": "Invalid action or missing parameters",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        try:
            preferences = self.preferences_collection.find_one({"user_id": user_id})
            if preferences:
                preferences['_id'] = str(preferences['_id'])
                return {
                    "status": "success",
                    "preferences": preferences,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Return default preferences
                default_prefs = {
                    "user_id": user_id,
                    "preferred_transit_modes": ["bus", "train"],
                    "max_walking_distance": 1.0,
                    "budget_preference": "medium",
                    "time_vs_cost_weight": 0.5,
                    "comfort_preference": 0.7,
                    "accessibility_needs": [],
                    "avoid_preferences": [],
                    "last_updated": datetime.now()
                }
                return {
                    "status": "success",
                    "preferences": default_prefs,
                    "is_default": True,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def update_preferences(self, user_id: str, preferences: Dict, 
                          current_selection: Dict) -> Dict:
        """Update user preferences based on current selection"""
        try:
            # Log current selection to history
            self.history_collection.insert_one({
                "user_id": user_id,
                "selection": current_selection,
                "timestamp": datetime.now()
            })
            
            # Update preferences with learning algorithm
            updated_prefs = self._learn_from_selection(preferences, current_selection)
            updated_prefs["last_updated"] = datetime.now()
            
            # Upsert preferences
            self.preferences_collection.update_one(
                {"user_id": user_id},
                {"$set": updated_prefs},
                upsert=True
            )
            
            return {
                "status": "success",
                "updated_preferences": updated_prefs,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _learn_from_selection(self, current_prefs: Dict, selection: Dict) -> Dict:
        """Simple learning algorithm to update preferences"""
        learning_rate = 0.1
        
        # Update time vs cost preference based on selection
        if "selected_for_time" in selection:
            if selection["selected_for_time"]:
                current_prefs["time_vs_cost_weight"] = min(1.0, 
                    current_prefs["time_vs_cost_weight"] + learning_rate)
            else:
                current_prefs["time_vs_cost_weight"] = max(0.0, 
                    current_prefs["time_vs_cost_weight"] - learning_rate)
        
        # Update preferred modes based on selection
        if "selected_mode" in selection:
            selected_mode = selection["selected_mode"]
            if selected_mode not in current_prefs["preferred_transit_modes"]:
                current_prefs["preferred_transit_modes"].append(selected_mode)
        
        return current_prefs

class DisruptionDatabaseTool(BaseTool):
    name: str = "disruption_database"
    description: str = "Manage disruption reports in MongoDB"
    _client: MongoClient = PrivateAttr()
    _db: Any = PrivateAttr()
    _disruptions_collection: Any = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
        self._db = self._client['travel_system']
        self._disruptions_collection = self._db['disruptions']
    
    def _run(self, action: str = "get", route_area: Optional[str] = None, 
             active_only: bool = True, disruption_data: Optional[Dict] = None) -> Dict:
        """
        Main entry point for the tool - implements the abstract _run method
        """
        if action == "get" and route_area:
            return self.get_disruptions(route_area, active_only)
        elif action == "report" and disruption_data:
            return self.report_disruption(disruption_data)
        else:
            return {
                "status": "error",
                "error": "Invalid action or missing parameters",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_disruptions(self, route_area: str, active_only: bool = True) -> Dict:
        """Get disruptions for a specific area"""
        try:
            query = {"location": {"$regex": route_area, "$options": "i"}}
            
            if active_only:
                # Only get disruptions from last 4 hours
                four_hours_ago = datetime.now().timestamp() - (4 * 3600)
                query["timestamp"] = {"$gte": four_hours_ago}
            
            disruptions = list(self._disruptions_collection.find(query))
            
            for disruption in disruptions:
                disruption['_id'] = str(disruption['_id'])
            
            return {
                "status": "success",
                "disruptions": disruptions,
                "count": len(disruptions),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def report_disruption(self, disruption_data: Dict) -> Dict:
        """Report a new disruption"""
        try:
            disruption_data["timestamp"] = datetime.now()
            disruption_data["disruption_id"] = f"dis_{datetime.now().timestamp()}"
            
            result = self.disruptions_collection.insert_one(disruption_data)
            
            return {
                "status": "success",
                "disruption_id": disruption_data["disruption_id"],
                "inserted_id": str(result.inserted_id),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }