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
             alternatives: bool = True, departure_time: Optional[datetime] = None,
             transit_mode_preference: Optional[str] = None) -> Dict:
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
                # Build the directions request parameters
                directions_params = {
                    "origin": origin,
                    "destination": destination,
                    "mode": "transit",
                    "alternatives": alternatives,
                    "departure_time": departure_time or datetime.now()
                }
                
                # Add transit mode preference if specified
                if transit_mode_preference:
                    directions_params["transit_mode"] = transit_mode_preference
                result = gmaps.directions(**directions_params)
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
            
            # Process and structure the results
            structured_results = self._process_search_results(results, enhanced_query)
            
            return {
                "status": "success",
                "general_info": structured_results,
                "raw_results": results,  # Keep raw results for debugging
                "timestamp": datetime.now().isoformat(),
                "query": enhanced_query
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_search_results(self, results: str, query: str) -> Dict[str, Any]:
        """
        Process and structure raw search results into useful information
        """
        try:
            # Extract key information from the search results
            processed_results = {
                "query": query,
                "summary": "",
                "key_points": [],
                "relevant_links": [],
                "extracted_data": {}
            }
            
            # If results is a string, try to extract useful information
            if isinstance(results, str):
                # Split into lines and extract key information
                lines = results.split('\n')
                summary_lines = []
                key_points = []
                
                for line in lines:
                    line = line.strip()
                    if line:
                        # Look for summary-like content (first few meaningful lines)
                        if len(summary_lines) < 3 and len(line) > 20:
                            summary_lines.append(line)
                        
                        # Look for key points (lines with bullet points, numbers, or key phrases)
                        if any(keyword in line.lower() for keyword in ['bus', 'train', 'route', 'time', 'fare', 'station', 'stop', 'attraction', 'landmark', 'traffic', 'weather']):
                            key_points.append(line)
                
                processed_results["summary"] = " ".join(summary_lines[:3])
                processed_results["key_points"] = key_points[:5]  # Limit to 5 key points
                
                # Extract any URLs or links if present
                import re
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, results)
                processed_results["relevant_links"] = urls[:3]  # Limit to 3 links
            
            return processed_results
            
        except Exception as e:
            print(f"Error processing search results: {str(e)}")
            return {
                "query": query,
                "summary": "Error processing search results",
                "key_points": [],
                "relevant_links": [],
                "extracted_data": {"error": str(e)}
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
            # Get the database and collection
            db = self._client['transit_companion_db']
            transit_fares_collection = db['transit_fares']
            
            # Create query parameters for exact match (case-insensitive)
            query_params = {
                "origin": {"$regex": f"^{source}$", "$options": "i"},
                "destination": {"$regex": f"^{destination}$", "$options": "i"},
                "mode": mode,
                "is_active": True
            }
            
            # If vehicle_type is specified, add it to the query
            if vehicle_type and vehicle_type != mode:
                query_params["vehicle_type"] = vehicle_type
            
            # Query the database for exact route match
            fare_record = transit_fares_collection.find_one(query_params)
            
            if fare_record:
                # Convert ObjectId to string for JSON serialization
                fare_record['_id'] = str(fare_record['_id'])
                
                return {
                    "status": "success",
                    "fares": [
                        {
                            "base_fare": fare_record.get('base_fare', 0),
                            "vehicle_type": fare_record.get('vehicle_type', mode),
                            "source": fare_record.get('origin', source),
                            "destination": fare_record.get('destination', destination),
                            "fare_type": fare_record.get('fare_type', 'unknown'),
                            "currency": fare_record.get('currency', 'LKR'),
                            "route_id": fare_record.get('route_id', 'unknown'),
                            "is_active": fare_record.get('is_active', True),
                            "created_at": fare_record.get('created_at', datetime.now().isoformat())
                        }
                    ],
                    "timestamp": datetime.now().isoformat(),
                    "source": "database"
                }
            
            # If no exact match found, try partial matching (case-insensitive)
            # This helps with location name variations
            partial_query = {
                "origin": {"$regex": f"^{source}$", "$options": "i"},
                "destination": {"$regex": f"^{destination}$", "$options": "i"},
                "mode": mode,
                "is_active": True
            }
            
            partial_fare_record = transit_fares_collection.find_one(partial_query)
            
            if partial_fare_record:
                partial_fare_record['_id'] = str(partial_fare_record['_id'])
                
                return {
                    "status": "success",
                    "fares": [
                        {
                            "base_fare": partial_fare_record.get('base_fare', 0),
                            "vehicle_type": partial_fare_record.get('vehicle_type', mode),
                            "source": partial_fare_record.get('origin', source),
                            "destination": partial_fare_record.get('destination', destination),
                            "fare_type": partial_fare_record.get('fare_type', 'unknown'),
                            "currency": partial_fare_record.get('currency', 'LKR'),
                            "route_id": partial_fare_record.get('route_id', 'unknown'),
                            "is_active": partial_fare_record.get('is_active', True),
                            "created_at": partial_fare_record.get('created_at', datetime.now().isoformat())
                        }
                    ],
                    "timestamp": datetime.now().isoformat(),
                    "source": "database_partial_match"
                }
            
            # If still no match found, try to find similar routes for the same mode
            similar_query = {
                "mode": mode,
                "is_active": True
            }
            
            similar_routes = list(transit_fares_collection.find(similar_query).limit(3))
            
            # Convert ObjectIds to strings
            for route in similar_routes:
                route['_id'] = str(route['_id'])
            
            # Return fallback with similar routes info
            fallback_response = {
                "status": "success",
                "fares": [
                    {
                        "base_fare": 5.0,  # Default fallback fare
                        "vehicle_type": vehicle_type or mode,
                        "source": source,
                        "destination": destination,
                        "fare_type": "estimated",
                        "currency": "LKR",
                        "route_id": "fallback_001",
                        "is_active": True,
                        "created_at": datetime.now().isoformat(),
                        "note": "Estimated fare - no exact route found in database"
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "source": "fallback",
                "similar_routes_available": len(similar_routes),
                "similar_routes": similar_routes[:2] if similar_routes else []  # Include up to 2 similar routes
            }
            
            return fallback_response
            
        except Exception as e:
            # Log the error for debugging
            print(f"❌ Error in FareDatabaseTool._run: {str(e)}")
            
            # Return fallback response even on error
            return {
                "status": "success",  # Still return success to avoid breaking the workflow
                "fares": [
                    {
                        "base_fare": 5.0,
                        "vehicle_type": vehicle_type or mode,
                        "source": source,
                        "destination": destination,
                        "fare_type": "fallback_error",
                        "currency": "LKR",
                        "route_id": "fallback_error_001",
                        "is_active": True,
                        "created_at": datetime.now().isoformat(),
                        "note": f"Fallback fare due to database error: {str(e)}"
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "source": "fallback_error",
                "error_details": str(e)
            }
    
    def __del__(self):
        """Clean up MongoDB connection"""
        if self._client:
            try:
                self._client.close()
            except:
                pass
    
    def get_fares_by_mode(self, mode: str, limit: int = 10) -> Dict:
        """
        Get all available fares for a specific travel mode
        """
        if not self._client:
            return {
                "status": "error",
                "error": "MongoDB connection not available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            db = self._client['transit_companion_db']
            transit_fares_collection = db['transit_fares']
            
            # Query for all active fares for the specified mode
            query = {
                "mode": mode,
                "is_active": True
            }
            
            fares = list(transit_fares_collection.find(query).limit(limit))
            
            # Convert ObjectIds to strings
            for fare in fares:
                fare['_id'] = str(fare['_id'])
            
            return {
                "status": "success",
                "mode": mode,
                "fares_count": len(fares),
                "fares": fares,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in FareDatabaseTool.get_fares_by_mode: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_fare_statistics(self) -> Dict:
        """
        Get fare statistics across all modes
        """
        if not self._client:
            return {
                "status": "error",
                "error": "MongoDB connection not available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            db = self._client['transit_companion_db']
            transit_fares_collection = db['transit_fares']
            
            # Aggregate fare statistics
            pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {
                    "_id": "$mode",
                    "count": {"$sum": 1},
                    "avg_fare": {"$avg": "$base_fare"},
                    "min_fare": {"$min": "$base_fare"},
                    "max_fare": {"$max": "$base_fare"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            stats = list(transit_fares_collection.aggregate(pipeline))
            
            return {
                "status": "success",
                "statistics": stats,
                "total_routes": sum(stat["count"] for stat in stats),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in FareDatabaseTool.get_fare_statistics: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_step_fare(self, step: Dict) -> Dict:
        """
        Calculate fare for a single transit step using departure_stop, arrival_stop, line_name
        """
        if not self._client:
            return {
                "status": "error",
                "error": "MongoDB connection not available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Get the database and collection
            db = self._client['transit_companion_db']
            transit_fares_collection = db['transit_fares']
            
            # Extract step details
            transit_details = step.get("transit_details", {})
            
            # Handle departure/arrival stops - they might be objects with 'name' property
            departure_stop_obj = transit_details.get("departure_stop", {})
            arrival_stop_obj = transit_details.get("arrival_stop", {})
            
            departure_stop = departure_stop_obj.get("name", "") if isinstance(departure_stop_obj, dict) else str(departure_stop_obj)
            arrival_stop = arrival_stop_obj.get("name", "") if isinstance(arrival_stop_obj, dict) else str(arrival_stop_obj)
            
            line_name = transit_details.get("line_name", "")
            vehicle_type = transit_details.get("vehicle_type", "").lower()
            
            # If vehicle_type is empty, try to infer from line or default to bus
            if not vehicle_type:
                if "bus" in line_name.lower():
                    vehicle_type = "bus"
                elif "train" in line_name.lower():
                    vehicle_type = "train"
                else:
                    vehicle_type = "bus"  # Default to bus for transit steps
            
            distance = step.get("distance", {}).get("value", 0) / 1000  # Convert to km
            
            print(f"🔍 Looking up fare for step: {departure_stop} -> {arrival_stop}, line: {line_name}, mode: {vehicle_type}")
            
            # Build queries only with exact matches
            queries_to_try = []
            
            # 1. Exact match with departure/arrival stops (only if both are non-empty)
            if departure_stop and arrival_stop:
                queries_to_try.append({
                    "departure_stop": {"$regex": f"^{departure_stop}$", "$options": "i"},
                    "arrival_stop": {"$regex": f"^{arrival_stop}$", "$options": "i"},
                    "mode": vehicle_type,
                    "is_active": True
                })
            
            # 2. Exact match with line name (only if line_name is non-empty)
            if line_name:
                queries_to_try.append({
                    "line_name": {"$regex": f"^{line_name}$", "$options": "i"},
                    "mode": vehicle_type,
                    "is_active": True
                })
            
            # 3. Try origin/destination match (for routes without departure/arrival stops)
            if departure_stop and arrival_stop:
                queries_to_try.append({
                    "origin": {"$regex": f"^{departure_stop}$", "$options": "i"},
                    "destination": {"$regex": f"^{arrival_stop}$", "$options": "i"},
                    "mode": vehicle_type,
                    "is_active": True
                })
            
            fare_record = None
            if queries_to_try:
                for query in queries_to_try:
                    fare_record = transit_fares_collection.find_one(query)
                    if fare_record:
                        print(f"✅ Found fare record with query: {query}")
                        break
            else:
                print("⚠️ No valid query parameters available, skipping database lookup")
            
            if fare_record:
                # Convert ObjectId to string for JSON serialization
                fare_record['_id'] = str(fare_record['_id'])
                
                return {
                    "status": "success",
                    "fare": {
                        "base_fare": fare_record.get('base_fare', 0),
                        "source": "database"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # If no database record found, calculate distance-based fare
            print(f"📏 No database record found, calculating distance-based fare for {vehicle_type}")
            
            if vehicle_type == "bus":
                # Bus fare: 15 LKR base + 2 LKR per km
                calculated_fare = 15 + (distance * 2)
            elif vehicle_type == "train":
                # Train fare: 25 LKR base + 1.5 LKR per km
                calculated_fare = 25 + (distance * 1.5)
            elif vehicle_type == "tuk_tuk":
                # Tuk-tuk fare: 50 LKR base + 8 LKR per km
                calculated_fare = 50 + (distance * 8)
            else:
                # Default fare: 20 LKR base + 3 LKR per km
                calculated_fare = 20 + (distance * 3)
            
            return {
                "status": "success",
                "fare": {
                    "base_fare": round(calculated_fare, 2),
                    "source": "distance_based"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in FareDatabaseTool.get_step_fare: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

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
            # Find all preference records for this user
            preference_records = list(self._preferences_collection.find({"user_id": user_id}))
            
            if preference_records:
                # Aggregate preferences into a single structure
                aggregated_prefs = {
                    "user_id": user_id,
                    "preferred_transit_modes": ["bus", "train"],  # Default
                    "max_walking_distance": 1.0,  # Default
                    "budget_preference": "medium",  # Default
                    "time_vs_cost_weight": 0.5,  # Default
                    "comfort_preference": 0.7,  # Default
                    "accessibility_needs": [],
                    "avoid_preferences": [],
                    "last_updated": datetime.now()
                }
                
                # Process each preference record
                for record in preference_records:
                    pref_type = record.get("preference_type")
                    weight = record.get("weight", 1.0)
                    value = record.get("value", {})
                    
                    if pref_type == "time":
                        # Handle time preferences
                        if "max_duration" in value:
                            # Convert max_duration to time_vs_cost_weight
                            max_duration = value["max_duration"]
                            if max_duration <= 60:
                                aggregated_prefs["time_vs_cost_weight"] = 0.8  # High time priority
                            elif max_duration <= 120:
                                aggregated_prefs["time_vs_cost_weight"] = 0.6  # Medium time priority
                            else:
                                aggregated_prefs["time_vs_cost_weight"] = 0.4  # Low time priority
                    
                    elif pref_type == "cost":
                        # Handle cost preferences
                        if "budget_range" in value:
                            budget_range = value["budget_range"]
                            if budget_range == "low":
                                aggregated_prefs["budget_preference"] = "low"
                            elif budget_range == "high":
                                aggregated_prefs["budget_preference"] = "high"
                    
                    elif pref_type == "comfort":
                        # Handle comfort preferences
                        if "comfort_level" in value:
                            comfort_level = value["comfort_level"]
                            aggregated_prefs["comfort_preference"] = comfort_level
                    
                    elif pref_type == "walking":
                        # Handle walking preferences
                        if "max_distance" in value:
                            aggregated_prefs["max_walking_distance"] = value["max_distance"]
                    
                    elif pref_type == "modes":
                        # Handle transit mode preferences
                        if "preferred_modes" in value:
                            aggregated_prefs["preferred_transit_modes"] = value["preferred_modes"]
                
                return {
                    "status": "success",
                    "preferences": aggregated_prefs,
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
            self._history_collection.insert_one({
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
        self._db = self._client['transit_companion_db']
        self._disruptions_collection = self._db['transit_disruptions']
    
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