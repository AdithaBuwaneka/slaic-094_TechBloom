from fastapi import APIRouter, HTTPException, Depends, status, Query, Header, Response
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib
import json

from app.models.user import User
from app.api.auth import get_current_user
from app.core.database import db

router = APIRouter()

class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class RouteSearchRequest(BaseModel):
    origin: str
    destination: str
    transport_mode: Optional[str] = "any"
    departure_time: Optional[datetime] = None
    passenger_count: int = 1
    accessibility_needs: List[str] = []
    max_results: int = 10

def generate_cache_key(data: dict) -> str:
    """Generate cache key for response caching"""
    return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

def set_cache_headers(response: Response, cache_duration: int = 300):
    """Set HTTP cache headers for mobile clients"""
    response.headers["Cache-Control"] = f"max-age={cache_duration}, public"
    response.headers["ETag"] = f'"{datetime.utcnow().timestamp()}"'
    response.headers["Last-Modified"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

@router.get("/routes/search", response_model=Dict[str, Any])
async def search_routes_optimized(
    response: Response,
    origin: str = Query(..., description="Origin location"),
    destination: str = Query(..., description="Destination location"),
    mode: str = Query("any", description="Transport mode: bus, train, tuk_tuk, any"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    user: User = Depends(get_current_user),
    if_none_match: Optional[str] = Header(None)
):
    """Optimized route search for React Native with caching and pagination"""
    try:
        # Generate cache key
        cache_data = {
            "origin": origin.lower(),
            "destination": destination.lower(), 
            "mode": mode,
            "page": page,
            "limit": limit
        }
        cache_key = generate_cache_key(cache_data)
        etag = f'"{cache_key}"'
        
        # Check ETag for client-side caching
        if if_none_match == etag:
            response.status_code = status.HTTP_304_NOT_MODIFIED
            return {}
        
        # Search bus routes
        bus_routes = []
        if mode in ["any", "bus"]:
            bus_query = {
                "$or": [
                    {"origin": {"$regex": origin, "$options": "i"}},
                    {"destination": {"$regex": destination, "$options": "i"}},
                    {"stops": {"$elemMatch": {"$regex": f"{origin}|{destination}", "$options": "i"}}}
                ]
            }
            
            bus_cursor = db.bus_routes_collection.find(bus_query).limit(limit)
            async for route in bus_cursor:
                bus_routes.append({
                    "id": str(route["_id"]),
                    "type": "bus",
                    "route_number": route.get("route_number", ""),
                    "origin": route.get("origin", ""),
                    "destination": route.get("destination", ""),
                    "stops": route.get("stops", []),
                    "operator": route.get("operator", ""),
                    "fare": route.get("fare", 0),
                    "frequency": route.get("frequency", ""),
                    "operating_hours": route.get("operating_hours", ""),
                    "estimated_duration": route.get("estimated_duration", "2-3 hours"),
                    "comfort_level": route.get("comfort_level", "standard")
                })
        
        # Search train routes
        train_routes = []
        if mode in ["any", "train"]:
            train_query = {
                "$or": [
                    {"origin": {"$regex": origin, "$options": "i"}},
                    {"destination": {"$regex": destination, "$options": "i"}},
                    {"stops": {"$elemMatch": {"$regex": f"{origin}|{destination}", "$options": "i"}}}
                ]
            }
            
            train_cursor = db.train_routes_collection.find(train_query).limit(limit)
            async for route in train_cursor:
                train_routes.append({
                    "id": str(route["_id"]),
                    "type": "train",
                    "route_name": route.get("route_name", ""),
                    "origin": route.get("origin", ""),
                    "destination": route.get("destination", ""),
                    "stops": route.get("stops", []),
                    "operator": route.get("operator", ""),
                    "classes": route.get("classes", []),
                    "fares": route.get("fares", {}),
                    "frequency": route.get("frequency", ""),
                    "operating_hours": route.get("operating_hours", ""),
                    "scenic_rating": route.get("scenic_rating", 4)
                })
        
        # Combine and sort results
        all_routes = bus_routes + train_routes
        total_routes = len(all_routes)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_routes = all_routes[start_idx:end_idx]
        
        # Set cache headers
        set_cache_headers(response, 300)  # 5 minutes cache
        response.headers["ETag"] = etag
        
        return {
            "routes": paginated_routes,
            "pagination": {
                "total": total_routes,
                "page": page,
                "per_page": limit,
                "has_next": end_idx < total_routes,
                "has_prev": page > 1,
                "total_pages": (total_routes + limit - 1) // limit
            },
            "search_meta": {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "cached_at": datetime.utcnow().isoformat(),
                "cache_key": cache_key
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/routes/popular", response_model=Dict[str, Any])
async def get_popular_routes(
    response: Response,
    limit: int = Query(20, ge=1, le=50),
    transport_type: str = Query("all", description="all, bus, train")
):
    """Get popular routes for home screen with aggressive caching"""
    try:
        cache_key = f"popular_routes_{transport_type}_{limit}"
        
        # Set long cache for popular routes (30 minutes)
        set_cache_headers(response, 1800)
        
        popular_routes = []
        
        if transport_type in ["all", "bus"]:
            # Get most popular bus routes (mock popularity data)
            bus_cursor = db.bus_routes_collection.find().limit(limit // 2 if transport_type == "all" else limit)
            async for route in bus_cursor:
                popular_routes.append({
                    "id": str(route["_id"]),
                    "type": "bus",
                    "route_number": route.get("route_number", ""),
                    "origin": route.get("origin", ""),
                    "destination": route.get("destination", ""),
                    "operator": route.get("operator", ""),
                    "fare": route.get("fare", 0),
                    "popularity_score": 85,  # Mock popularity
                    "average_rating": 4.2,
                    "daily_passengers": 1500,
                    "thumbnail": f"/images/routes/bus_{route.get('route_number', 'default')}.jpg"
                })
        
        if transport_type in ["all", "train"]:
            train_cursor = db.train_routes_collection.find().limit(limit // 2 if transport_type == "all" else limit)
            async for route in train_cursor:
                popular_routes.append({
                    "id": str(route["_id"]),
                    "type": "train",
                    "route_name": route.get("route_name", ""),
                    "origin": route.get("origin", ""),
                    "destination": route.get("destination", ""),
                    "operator": route.get("operator", ""),
                    "classes": route.get("classes", []),
                    "popularity_score": 92,
                    "average_rating": 4.5,
                    "daily_passengers": 800,
                    "scenic_rating": 5,
                    "thumbnail": f"/images/routes/train_{route.get('route_name', 'default').replace(' ', '_').lower()}.jpg"
                })
        
        return {
            "popular_routes": popular_routes[:limit],
            "last_updated": datetime.utcnow().isoformat(),
            "cache_duration": 1800,
            "recommendations": [
                "Kandy-Colombo train offers scenic mountain views",
                "Bus Route 138 has frequent services during peak hours",
                "Early morning trains have better availability"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular routes: {str(e)}"
        )

@router.get("/user/journey-history", response_model=PaginatedResponse)
async def get_journey_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user)
):
    """Get user's journey history with pagination for React Native ListView"""
    try:
        # Get total count
        total = await db.journey_history_collection.count_documents({"user_id": user.id})
        
        # Get paginated journeys
        skip = (page - 1) * limit
        journeys_cursor = db.journey_history_collection.find({"user_id": user.id})\
            .sort("created_at", -1)\
            .skip(skip)\
            .limit(limit)
        
        journeys = []
        async for journey in journeys_cursor:
            journeys.append({
                "id": str(journey["_id"]),
                "origin": journey.get("origin", ""),
                "destination": journey.get("destination", ""),
                "transport_mode": journey.get("transport_mode", ""),
                "departure_time": journey.get("departure_time", "").isoformat() if journey.get("departure_time") else None,
                "arrival_time": journey.get("arrival_time", "").isoformat() if journey.get("arrival_time") else None,
                "total_cost": journey.get("total_cost", 0),
                "rating": journey.get("rating", None),
                "created_at": journey.get("created_at", "").isoformat() if journey.get("created_at") else None
            })
        
        return PaginatedResponse(
            data=journeys,
            total=total,
            page=page,
            per_page=limit,
            has_next=skip + limit < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get journey history: {str(e)}"
        )

@router.get("/disruptions/active-compact")
async def get_active_disruptions_compact(
    response: Response,
    severity: Optional[str] = Query(None, description="low, medium, high"),
    transport_mode: Optional[str] = Query(None, description="bus, train, tuk_tuk")
):
    """Get active disruptions in compact format for mobile notifications"""
    try:
        # Set short cache for disruptions (1 minute)
        set_cache_headers(response, 60)
        
        query = {
            "start_time": {"$lte": datetime.utcnow()},
            "$or": [
                {"end_time": {"$gte": datetime.utcnow()}},
                {"end_time": None}
            ]
        }
        
        if severity:
            query["severity"] = severity
        if transport_mode:
            query["transport_mode"] = transport_mode
        
        disruptions_cursor = db.disruptions_collection.find(query).limit(20)
        
        disruptions = []
        async for disruption in disruptions_cursor:
            disruptions.append({
                "id": str(disruption["_id"]),
                "title": disruption.get("title", ""),
                "summary": disruption.get("description", "")[:100] + "..." if len(disruption.get("description", "")) > 100 else disruption.get("description", ""),
                "severity": disruption.get("severity", "medium"),
                "transport_mode": disruption.get("transport_mode", ""),
                "affected_areas": disruption.get("affected_stops", [])[:3],  # First 3 areas only
                "estimated_duration": disruption.get("estimated_duration", "unknown"),
                "color": {
                    "low": "#4CAF50",
                    "medium": "#FF9800", 
                    "high": "#F44336"
                }.get(disruption.get("severity", "medium"), "#FF9800"),
                "icon": {
                    "bus": "🚌",
                    "train": "🚂", 
                    "tuk_tuk": "🛺"
                }.get(disruption.get("transport_mode", ""), "⚠️")
            })
        
        return {
            "disruptions": disruptions,
            "summary": {
                "total_active": len(disruptions),
                "high_severity": len([d for d in disruptions if d["severity"] == "high"]),
                "affected_modes": list(set([d["transport_mode"] for d in disruptions if d["transport_mode"]]))
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get disruptions: {str(e)}"
        )

@router.get("/app/startup-data")
async def get_startup_data(
    response: Response,
    user: User = Depends(get_current_user)
):
    """Get all essential data needed for app startup in one request"""
    try:
        # Set moderate cache (5 minutes)
        set_cache_headers(response, 300)
        
        # Get user's recent searches/favorites (mock data)
        recent_searches = [
            {"origin": "Colombo", "destination": "Kandy", "count": 5},
            {"origin": "Galle", "destination": "Colombo", "count": 3},
            {"origin": "Kandy", "destination": "Nuwara Eliya", "count": 2}
        ]
        
        # Get unread notifications count
        unread_notifications = await db.notifications_collection.count_documents({
            "user_id": user.id,
            "read_at": {"$exists": False}
        })
        
        # Get active disruptions count
        active_disruptions = await db.disruptions_collection.count_documents({
            "start_time": {"$lte": datetime.utcnow()},
            "$or": [
                {"end_time": {"$gte": datetime.utcnow()}},
                {"end_time": None}
            ]
        })
        
        return {
            "user": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "preferred_language": user.preferred_language,
                "profile_picture": user.profile_picture,
                "unread_notifications": unread_notifications
            },
            "app_state": {
                "active_disruptions": active_disruptions,
                "service_status": "operational",
                "maintenance_mode": False,
                "feature_flags": {
                    "voice_search": True,
                    "offline_maps": True,
                    "real_time_tracking": False
                }
            },
            "quick_access": {
                "recent_searches": recent_searches,
                "saved_routes": [],  # Would come from user preferences
                "emergency_contacts": [
                    {"name": "Police", "number": "119"},
                    {"name": "Ambulance", "number": "110"},
                    {"name": "Tourist Hotline", "number": "+94112426900"}
                ]
            },
            "weather": {
                "condition": "partly_cloudy",
                "temperature": 28,
                "humidity": 75,
                "rain_probability": 30,
                "travel_impact": "minimal"
            },
            "startup_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get startup data: {str(e)}"
        )

@router.post("/user/save-route")
async def save_favorite_route(
    route_data: dict,
    user: User = Depends(get_current_user)
):
    """Save a route to user's favorites for quick access"""
    try:
        favorite = {
            "user_id": user.id,
            "route_id": route_data.get("route_id"),
            "route_type": route_data.get("route_type"),
            "origin": route_data.get("origin"),
            "destination": route_data.get("destination"),
            "nickname": route_data.get("nickname", f"{route_data.get('origin')} → {route_data.get('destination')}"),
            "created_at": datetime.utcnow(),
            "usage_count": 1
        }
        
        # Check if already exists
        existing = await db.user_favorites_collection.find_one({
            "user_id": user.id,
            "route_id": route_data.get("route_id")
        })
        
        if existing:
            # Increment usage count
            await db.user_favorites_collection.update_one(
                {"_id": existing["_id"]},
                {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.utcnow()}}
            )
            return {"message": "Route updated in favorites", "action": "updated"}
        else:
            # Add new favorite
            await db.user_favorites_collection.insert_one(favorite)
            return {"message": "Route saved to favorites", "action": "created"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save route: {str(e)}"
        )