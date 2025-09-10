# Authentication Middleware and Dependencies
# JWT token validation and user role checking

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from app.services.auth_service import auth_service
from app.core.database import db

# Security scheme for JWT tokens
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = auth_service.verify_token(token, "access")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Debug logging
    print(f"[AUTH DEBUG] Looking up user_id: {user_id}")
    print(f"[AUTH DEBUG] Database available: {db.database is not None}")
    
    # Get user from database with fresh connection
    try:
        # Try direct MongoDB connection to ensure we're using the right database
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.core.config import settings
        
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.DATABASE_NAME]
        
        # Debug the query
        print(f"[AUTH DEBUG] Querying: {{'user_id': '{user_id}'}}")
        
        # Also try listing all users to debug
        all_users = await database.users.find({}).limit(5).to_list(length=5)
        print(f"[AUTH DEBUG] Total users found: {len(all_users)}")
        for u in all_users:
            print(f"[AUTH DEBUG] User in DB: {u['user_id']} | {u['email']} | {u['role']}")
        
        user = await database.users.find_one({"user_id": user_id})
        print(f"[AUTH DEBUG] User lookup result: {user is not None}")
        if user:
            print(f"[AUTH DEBUG] User email: {user.get('email')}, role: {user.get('role')}")
        
        client.close()
    except Exception as e:
        print(f"[AUTH DEBUG] Database query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query failed"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Remove password hash from response
    user.pop("password_hash", None)
    user.pop("_id", None)
    
    # Override role with JWT token role (JWT is the source of truth for permissions)
    user["role"] = payload.get("role", user.get("role"))
    
    return user

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current active user (alias for get_current_user)
    """
    return current_user

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user and verify admin role
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get current user if token provided, otherwise return None
    Useful for endpoints that work with or without authentication
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        payload = auth_service.verify_token(token, "access")
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user from database
        user = await db.database.users.find_one({"user_id": user_id})
        if not user or not user.get("is_active", True):
            return None
        
        # Remove password hash from response
        user.pop("password_hash", None)
        user.pop("_id", None)
        
        return user
    except Exception:
        return None

class RoleChecker:
    """
    Role-based access control dependency
    """
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user

# Pre-defined role checkers
require_admin = RoleChecker(["admin"])
require_user_or_admin = RoleChecker(["user", "admin"])
require_user = RoleChecker(["user"])