from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.models.user import User, UserRole, UserStatus
from app.api.auth import get_current_user
from app.core.database import db

router = APIRouter()

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify user has admin privileges"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_journeys: int
    total_routes: int
    system_health: str

class UserManagement(BaseModel):
    user_id: str
    action: str  # activate, suspend, delete, make_admin, make_user
    reason: Optional[str] = None

@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(admin_user: User = Depends(get_admin_user)):
    """Get comprehensive system statistics"""
    try:
        # User statistics
        total_users = await db.users_collection.count_documents({})
        active_users = await db.users_collection.count_documents({"status": "active"})
        
        # Journey statistics  
        total_journeys = await db.journey_history_collection.count_documents({})
        
        # Route statistics
        bus_routes = await db.bus_routes_collection.count_documents({})
        train_routes = await db.train_routes_collection.count_documents({})
        total_routes = bus_routes + train_routes
        
        return SystemStats(
            total_users=total_users,
            active_users=active_users,
            total_journeys=total_journeys,
            total_routes=total_routes,
            system_health="healthy"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system stats: {str(e)}"
        )

@router.get("/users/list")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(get_admin_user)
):
    """List all users with filtering and pagination"""
    try:
        query = {}
        if status_filter:
            query["status"] = status_filter
        if search:
            query["$or"] = [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        total = await db.users_collection.count_documents(query)
        skip = (page - 1) * limit
        
        users_cursor = db.users_collection.find(query, {"password_hash": 0})\
            .sort("created_at", -1)\
            .skip(skip)\
            .limit(limit)
        
        users = []
        async for user in users_cursor:
            users.append({
                "id": str(user["_id"]),
                "email": user.get("email", ""),
                "full_name": user.get("full_name", ""),
                "role": user.get("role", "user"),
                "status": user.get("status", "active"),
                "created_at": user.get("created_at", "").isoformat() if user.get("created_at") else None,
                "last_login": user.get("last_login", "").isoformat() if user.get("last_login") else None,
                "email_verified": user.get("email_verified", False)
            })
        
        return {
            "users": users,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "has_next": skip + limit < total,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.post("/users/manage")
async def manage_user(
    user_management: UserManagement,
    admin_user: User = Depends(get_admin_user)
):
    """Manage user accounts (suspend, activate, delete, change role)"""
    try:
        user_id = user_management.user_id
        action = user_management.action
        
        # Prevent admin from managing themselves
        if user_id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot perform admin actions on your own account"
            )
        
        # Check if target user exists
        target_user = await db.users_collection.find_one({"_id": user_id})
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = {"updated_at": datetime.utcnow()}
        
        if action == "activate":
            update_data["status"] = "active"
        elif action == "suspend":
            update_data["status"] = "suspended"
        elif action == "make_admin":
            update_data["role"] = "admin"
        elif action == "make_user":
            update_data["role"] = "user"
        elif action == "delete":
            # Soft delete - mark as deleted
            update_data["status"] = "deleted"
            update_data["deleted_at"] = datetime.utcnow()
            update_data["deleted_by"] = admin_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}"
            )
        
        # Log admin action
        admin_log = {
            "admin_id": admin_user.id,
            "admin_email": admin_user.email,
            "target_user_id": user_id,
            "target_user_email": target_user.get("email"),
            "action": action,
            "reason": user_management.reason,
            "timestamp": datetime.utcnow()
        }
        await db.admin_logs_collection.insert_one(admin_log)
        
        # Update user
        await db.users_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        return {
            "message": f"User {action} successful",
            "user_id": user_id,
            "action": action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User management failed: {str(e)}"
        )

@router.get("/analytics/usage")
async def get_usage_analytics(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(get_admin_user)
):
    """Get usage analytics for the specified period"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # New user registrations
        new_users = await db.users_collection.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Journey statistics
        total_journeys = await db.journey_history_collection.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Most popular routes (mock aggregation)
        popular_routes = [
            {"route": "Colombo → Kandy", "count": 150},
            {"route": "Galle → Colombo", "count": 120},
            {"route": "Kandy → Nuwara Eliya", "count": 89}
        ]
        
        # Device statistics
        device_stats = []
        device_cursor = db.devices_collection.aggregate([
            {"$group": {"_id": "$device_type", "count": {"$sum": 1}}}
        ])
        async for device_stat in device_cursor:
            device_stats.append({
                "device_type": device_stat["_id"],
                "count": device_stat["count"]
            })
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "metrics": {
                "new_users": new_users,
                "total_journeys": total_journeys,
                "popular_routes": popular_routes,
                "device_distribution": device_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics failed: {str(e)}"
        )

@router.get("/logs/admin")
async def get_admin_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    admin_user: User = Depends(get_admin_user)
):
    """Get admin action logs"""
    try:
        total = await db.admin_logs_collection.count_documents({})
        skip = (page - 1) * limit
        
        logs_cursor = db.admin_logs_collection.find({})\
            .sort("timestamp", -1)\
            .skip(skip)\
            .limit(limit)
        
        logs = []
        async for log in logs_cursor:
            logs.append({
                "id": str(log["_id"]),
                "admin_email": log.get("admin_email", ""),
                "target_user_email": log.get("target_user_email", ""),
                "action": log.get("action", ""),
                "reason": log.get("reason", ""),
                "timestamp": log.get("timestamp", "").isoformat() if log.get("timestamp") else None
            })
        
        return {
            "logs": logs,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "has_next": skip + limit < total,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin logs: {str(e)}"
        )

@router.post("/routes/add")
async def add_transport_route(
    route_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Add new transport routes"""
    try:
        route_type = route_data.get("type", "bus")
        
        if route_type == "bus":
            collection = db.bus_routes_collection
        elif route_type == "train":
            collection = db.train_routes_collection
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid route type. Must be 'bus' or 'train'"
            )
        
        route_data["created_by"] = admin_user.id
        route_data["created_at"] = datetime.utcnow()
        
        result = await collection.insert_one(route_data)
        
        # Log admin action
        admin_log = {
            "admin_id": admin_user.id,
            "admin_email": admin_user.email,
            "action": "add_route",
            "route_type": route_type,
            "route_id": str(result.inserted_id),
            "timestamp": datetime.utcnow()
        }
        await db.admin_logs_collection.insert_one(admin_log)
        
        return {
            "message": "Route added successfully",
            "route_id": str(result.inserted_id),
            "route_type": route_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add route: {str(e)}"
        )

@router.delete("/routes/{route_id}")
async def delete_transport_route(
    route_id: str,
    route_type: str = Query(..., description="bus or train"),
    admin_user: User = Depends(get_admin_user)
):
    """Delete transport routes"""
    try:
        if route_type == "bus":
            collection = db.bus_routes_collection
        elif route_type == "train":
            collection = db.train_routes_collection
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid route type"
            )
        
        result = await collection.delete_one({"_id": route_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found"
            )
        
        # Log admin action
        admin_log = {
            "admin_id": admin_user.id,
            "admin_email": admin_user.email,
            "action": "delete_route",
            "route_type": route_type,
            "route_id": route_id,
            "timestamp": datetime.utcnow()
        }
        await db.admin_logs_collection.insert_one(admin_log)
        
        return {"message": "Route deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete route: {str(e)}"
        )