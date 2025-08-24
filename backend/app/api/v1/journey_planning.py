from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.journey_planning import (
    JourneyPlanRequest, JourneyPlanResponse, MultiStopJourneyRequest,
    BookingRequest, BookingResponse, JourneySearchFilters, JourneyAnalytics,
    Journey, TripManagement
)
from app.services.journey_planning_service import JourneyPlanningService
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()
journey_service = JourneyPlanningService()
user_service = UserService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    token_data = user_service._verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return token_data["user_id"]


@router.post("/plan")
async def plan_journey(request: JourneyPlanRequest):
    """Plan a comprehensive journey using all available agents"""
    try:
        response = await journey_service.plan_journey(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return {
            "status": "success",
            "message": response.message,
            "data": {
                "recommended_journey": response.recommended_journey.model_dump() if response.recommended_journey else None,
                "alternative_journeys": [j.model_dump() for j in response.alternative_journeys],
                "total_journeys_found": response.total_journeys_found,
                "processing_time_ms": response.processing_time_ms,
                "personalization_applied": response.personalization_applied,
                "travel_tips": response.travel_tips,
                "local_insights": response.local_insights
            },
            "metadata": {
                "data_sources_used": response.data_sources_used,
                "real_time_coverage": response.real_time_coverage,
                "journey_warnings": response.journey_warnings,
                "system_notices": response.system_notices
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Journey planning failed: {str(e)}"
        )


@router.post("/plan-multi-stop")
async def plan_multi_stop_journey(request: MultiStopJourneyRequest):
    """Plan multi-stop journey with waypoint optimization"""
    try:
        if len(request.waypoints) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multi-stop journey requires at least 3 waypoints (origin + stops + destination)"
            )
        
        response = await journey_service.plan_multi_stop_journey(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return {
            "status": "success",
            "message": response.message,
            "data": {
                "journey": response.recommended_journey.model_dump() if response.recommended_journey else None,
                "waypoints_count": len(request.waypoints),
                "total_segments": len(request.waypoints) - 1,
                "optimize_order_applied": request.optimize_order
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-stop journey planning failed: {str(e)}"
        )


@router.post("/book")
async def book_journey(
    booking_request: BookingRequest,
    current_user: str = Depends(get_current_user)
):
    """Book a journey for the authenticated user"""
    try:
        # Ensure the booking is for the authenticated user
        if booking_request.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot book journey for another user"
            )
        
        response = await journey_service.book_journey(booking_request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return {
            "status": "success",
            "message": response.message,
            "data": {
                "booking_id": response.booking_id,
                "booking_status": response.booking_status,
                "confirmation_number": response.confirmation_number,
                "qr_code_url": response.qr_code_url,
                "booking_reference": response.booking_reference,
                "total_fare": response.total_fare,
                "passenger_details": response.passenger_details,
                "booking_expires_at": response.booking_expires_at.isoformat() if response.booking_expires_at else None
            },
            "journey": response.journey.model_dump() if response.journey else None,
            "booking_info": {
                "cancellation_policy": response.cancellation_policy,
                "check_in_requirements": response.check_in_requirements
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Journey booking failed: {str(e)}"
        )


@router.get("/trip/{trip_id}")
async def get_trip_details(
    trip_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get details of a specific trip"""
    try:
        result = await journey_service.manage_trip(trip_id, "get_details")
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        return {
            "status": "success",
            "data": result.get("trip", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trip details: {str(e)}"
        )


@router.post("/trip/{trip_id}/start")
async def start_trip(
    trip_id: str,
    current_user: str = Depends(get_current_user)
):
    """Start an active trip"""
    try:
        result = await journey_service.manage_trip(trip_id, "start")
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to start trip")
            )
        
        return {
            "status": "success",
            "message": result["message"],
            "data": {
                "trip_status": "active",
                "started_at": datetime.utcnow().isoformat(),
                "next_leg": result.get("next_leg")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start trip: {str(e)}"
        )


@router.post("/trip/{trip_id}/update-location")
async def update_trip_location(
    trip_id: str,
    location_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Update current location for an active trip"""
    try:
        result = await journey_service.manage_trip(
            trip_id, 
            "update_location",
            current_location=location_data.get("current_location")
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to update location")
            )
        
        return {
            "status": "success",
            "message": result["message"],
            "data": {
                "trip_status": result.get("trip_status"),
                "estimated_arrival": result.get("estimated_arrival"),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update trip location: {str(e)}"
        )


@router.post("/trip/{trip_id}/complete")
async def complete_trip(
    trip_id: str,
    feedback_data: Optional[Dict[str, Any]] = None,
    current_user: str = Depends(get_current_user)
):
    """Complete a trip and optionally submit feedback"""
    try:
        result = await journey_service.manage_trip(trip_id, "complete")
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to complete trip")
            )
        
        return {
            "status": "success",
            "message": result["message"],
            "data": {
                "trip_status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "feedback_prompt": result.get("feedback_prompt")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete trip: {str(e)}"
        )


@router.post("/trip/{trip_id}/cancel")
async def cancel_trip(
    trip_id: str,
    cancellation_reason: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Cancel a trip"""
    try:
        result = await journey_service.manage_trip(
            trip_id, 
            "cancel",
            reason=cancellation_reason
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to cancel trip")
            )
        
        return {
            "status": "success",
            "message": result["message"],
            "data": {
                "trip_status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat(),
                "cancellation_policy": result.get("cancellation_policy")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel trip: {str(e)}"
        )


@router.post("/search")
async def search_journeys(filters: JourneySearchFilters):
    """Search journeys with advanced filters"""
    try:
        journeys = await journey_service.search_journeys(filters)
        
        return {
            "status": "success",
            "message": f"Found {len(journeys)} journeys matching criteria",
            "data": {
                "journeys": [journey.model_dump() for journey in journeys],
                "total_found": len(journeys),
                "filters_applied": filters.model_dump(exclude_unset=True)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Journey search failed: {str(e)}"
        )


@router.get("/analytics")
async def get_journey_analytics(
    user_id: Optional[str] = Query(None),
    days_back: int = Query(30, ge=1, le=365),
    current_user: str = Depends(get_current_user)
):
    """Get journey analytics and patterns"""
    try:
        # If user_id is provided, ensure it matches current user (unless admin)
        if user_id and user_id != current_user:
            # For now, only allow users to see their own analytics
            user_id = current_user
        
        analytics = await journey_service.get_journey_analytics(user_id, days_back)
        
        return {
            "status": "success",
            "data": analytics.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/quick-routes")
async def get_quick_routes(
    origin_lat: float = Query(..., ge=-90, le=90),
    origin_lng: float = Query(..., ge=-180, le=180),
    destination_lat: float = Query(..., ge=-90, le=90),
    destination_lng: float = Query(..., ge=-180, le=180),
    limit: int = Query(3, ge=1, le=10)
):
    """Get quick route suggestions for common journeys"""
    try:
        # Create quick journey request
        quick_request = JourneyPlanRequest(
            origin={
                "name": "Current Location",
                "latitude": origin_lat,
                "longitude": origin_lng
            },
            destination={
                "name": "Destination",
                "latitude": destination_lat,
                "longitude": destination_lng
            },
            max_alternatives=limit,
            priorities=["fastest", "cheapest", "balanced"]
        )
        
        response = await journey_service.plan_journey(quick_request)
        
        # Return simplified route data
        quick_routes = []
        if response.recommended_journey:
            quick_routes.append({
                "journey_id": response.recommended_journey.journey_id,
                "duration_minutes": response.recommended_journey.total_duration_minutes,
                "fare": response.recommended_journey.total_fare,
                "transport_modes": [leg.transport_mode.value for leg in response.recommended_journey.legs],
                "departure_time": response.recommended_journey.departure_time.isoformat(),
                "arrival_time": response.recommended_journey.arrival_time.isoformat(),
                "overall_score": response.recommended_journey.overall_score
            })
        
        for alt_journey in response.alternative_journeys:
            quick_routes.append({
                "journey_id": alt_journey.journey_id,
                "duration_minutes": alt_journey.total_duration_minutes,
                "fare": alt_journey.total_fare,
                "transport_modes": [leg.transport_mode.value for leg in alt_journey.legs],
                "departure_time": alt_journey.departure_time.isoformat(),
                "arrival_time": alt_journey.arrival_time.isoformat(),
                "overall_score": alt_journey.overall_score
            })
        
        return {
            "status": "success",
            "message": f"Found {len(quick_routes)} quick route options",
            "data": {
                "routes": quick_routes[:limit],
                "processing_time_ms": response.processing_time_ms
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick routes failed: {str(e)}"
        )


@router.get("/popular-routes")
async def get_popular_routes():
    """Get popular route suggestions"""
    try:
        # Generate popular routes (in real implementation, this would come from analytics)
        popular_routes = [
            {
                "route_name": "Colombo Fort to Kandy",
                "description": "Express train service with scenic mountain views",
                "average_duration_minutes": 180,
                "average_fare": 250.0,
                "popularity_score": 9.2,
                "transport_modes": ["train"],
                "tags": ["scenic", "express", "popular"]
            },
            {
                "route_name": "Colombo to Galle Coastal Route",
                "description": "Beautiful coastal journey with ocean views",
                "average_duration_minutes": 120,
                "average_fare": 180.0,
                "popularity_score": 8.8,
                "transport_modes": ["bus", "train"],
                "tags": ["coastal", "scenic", "frequent"]
            },
            {
                "route_name": "Kandy to Ella Scenic Train",
                "description": "World-famous scenic train journey through tea plantations",
                "average_duration_minutes": 240,
                "average_fare": 200.0,
                "popularity_score": 9.8,
                "transport_modes": ["train"],
                "tags": ["scenic", "world_famous", "tea_country"]
            },
            {
                "route_name": "Colombo Airport to City Center",
                "description": "Multiple transport options from airport to city",
                "average_duration_minutes": 45,
                "average_fare": 150.0,
                "popularity_score": 8.5,
                "transport_modes": ["taxi", "bus"],
                "tags": ["airport", "frequent", "essential"]
            }
        ]
        
        return {
            "status": "success",
            "message": f"Retrieved {len(popular_routes)} popular routes",
            "data": {
                "popular_routes": popular_routes,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular routes: {str(e)}"
        )


@router.get("/service-status")
async def get_service_status():
    """Get journey planning service status and performance metrics"""
    try:
        return {
            "status": "success",
            "data": {
                "service_status": "operational",
                "total_requests_processed": journey_service.request_count,
                "average_response_time_ms": (
                    journey_service.total_processing_time / journey_service.request_count
                    if journey_service.request_count > 0 else 0
                ),
                "cache_hit_rate": 0.75,  # Simulated
                "active_data_sources": 7,
                "real_time_coverage": 0.85,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service status: {str(e)}"
        )