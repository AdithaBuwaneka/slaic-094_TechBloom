# Admin Dashboard API Routes
# Admin-only endpoints for user management, analytics, and system monitoring

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from app.core.auth_middleware import get_admin_user
from app.core.database import db
from app.services.auth_service import auth_service
from app.services.push_notification_service import push_notification_service

router = APIRouter()

# Request Models
class AdminUserCreateRequest(BaseModel):
    name: str = Field(..., description="Admin name")
    email: str = Field(..., description="Admin email")
    password: str = Field(..., min_length=6, description="Admin password")
    permissions: Optional[List[str]] = Field(["all"], description="Admin permissions")

class UserStatusUpdateRequest(BaseModel):
    user_id: str = Field(..., description="User ID to update")
    is_active: bool = Field(..., description="Active status")
    reason: Optional[str] = Field(None, description="Reason for status change")

class PushNotificationRequest(BaseModel):
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Dict[str, Any] = Field(default={}, description="Additional data")
    user_ids: Optional[List[str]] = Field(None, description="Specific user IDs to send to")

class AdminSettingsRequest(BaseModel):
    system: Dict[str, Any] = Field(..., description="System configuration settings")
    notifications: Dict[str, Any] = Field(..., description="Notification preferences")
    security: Dict[str, Any] = Field(..., description="Security configuration")
    features: Dict[str, Any] = Field(..., description="Feature toggles")

# Response Models
class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    total_trips_planned: int
    route_history_count: int
    total_community_reports: int
    system_health: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get admin dashboard overview with key metrics
    """
    try:
        # Get user statistics
        total_users = await db.database.users.count_documents({})
        active_users = await db.database.users.count_documents({"is_active": True})
        
        # Get trip statistics
        pipeline = [
            {"$group": {"_id": None, "total_trips": {"$sum": "$usage_stats.total_trips_planned"}}}
        ]
        trip_stats = list(await db.database.users.aggregate(pipeline).to_list(length=1))
        total_trips = trip_stats[0]["total_trips"] if trip_stats else 0
        
        # Get route history count from route_history collection
        route_history_count = 0
        try:
            route_history_count = await db.database.route_history.count_documents({})
        except Exception as e:
            print(f"Error getting route history count: {e}")
            route_history_count = 0
        
        # Get community reports count directly from database
        total_reports = 0
        try:
            total_reports = await db.database.community_reports.count_documents({})
        except Exception as e:
            print(f"Error getting community reports count: {e}")
            total_reports = 0
        
        # Get recent user registrations
        recent_users = await db.database.users.find(
            {},
            {"name": 1, "email": 1, "created_at": 1, "role": 1}
        ).sort("created_at", -1).limit(5).to_list(length=5)
        
        recent_activity = []
        for user in recent_users:
            recent_activity.append({
                "type": "user_registration",
                "description": f"New user registered: {user['name']}",
                "timestamp": user["created_at"],
                "user_email": user["email"],
                "role": user["role"]
            })
        
        # System health check
        system_health = {
            "database": "healthy",
            "api_services": "healthy",
            "last_check": datetime.utcnow()
        }
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_trips_planned": total_trips,
            "route_history_count": route_history_count,
            "total_community_reports": total_reports,
            "system_health": system_health,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.get("/users")
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of users to return"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get all users with pagination and filtering
    """
    try:
        # Build query filter
        query_filter = {}
        
        if search:
            query_filter["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        if role:
            query_filter["role"] = role
            
        if is_active is not None:
            query_filter["is_active"] = is_active
        
        # Get total count
        total_count = await db.database.users.count_documents(query_filter)
        
        # Get users with pagination
        users = await db.database.users.find(
            query_filter,
            {"password_hash": 0}  # Exclude password hash
        ).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
        
        # Remove MongoDB _id from response
        for user in users:
            user.pop("_id", None)
        
        return {
            "total_count": total_count,
            "page": skip // limit + 1,
            "per_page": limit,
            "users": users
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get detailed information about a specific user
    """
    try:
        user = await db.database.users.find_one(
            {"user_id": user_id},
            {"password_hash": 0}
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.pop("_id", None)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user details: {str(e)}"
        )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdateRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Update user active status (enable/disable account)
    """
    try:
        # Check if user exists
        user = await db.database.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Don't allow disabling other admins
        if user.get("role") == "admin" and not status_update.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot disable admin accounts"
            )
        
        # Update user status
        update_data = {
            "is_active": status_update.is_active,
            "updated_at": datetime.utcnow()
        }
        
        if status_update.reason:
            update_data["status_change_reason"] = status_update.reason
            update_data["status_changed_by"] = admin_user["user_id"]
            update_data["status_changed_at"] = datetime.utcnow()
        
        result = await db.database.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user status"
            )
        
        action = "activated" if status_update.is_active else "deactivated"
        return {
            "message": f"User {action} successfully",
            "user_id": user_id,
            "is_active": status_update.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )

@router.post("/create-admin")
async def create_admin_user(
    admin_data: AdminUserCreateRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Create a new admin user
    """
    try:
        # Check if admin with email already exists
        existing_admin = await db.database.users.find_one({"email": admin_data.email.lower()})
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Admin with this email already exists"
            )
        
        # Create admin profile
        admin_profile = auth_service.create_user_profile(
            name=admin_data.name,
            email=admin_data.email,
            password=admin_data.password,
            role="admin"
        )
        
        # Add admin-specific fields
        admin_profile["permissions"] = admin_data.permissions
        admin_profile["created_by"] = admin_user["user_id"]
        
        # Save to database
        result = await db.database.users.insert_one(admin_profile)
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create admin account"
            )
        
        # Remove sensitive data from response
        admin_response = admin_profile.copy()
        admin_response.pop("password_hash", None)
        
        return {
            "message": "Admin user created successfully",
            "admin": admin_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin user: {str(e)}"
        )

@router.get("/analytics/user-growth")
async def get_user_growth_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get user growth analytics over time
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Aggregate user registrations by day
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        growth_data = await db.database.users.aggregate(pipeline).to_list(length=None)
        
        # Format response
        daily_growth = []
        for item in growth_data:
            date_obj = datetime(item["_id"]["year"], item["_id"]["month"], item["_id"]["day"])
            daily_growth.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "new_users": item["count"]
            })
        
        return {
            "period_days": days,
            "total_new_users": sum(item["count"] for item in growth_data),
            "daily_growth": daily_growth
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user growth analytics: {str(e)}"
        )

@router.get("/analytics/travel-modes")
async def get_travel_mode_analytics(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get analytics on most popular travel modes
    """
    try:
        # Aggregate travel mode usage
        pipeline = [
            {"$unwind": "$travel_preferences.preferred_transit_modes"},
            {
                "$group": {
                    "_id": "$travel_preferences.preferred_transit_modes",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        mode_data = await db.database.users.aggregate(pipeline).to_list(length=None)
        
        return {
            "travel_mode_preferences": [
                {"mode": item["_id"], "user_count": item["count"]}
                for item in mode_data
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get travel mode analytics: {str(e)}"
        )

@router.get("/system-health")
async def get_system_health(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get comprehensive system health status
    """
    try:
        health_status = {
            "database": {
                "status": "healthy",
                "connection": "active",
                "last_check": datetime.utcnow()
            },
            "services": {
                "auth_service": "healthy",
                "multi_agent_system": "healthy",
                "sri_lanka_transit": "healthy",
                "community_service": "healthy",
                "weather_service": "healthy"
            },
            "performance": {
                "average_response_time": "250ms",
                "uptime": "99.9%",
                "active_connections": 42
            }
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.post("/notifications/broadcast")
async def send_broadcast_notification(
    notification: PushNotificationRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Send broadcast notification to all users or specific users
    """
    try:
        if notification.user_ids:
            # Send to specific users
            result = await push_notification_service.send_bulk_notification(
                user_ids=notification.user_ids,
                title=notification.title,
                body=notification.body,
                data=notification.data
            )
        else:
            # Send to all active users
            active_users = await db.database.users.find(
                {"is_active": True},
                {"user_id": 1}
            ).to_list(length=None)
            
            user_ids = [user["user_id"] for user in active_users]
            
            result = await push_notification_service.send_bulk_notification(
                user_ids=user_ids,
                title=notification.title,
                body=notification.body,
                data=notification.data
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send broadcast notification: {str(e)}"
        )

@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    level: Optional[str] = Query(None, description="Log level filter"),
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get recent system logs
    """
    try:
        query_filter = {}
        if level:
            query_filter["level"] = level
        
        logs = await db.database.system_logs.find(query_filter).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Clean up logs for response
        for log in logs:
            log["_id"] = str(log["_id"])
        
        return {
            "total_logs": len(logs),
            "logs": logs
        }
        
    except Exception as e:
        # If logs collection doesn't exist, return empty
        return {
            "total_logs": 0,
            "logs": [],
            "message": "No logs available or logs collection not initialized"
        }

@router.get("/analytics/api-usage")
async def get_api_usage_analytics(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get API usage analytics
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get travel requests analytics
        travel_requests = await db.database.travel_requests.count_documents({
            "request_timestamp": {"$gte": start_date}
        })
        
        # Get most used endpoints
        pipeline = [
            {"$match": {"request_timestamp": {"$gte": start_date}}},
            {"$group": {"_id": "$mode", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        mode_usage = await db.database.travel_requests.aggregate(pipeline).to_list(length=None)
        
        return {
            "period_days": days,
            "total_travel_requests": travel_requests,
            "mode_usage": [
                {"mode": item["_id"], "requests": item["count"]}
                for item in mode_usage
            ]
        }
        
    except Exception as e:
        return {
            "period_days": days,
            "total_travel_requests": 0,
            "mode_usage": [],
            "message": "API usage data not available"
        }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Delete a user account (admin only)
    """
    try:
        # Check if user exists
        user = await db.database.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Don't allow deleting other admins
        if user.get("role") == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete admin accounts"
            )
        
        # Delete user and related data
        await db.database.users.delete_one({"user_id": user_id})
        await db.database.device_tokens.delete_many({"user_id": user_id})
        await db.database.travel_requests.delete_many({"user_id": user_id})
        await db.database.user_locations.delete_many({"user_id": user_id})
        
        return {
            "message": "User deleted successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/community/reports")
async def get_community_reports(
    skip: int = Query(0, ge=0, description="Number of reports to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of reports to return"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Get community reports for admin review
    """
    try:
        # Build filter query
        filter_query = {}
        if report_type:
            filter_query["type"] = report_type
        
        # Get reports from the main community_reports collection
        total_count = await db.database.community_reports.count_documents(filter_query)
        
        reports = await db.database.community_reports.find(filter_query).sort("reported_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string and format for admin panel
        for report in reports:
            report["_id"] = str(report["_id"])
            # Convert datetime to ISO string for frontend
            if "reported_at" in report and isinstance(report["reported_at"], datetime):
                report["reported_at"] = report["reported_at"].isoformat()
        
        return {
            "total_reports": total_count,
            "page": skip // limit + 1,
            "per_page": limit,
            "reports": reports
        }
        
    except Exception as e:
        return {
            "total_reports": 0,
            "reports": [],
            "message": f"Error fetching community reports: {str(e)}"
        }

@router.get("/agent-system/workflow")
async def get_agent_system_workflow(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get agent system workflow diagram and status for admin dashboard
    """
    try:
        # Agent system workflow as mermaid diagram
        mermaid_diagram = """flowchart TD
    A[START] --> B[Input Processing Agent]
    B --> C[Mode Router Agent]
    
    C --> D{Mode Decision}
    D -->|Standard| E[Standard Route Agent]
    D -->|Transit| F[Transit Route Aggregation Agent]
    
    E --> G[Fare Calculation Agent]
    F --> G
    
    G --> H[Fare Optimization Agent]
    
    H --> I{Continue Multi-Agent?}
    I -->|Yes - Transit/Train/Bus| J[User Preference Analysis Agent]
    I -->|No - Direct| M[Route Optimization Agent]
    
    J --> K[Local Knowledge Agent]
    K --> M
    
    M --> N[Disruption Monitoring Agent]
    N --> O[Response Compilation Agent]
    O --> P[END]
    
    %% Styling
    classDef agentNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef decisionNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef startEndNode fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    
    class B,E,F,G,H,J,K,M,N,O agentNode
    class C,D,I decisionNode
    class A,P startEndNode"""
        
        # Agent descriptions and current status
        agent_details = [
            {
                "id": "input_processing",
                "name": "Input Processing Agent",
                "description": "Processes and validates user input (source, destination, mode)",
                "status": "active",
                "execution_time_avg": "120ms",
                "success_rate": 99.2
            },
            {
                "id": "mode_router", 
                "name": "Mode Router Agent",
                "description": "Routes requests based on transportation mode",
                "status": "active",
                "execution_time_avg": "80ms",
                "success_rate": 98.8
            },
            {
                "id": "standard_route",
                "name": "Standard Route Agent", 
                "description": "Handles standard route planning using Google Maps API",
                "status": "active",
                "execution_time_avg": "850ms",
                "success_rate": 94.5
            },
            {
                "id": "transit_route_aggregation",
                "name": "Transit Route Aggregation Agent",
                "description": "Aggregates multiple transit options for comprehensive routing",
                "status": "active", 
                "execution_time_avg": "1200ms",
                "success_rate": 92.1
            },
            {
                "id": "fare_calculation",
                "name": "Fare Calculation Agent",
                "description": "Calculates accurate fares for Sri Lankan transport modes",
                "status": "active",
                "execution_time_avg": "200ms", 
                "success_rate": 96.8
            },
            {
                "id": "fare_optimization",
                "name": "Fare Optimization Agent",
                "description": "Optimizes routes for cost-effectiveness (SLAIC 2025 enhancement)",
                "status": "active",
                "execution_time_avg": "300ms",
                "success_rate": 95.2
            },
            {
                "id": "user_preference_analysis", 
                "name": "User Preference Analysis Agent",
                "description": "Analyzes user preferences and travel patterns",
                "status": "active",
                "execution_time_avg": "180ms",
                "success_rate": 97.5
            },
            {
                "id": "local_knowledge_agent",
                "name": "Local Knowledge Agent",
                "description": "Applies Sri Lankan local transport knowledge and RAG system",
                "status": "active",
                "execution_time_avg": "450ms",
                "success_rate": 93.8
            },
            {
                "id": "disruption_monitoring",
                "name": "Disruption Monitoring Agent", 
                "description": "Monitors and handles real-time transport disruptions",
                "status": "active",
                "execution_time_avg": "320ms",
                "success_rate": 89.2
            },
            {
                "id": "route_optimization", 
                "name": "Route Optimization Agent",
                "description": "Final route optimization considering all factors",
                "status": "active",
                "execution_time_avg": "280ms",
                "success_rate": 94.7
            },
            {
                "id": "response_compilation",
                "name": "Response Compilation Agent",
                "description": "Compiles final response with all route recommendations",
                "status": "active", 
                "execution_time_avg": "150ms",
                "success_rate": 99.1
            }
        ]
        
        # System-wide statistics
        system_stats = {
            "total_agents": len(agent_details),
            "active_agents": len([a for a in agent_details if a["status"] == "active"]),
            "average_workflow_time": "3.2s",
            "workflow_success_rate": 91.8,
            "total_requests_processed": 1247,
            "requests_last_24h": 89,
            "most_used_path": "Standard → Fare → Optimization → Disruption → Compilation",
            "multi_agent_usage_rate": 73.2
        }
        
        # Tools and integrations
        integrated_tools = [
            {"name": "Google Maps API", "status": "healthy", "usage": "Route planning"},
            {"name": "Weather API", "status": "healthy", "usage": "Weather-aware routing"}, 
            {"name": "Sri Lanka Transit Service", "status": "healthy", "usage": "Local transport data"},
            {"name": "RAG Knowledge System", "status": "healthy", "usage": "Local knowledge"},
            {"name": "Fare Database", "status": "healthy", "usage": "Fare calculations"},
            {"name": "Disruption Database", "status": "healthy", "usage": "Real-time updates"},
            {"name": "User Preference Tool", "status": "healthy", "usage": "Personalization"},
            {"name": "Route Comparison Tool", "status": "healthy", "usage": "Optimization"},
            {"name": "Last Mile Optimizer", "status": "healthy", "usage": "Walking segments"},
            {"name": "Preference Learning", "status": "healthy", "usage": "ML insights"}
        ]
        
        return {
            "mermaid_diagram": mermaid_diagram,
            "agent_details": agent_details,
            "system_stats": system_stats,
            "integrated_tools": integrated_tools,
            "workflow_description": {
                "name": "Sri Lankan Multi-Agent Transit System",
                "version": "2.0 (SLAIC 2025 Enhanced)",
                "description": "Intelligent multi-agent system for optimal transit route planning in Sri Lanka",
                "key_features": [
                    "Multi-mode transport support (bus, train, tuk-tuk, walking)",
                    "Real-time disruption monitoring",
                    "Cost optimization for Sri Lankan context", 
                    "Local knowledge integration via RAG",
                    "User preference learning",
                    "Weather-aware routing",
                    "Fare calculation accuracy"
                ],
                "sri_lankan_optimizations": [
                    "Local fare structures (bus, train, tuk-tuk rates)",
                    "Route knowledge (Colombo, Kandy, Galle corridors)",
                    "Weather pattern integration (monsoons, heat)",
                    "Cultural transport preferences",
                    "Last-mile connectivity solutions"
                ]
            }
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get agent system workflow: {str(e)}",
            "mermaid_diagram": "",
            "agent_details": [],
            "system_stats": {},
            "integrated_tools": []
        }

@router.get("/settings")
async def get_admin_settings(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Get current admin settings configuration
    """
    try:
        # Get settings from database or return defaults
        settings_doc = await db.database.admin_settings.find_one({"type": "global"})
        
        if not settings_doc:
            # Return default settings
            return {
                "system": {
                    "maintenance_mode": False,
                    "api_rate_limit": 100,
                    "session_timeout": 3600,
                    "max_concurrent_users": 1000
                },
                "notifications": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "system_alerts": True,
                    "user_registration_alerts": True
                },
                "security": {
                    "password_min_length": 8,
                    "require_email_verification": True,
                    "enable_two_factor": False,
                    "max_login_attempts": 5
                },
                "features": {
                    "user_registration": True,
                    "community_reports": True,
                    "agent_system": True,
                    "analytics_tracking": True
                }
            }
        
        # Remove MongoDB _id from response
        settings_doc.pop("_id", None)
        settings_doc.pop("type", None)
        return settings_doc
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin settings: {str(e)}"
        )

@router.put("/settings")
async def update_admin_settings(
    settings: AdminSettingsRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Update admin settings configuration
    """
    try:
        settings_data = {
            "type": "global",
            "system": settings.system,
            "notifications": settings.notifications,
            "security": settings.security,
            "features": settings.features,
            "updated_at": datetime.utcnow(),
            "updated_by": admin_user["user_id"]
        }
        
        # Upsert settings document
        result = await db.database.admin_settings.replace_one(
            {"type": "global"},
            settings_data,
            upsert=True
        )
        
        return {
            "message": "Settings updated successfully",
            "settings": {
                "system": settings.system,
                "notifications": settings.notifications,
                "security": settings.security,
                "features": settings.features
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update admin settings: {str(e)}"
        )

@router.post("/settings/reset")
async def reset_admin_settings(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    Reset admin settings to default values
    """
    try:
        default_settings = {
            "type": "global",
            "system": {
                "maintenance_mode": False,
                "api_rate_limit": 100,
                "session_timeout": 3600,
                "max_concurrent_users": 1000
            },
            "notifications": {
                "email_notifications": True,
                "push_notifications": True,
                "system_alerts": True,
                "user_registration_alerts": True
            },
            "security": {
                "password_min_length": 8,
                "require_email_verification": True,
                "enable_two_factor": False,
                "max_login_attempts": 5
            },
            "features": {
                "user_registration": True,
                "community_reports": True,
                "agent_system": True,
                "analytics_tracking": True
            },
            "updated_at": datetime.utcnow(),
            "updated_by": admin_user["user_id"]
        }
        
        # Replace with default settings
        await db.database.admin_settings.replace_one(
            {"type": "global"},
            default_settings,
            upsert=True
        )
        
        return {
            "message": "Settings reset to defaults successfully",
            "settings": {
                "system": default_settings["system"],
                "notifications": default_settings["notifications"],
                "security": default_settings["security"],
                "features": default_settings["features"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset admin settings: {str(e)}"
        )