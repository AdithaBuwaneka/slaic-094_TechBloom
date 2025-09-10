"""
Enhanced Route API endpoints with multiagent system integration.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from datetime import datetime

from ..models.enhanced_route import MultiAgentRequest
from ..services.enhanced_route_service import EnhancedRouteService
from ..core.database import db

router = APIRouter()
enhanced_service = EnhancedRouteService()

@router.post("/enhanced-route")
async def get_enhanced_route(
    origin: str,
    destination: str,
    mode: str,
    transit_preference: Optional[str] = None,
    user_id: Optional[str] = None,
    include_supplementary: bool = True
):
    """
    Get enhanced route with supplementary options and multiagent analysis.
    
    - **origin**: Starting location
    - **destination**: End location  
    - **mode**: Travel mode (driving, transit, walking, bicycling, three_wheeler, uber)
    - **transit_preference**: Preferred transit mode (bus or train) when mode is transit
    - **user_id**: User ID for personalized recommendations
    - **include_supplementary**: Whether to include supplementary route options
    """
    
    try:
        result = await enhanced_service.get_enhanced_route(
            origin=origin,
            destination=destination,
            mode=mode,
            transit_preference=transit_preference,
            user_id=user_id,
            include_supplementary=include_supplementary
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/route-with-preferences")
async def get_route_with_preferences(
    origin: str,
    destination: str,
    mode: str,
    user_id: str,
    preferences: Dict[str, Any]
):
    """
    Get route optimized for user preferences.
    
    - **origin**: Starting location
    - **destination**: End location
    - **mode**: Travel mode
    - **user_id**: User ID for preferences
    - **preferences**: User preference dictionary
    """
    
    try:
        result = await enhanced_service.get_route_with_preferences(
            origin=origin,
            destination=destination,
            mode=mode,
            user_id=user_id,
            preferences=preferences
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transit-routes")
async def get_transit_routes(origin: str, destination: str):
    """Get available transit routes from database"""
    
    try:
        collection = db.database["transit_routes"]
        
        routes = await collection.find({
            "$or": [
                {"origin": {"$regex": origin, "$options": "i"}},
                {"destination": {"$regex": destination, "$options": "i"}}
            ]
        }).to_list(length=10)
        
        # Convert ObjectId to string for JSON serialization
        for route in routes:
            if "_id" in route:
                route["_id"] = str(route["_id"])
        
        return {
            "success": True,
            "routes": routes,
            "count": len(routes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/route-fares")
async def get_route_fares(origin: str, destination: str, mode: str):
    """Get fare information for routes"""
    
    try:
        collection = db.database["transit_fares"]
        
        fares = await collection.find({
            "$or": [
                {"origin": {"$regex": origin, "$options": "i"}},
                {"destination": {"$regex": destination, "$options": "i"}}
            ],
            "mode": mode
        }).to_list(length=10)
        
        # Convert ObjectId to string for JSON serialization
        for fare in fares:
            if "_id" in fare:
                fare["_id"] = str(fare["_id"])
        
        return {
            "success": True,
            "fares": fares,
            "count": len(fares)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/last-mile-options")
async def get_last_mile_options(origin: str, destination: str):
    """Get last mile connectivity options"""
    
    try:
        collection = db.database["last_mile_options"]
        
        options = await collection.find({
            "$or": [
                {"origin": {"$regex": origin, "$options": "i"}},
                {"destination": {"$regex": destination, "$options": "i"}}
            ]
        }).to_list(length=10)
        
        # Convert ObjectId to string for JSON serialization
        for option in options:
            if "_id" in option:
                option["_id"] = str(option["_id"])
        
        return {
            "success": True,
            "options": options,
            "count": len(options)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    
    try:
        collection = db.database["user_preferences"]
        
        preferences = await collection.find({"user_id": user_id}).to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        for pref in preferences:
            if "_id" in pref:
                pref["_id"] = str(pref["_id"])
        
        return {
            "success": True,
            "user_id": user_id,
            "preferences": preferences,
            "count": len(preferences)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/user-preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]):
    """Update user preferences"""
    
    try:
        collection = db.database["user_preferences"]
        
        # Update existing preferences or insert new ones
        for pref_type, pref_data in preferences.items():
            await collection.update_one(
                {"user_id": user_id, "preference_type": pref_type},
                {
                    "$set": {
                        "user_id": user_id,
                        "preference_type": pref_type,
                        "value": pref_data,
                        "last_updated": datetime.now()
                    }
                },
                upsert=True
            )
        
        return {
            "success": True,
            "message": f"Preferences updated for user {user_id}",
            "updated_preferences": list(preferences.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disruptions")
async def get_active_disruptions():
    """Get active transit disruptions"""
    
    try:
        collection = db.database["transit_disruptions"]
        
        disruptions = await collection.find({"is_resolved": False}).to_list(length=20)
        
        # Convert ObjectId to string for JSON serialization
        for disruption in disruptions:
            if "_id" in disruption:
                disruption["_id"] = str(disruption["_id"])
        
        return {
            "success": True,
            "disruptions": disruptions,
            "count": len(disruptions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disruptions")
async def report_disruption(disruption: Dict[str, Any]):
    """Report a new transit disruption"""
    
    try:
        collection = db.database["transit_disruptions"]
        
        # Add timestamp and ID
        disruption["disruption_id"] = f"disp_{datetime.now().timestamp()}"
        disruption["reported_at"] = datetime.now()
        disruption["is_resolved"] = False
        
        result = await collection.insert_one(disruption)
        
        return {
            "success": True,
            "message": "Disruption reported successfully",
            "disruption_id": disruption["disruption_id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
