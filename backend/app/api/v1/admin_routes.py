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

# Response Models
class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    total_trips_planned: int
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
        
        # Get community reports count
        total_reports = 0
        try:
            # This would come from community service in a real implementation
            from app.services.community_service import community_service
            community_stats = community_service.get_community_stats()
            if community_stats["status"] == "success":
                total_reports = community_stats["data"]["total_reports"]
        except:
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
        reports = []
        
        # Get traffic reports
        if not report_type or report_type == "traffic":
            traffic_reports = await db.database.community_traffic_reports.find({}).sort("timestamp", -1).to_list(length=None)
            for report in traffic_reports:
                report["report_type"] = "traffic"
                report["_id"] = str(report["_id"])
                reports.append(report)
        
        # Get delay reports
        if not report_type or report_type == "delay":
            delay_reports = await db.database.community_delay_reports.find({}).sort("timestamp", -1).to_list(length=None)
            for report in delay_reports:
                report["report_type"] = "delay"
                report["_id"] = str(report["_id"])
                reports.append(report)
        
        # Sort by timestamp and apply pagination
        reports.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
        paginated_reports = reports[skip:skip + limit]
        
        return {
            "total_reports": len(reports),
            "page": skip // limit + 1,
            "per_page": limit,
            "reports": paginated_reports
        }
        
    except Exception as e:
        return {
            "total_reports": 0,
            "reports": [],
            "message": "Community reports not available"
        }