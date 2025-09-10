# Centralized Error Handler Middleware
# Handles all exceptions and provides consistent error responses

import logging
import traceback
from datetime import datetime
from typing import Any, Dict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    TransitCompanionException,
    ErrorCode,
    create_error_response
)
from app.core.database import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """
    Middleware to handle all exceptions and provide consistent error responses
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            response = await self.handle_exception(request, exc)
            await response(scope, receive, send)

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle different types of exceptions and return appropriate responses
        """
        
        # Log the exception
        await self.log_exception(request, exc)
        
        # Handle custom Transit Companion exceptions
        if isinstance(exc, TransitCompanionException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error_code": exc.error_code.value,
                    "message": exc.message,
                    "details": exc.details,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            )
        
        # Handle FastAPI validation errors
        elif isinstance(exc, RequestValidationError):
            errors = []
            for error in exc.errors():
                errors.append({
                    "field": " -> ".join(str(x) for x in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error_code": ErrorCode.VALIDATION_ERROR.value,
                    "message": "Validation error",
                    "details": {"validation_errors": errors},
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            )
        
        # Handle standard HTTP exceptions
        elif isinstance(exc, (HTTPException, StarletteHTTPException)):
            # Map common HTTP status codes to error codes
            error_code_map = {
                400: ErrorCode.VALIDATION_ERROR,
                401: ErrorCode.AUTH_TOKEN_INVALID,
                403: ErrorCode.AUTH_PERMISSION_DENIED,
                404: ErrorCode.NOT_FOUND,
                409: ErrorCode.USER_ALREADY_EXISTS,
                429: ErrorCode.RATE_LIMIT_EXCEEDED,
                500: ErrorCode.INTERNAL_SERVER_ERROR,
                503: ErrorCode.EXTERNAL_API_UNAVAILABLE
            }
            
            error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error_code": error_code.value,
                    "message": str(exc.detail) if hasattr(exc, 'detail') else str(exc),
                    "details": {},
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            )
        
        # Handle database connection errors
        elif "ConnectionFailure" in str(type(exc)) or "ServerSelectionTimeoutError" in str(type(exc)):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error_code": ErrorCode.DATABASE_CONNECTION_ERROR.value,
                    "message": "Database connection error",
                    "details": {"service": "mongodb"},
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            )
        
        # Handle all other unexpected exceptions
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error_code": ErrorCode.INTERNAL_SERVER_ERROR.value,
                    "message": "An unexpected error occurred",
                    "details": {
                        "error_type": type(exc).__name__,
                        "error_message": str(exc) if str(exc) else "Unknown error"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            )
    
    async def log_exception(self, request: Request, exc: Exception):
        """
        Log exception details for monitoring and debugging
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.utcnow(),
                "level": "ERROR",
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "path": str(request.url.path),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "traceback": traceback.format_exc() if not isinstance(exc, TransitCompanionException) else None
            }
            
            # Add user info if available
            if hasattr(request.state, 'user'):
                log_entry["user_id"] = getattr(request.state.user, 'user_id', 'unknown')
            
            # Store in database
            try:
                await db.database.error_logs.insert_one(log_entry)
            except Exception as db_error:
                # If database logging fails, at least log to console
                logger.error(f"Failed to log error to database: {db_error}")
            
            # Also log to console
            logger.error(f"Exception in {request.method} {request.url.path}: {exc}")
            
            # For non-custom exceptions, log the full traceback
            if not isinstance(exc, TransitCompanionException):
                logger.error(traceback.format_exc())
                
        except Exception as log_error:
            # If logging fails, don't crash the application
            logger.error(f"Failed to log exception: {log_error}")

# Custom exception handlers for specific FastAPI usage
async def transit_companion_exception_handler(request: Request, exc: TransitCompanionException) -> JSONResponse:
    """
    Handle custom Transit Companion exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code.value,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI validation errors
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": ErrorCode.VALIDATION_ERROR.value,
            "message": "Validation error",
            "details": {"validation_errors": errors},
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle standard HTTP exceptions
    """
    # Map common HTTP status codes to error codes
    error_code_map = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.AUTH_TOKEN_INVALID,
        403: ErrorCode.AUTH_PERMISSION_DENIED,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.USER_ALREADY_EXISTS,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        503: ErrorCode.EXTERNAL_API_UNAVAILABLE
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": error_code.value,
            "message": str(exc.detail),
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )