# Rate Limiting Middleware
# Implements rate limiting for API endpoints to prevent abuse

import time
import redis
from typing import Dict, Optional, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import ErrorCode
import asyncio

class RateLimiter:
    """
    Redis-based rate limiter with sliding window
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            print("Rate limiter connected to Redis")
        except Exception as e:
            print(f"Redis not available for rate limiting: {e}")
            self.redis_available = False
            # Fallback to in-memory rate limiting
            self.memory_store: Dict[str, Dict[str, Any]] = {}
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        identifier: str = "default"
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limit
        Returns (is_allowed, rate_limit_info)
        """
        current_time = int(time.time())
        
        if self.redis_available:
            return await self._redis_check(key, limit, window_seconds, current_time)
        else:
            return await self._memory_check(key, limit, window_seconds, current_time)
    
    async def _redis_check(self, key: str, limit: int, window_seconds: int, current_time: int) -> tuple[bool, Dict[str, Any]]:
        """
        Redis-based rate limiting with sliding window
        """
        try:
            pipe = self.redis_client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, current_time - window_seconds)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            current_count = results[1] + 1  # +1 for the request we just added
            
            rate_limit_info = {
                "limit": limit,
                "remaining": max(0, limit - current_count),
                "reset_time": current_time + window_seconds,
                "window_seconds": window_seconds
            }
            
            if current_count > limit:
                # Remove the request we just added since it's not allowed
                self.redis_client.zrem(key, str(current_time))
                return False, rate_limit_info
            
            return True, rate_limit_info
            
        except Exception as e:
            print(f"Redis rate limiting error: {e}")
            # Fallback to allowing the request if Redis fails
            return True, {
                "limit": limit,
                "remaining": limit - 1,
                "reset_time": current_time + window_seconds,
                "window_seconds": window_seconds
            }
    
    async def _memory_check(self, key: str, limit: int, window_seconds: int, current_time: int) -> tuple[bool, Dict[str, Any]]:
        """
        In-memory rate limiting fallback
        """
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "last_cleanup": current_time}
        
        store = self.memory_store[key]
        
        # Clean up old requests (every 60 seconds)
        if current_time - store["last_cleanup"] > 60:
            store["requests"] = [req_time for req_time in store["requests"] 
                               if req_time > current_time - window_seconds]
            store["last_cleanup"] = current_time
        
        # Remove requests outside the window
        store["requests"] = [req_time for req_time in store["requests"] 
                           if req_time > current_time - window_seconds]
        
        current_count = len(store["requests"])
        
        rate_limit_info = {
            "limit": limit,
            "remaining": max(0, limit - current_count - 1),
            "reset_time": current_time + window_seconds,
            "window_seconds": window_seconds
        }
        
        if current_count >= limit:
            return False, rate_limit_info
        
        # Add current request
        store["requests"].append(current_time)
        
        return True, rate_limit_info

# Global rate limiter instance
rate_limiter = RateLimiter()

class RateLimitMiddleware:
    """
    Middleware to apply rate limiting to requests
    """
    
    def __init__(self, app):
        self.app = app
        
        # Rate limit configurations for different endpoints
        self.rate_limits = {
            # Authentication endpoints
            "/api/v1/auth/login": {"limit": 5, "window": 300},  # 5 attempts per 5 minutes
            "/api/v1/auth/register": {"limit": 3, "window": 3600},  # 3 attempts per hour
            "/api/v1/auth/refresh": {"limit": 10, "window": 300},  # 10 refreshes per 5 minutes
            
            # Travel planning endpoints
            "/api/v1/travel/plan-route": {"limit": 30, "window": 300},  # 30 requests per 5 minutes
            
            # Mobile endpoints
            "/api/v1/mobile/register-device": {"limit": 5, "window": 3600},  # 5 per hour
            "/api/v1/mobile/send-test-notification": {"limit": 3, "window": 3600},  # 3 per hour
            
            # Admin endpoints (more restrictive)
            "/api/v1/admin/create-admin": {"limit": 1, "window": 3600},  # 1 per hour
            "/api/v1/admin/notifications/broadcast": {"limit": 5, "window": 3600},  # 5 per hour
            
            # Community reporting
            "/api/v1/community/traffic": {"limit": 10, "window": 300},  # 10 reports per 5 minutes
            "/api/v1/community/delays": {"limit": 10, "window": 300},  # 10 reports per 5 minutes
            
            # Default rate limit
            "default": {"limit": 100, "window": 300}  # 100 requests per 5 minutes
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Check rate limit
        rate_limit_result = await self.check_rate_limit(request)
        
        if not rate_limit_result["allowed"]:
            # Return rate limit exceeded response
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error_code": ErrorCode.RATE_LIMIT_EXCEEDED.value,
                    "message": "Rate limit exceeded",
                    "details": rate_limit_result["rate_limit_info"],
                    "timestamp": int(time.time())
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limit_result["rate_limit_info"]["limit"]),
                    "X-RateLimit-Remaining": str(rate_limit_result["rate_limit_info"]["remaining"]),
                    "X-RateLimit-Reset": str(rate_limit_result["rate_limit_info"]["reset_time"]),
                    "Retry-After": str(rate_limit_result["rate_limit_info"]["window_seconds"])
                }
            )
            await response(scope, receive, send)
            return
        
        # Add rate limit headers to response
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers.update({
                    b"x-ratelimit-limit": str(rate_limit_result["rate_limit_info"]["limit"]).encode(),
                    b"x-ratelimit-remaining": str(rate_limit_result["rate_limit_info"]["remaining"]).encode(),
                    b"x-ratelimit-reset": str(rate_limit_result["rate_limit_info"]["reset_time"]).encode()
                })
                message["headers"] = list(headers.items())
            await send(message)
        
        await self.app(scope, receive, send_with_headers)
    
    async def check_rate_limit(self, request: Request) -> Dict[str, Any]:
        """
        Check if the request should be rate limited
        """
        # Get client identifier (IP address + user if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        user_identifier = client_ip
        
        # Try to get user ID from authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("sub", "")
                if user_id:
                    user_identifier = f"{user_id}:{client_ip}"
            except:
                pass  # Invalid token, continue with IP-based limiting
        
        # Get rate limit configuration for this endpoint
        path = request.url.path
        rate_config = self.rate_limits.get(path, self.rate_limits["default"])
        
        # Create rate limit key
        rate_limit_key = f"rate_limit:{path}:{user_identifier}"
        
        # Check rate limit
        is_allowed, rate_limit_info = await rate_limiter.is_allowed(
            key=rate_limit_key,
            limit=rate_config["limit"],
            window_seconds=rate_config["window"]
        )
        
        return {
            "allowed": is_allowed,
            "rate_limit_info": rate_limit_info,
            "path": path,
            "identifier": user_identifier
        }

# Special rate limiting decorators for specific use cases
def rate_limit(limit: int, window: int):
    """
    Decorator for applying custom rate limits to specific endpoints
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented to work with the specific endpoint
            # For now, we rely on the middleware for rate limiting
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Rate limiting utility functions
async def check_user_rate_limit(user_id: str, action: str, limit: int, window: int) -> bool:
    """
    Check rate limit for specific user actions
    """
    key = f"user_action:{user_id}:{action}"
    is_allowed, _ = await rate_limiter.is_allowed(key, limit, window)
    return is_allowed

async def get_rate_limit_status(user_id: str, action: str) -> Dict[str, Any]:
    """
    Get current rate limit status for a user action
    """
    key = f"user_action:{user_id}:{action}"
    current_time = int(time.time())
    
    if rate_limiter.redis_available:
        try:
            count = rate_limiter.redis_client.zcard(key)
            return {
                "current_count": count,
                "limit": 100,  # Default, should be configurable
                "window_seconds": 300,
                "reset_time": current_time + 300
            }
        except:
            pass
    
    return {
        "current_count": 0,
        "limit": 100,
        "window_seconds": 300,
        "reset_time": current_time + 300
    }