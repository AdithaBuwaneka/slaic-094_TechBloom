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
    
    # Get user from database
    user = await db.database.users.find_one({"user_id": user_id})
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