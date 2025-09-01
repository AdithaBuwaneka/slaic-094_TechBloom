from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback
import logging
import json
from datetime import datetime
from typing import Optional

from app.core.database import db

# Configure logger
logger = logging.getLogger("app_errors")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle different types of exceptions and return appropriate responses"""
        
        # Get user info for logging
        user_id = None
        user_email = None
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # Would need to decode JWT token here for user info
                # For now, we'll leave as None
                pass
        except:
            pass

        error_id = f"error_{int(datetime.utcnow().timestamp())}"
        
        # Log error to database
        await self._log_error_to_db(
            error_id=error_id,
            request=request,
            exception=exc,
            user_id=user_id,
            user_email=user_email
        )
        
        # Log to console/file
        logger.error(
            f"Error ID: {error_id} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"User: {user_email or 'anonymous'} | "
            f"Error: {str(exc)}"
        )

        # Handle different error types
        if isinstance(exc, ValueError):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(exc),
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        elif isinstance(exc, PermissionError):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": "You don't have permission to access this resource",
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        elif isinstance(exc, FileNotFoundError):
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        else:
            # Generic server error
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

    async def _log_error_to_db(
        self, 
        error_id: str, 
        request: Request, 
        exception: Exception,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None
    ):
        """Log error details to database"""
        try:
            error_log = {
                "error_id": error_id,
                "timestamp": datetime.utcnow(),
                "user_id": user_id,
                "user_email": user_email,
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "headers": dict(request.headers),
                    "client_host": request.client.host if request.client else None
                },
                "exception": {
                    "type": type(exception).__name__,
                    "message": str(exception),
                    "traceback": traceback.format_exc()
                },
                "severity": "error",
                "resolved": False
            }
            
            if db.error_logs_collection:
                await db.error_logs_collection.insert_one(error_log)
        except Exception as log_exc:
            # If we can't log to DB, at least log to console
            logger.error(f"Failed to log error to database: {str(log_exc)}")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("api_requests")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - API - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Log request start
        self.logger.info(
            f"Starting {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        
        # Calculate response time
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        # Log request completion
        self.logger.info(
            f"Completed {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {response_time:.2f}ms"
        )
        
        # Log to database for analytics
        await self._log_request_to_db(request, response, start_time, end_time, response_time)
        
        return response
    
    async def _log_request_to_db(
        self, 
        request: Request, 
        response: Response, 
        start_time: datetime, 
        end_time: datetime,
        response_time: float
    ):
        """Log request details to database for analytics"""
        try:
            request_log = {
                "timestamp": start_time,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "referer": request.headers.get("referer"),
                "completed_at": end_time
            }
            
            if db.analytics_events_collection:
                await db.analytics_events_collection.insert_one({
                    "event_type": "api_request",
                    "event_name": "request_completed",
                    "properties": request_log,
                    "timestamp": start_time
                })
        except Exception as log_exc:
            # If we can't log to DB, continue silently
            pass

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CORS headers for mobile apps
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        
        return response