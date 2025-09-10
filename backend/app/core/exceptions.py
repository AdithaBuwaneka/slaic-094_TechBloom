# Centralized Exception Handling for Transit Companion Backend
# Custom exceptions and error handling utilities

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from enum import Enum

class ErrorCode(str, Enum):
    # Authentication Errors
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_CREDENTIALS_INVALID = "AUTH_CREDENTIALS_INVALID"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"
    AUTH_USER_INACTIVE = "AUTH_USER_INACTIVE"
    AUTH_PERMISSION_DENIED = "AUTH_PERMISSION_DENIED"
    
    # User Management Errors
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_VALIDATION_ERROR = "USER_VALIDATION_ERROR"
    USER_PREFERENCES_ERROR = "USER_PREFERENCES_ERROR"
    
    # Travel Planning Errors
    TRAVEL_INVALID_LOCATION = "TRAVEL_INVALID_LOCATION"
    TRAVEL_ROUTE_NOT_FOUND = "TRAVEL_ROUTE_NOT_FOUND"
    TRAVEL_MODE_INVALID = "TRAVEL_MODE_INVALID"
    TRAVEL_AGENT_ERROR = "TRAVEL_AGENT_ERROR"
    TRAVEL_EXTERNAL_API_ERROR = "TRAVEL_EXTERNAL_API_ERROR"
    
    # Mobile App Errors
    MOBILE_DEVICE_REGISTRATION_ERROR = "MOBILE_DEVICE_REGISTRATION_ERROR"
    MOBILE_PUSH_NOTIFICATION_ERROR = "MOBILE_PUSH_NOTIFICATION_ERROR"
    MOBILE_LOCATION_ERROR = "MOBILE_LOCATION_ERROR"
    
    # Admin Dashboard Errors
    ADMIN_OPERATION_FORBIDDEN = "ADMIN_OPERATION_FORBIDDEN"
    ADMIN_USER_CREATION_ERROR = "ADMIN_USER_CREATION_ERROR"
    ADMIN_ANALYTICS_ERROR = "ADMIN_ANALYTICS_ERROR"
    
    # Database Errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_OPERATION_ERROR = "DATABASE_OPERATION_ERROR"
    DATABASE_VALIDATION_ERROR = "DATABASE_VALIDATION_ERROR"
    
    # External Service Errors
    EXTERNAL_API_UNAVAILABLE = "EXTERNAL_API_UNAVAILABLE"
    EXTERNAL_API_RATE_LIMIT = "EXTERNAL_API_RATE_LIMIT"
    EXTERNAL_API_AUTHENTICATION = "EXTERNAL_API_AUTHENTICATION"
    
    # General Errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

class TransitCompanionException(Exception):
    """
    Base exception class for Transit Companion application
    """
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationException(TransitCompanionException):
    """Authentication related exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.AUTH_CREDENTIALS_INVALID, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )

class AuthorizationException(TransitCompanionException):
    """Authorization related exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.AUTH_PERMISSION_DENIED, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )

class ValidationException(TransitCompanionException):
    """Data validation exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.VALIDATION_ERROR, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class NotFoundException(TransitCompanionException):
    """Resource not found exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.NOT_FOUND, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

class ConflictException(TransitCompanionException):
    """Resource conflict exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.USER_ALREADY_EXISTS, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )

class ExternalServiceException(TransitCompanionException):
    """External service related exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.EXTERNAL_API_UNAVAILABLE, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )

class DatabaseException(TransitCompanionException):
    """Database related exceptions"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.DATABASE_OPERATION_ERROR, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class RateLimitException(TransitCompanionException):
    """Rate limiting exceptions"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )

def create_http_exception(exception: TransitCompanionException) -> HTTPException:
    """
    Convert custom exception to HTTPException
    """
    return HTTPException(
        status_code=exception.status_code,
        detail={
            "error_code": exception.error_code.value,
            "message": exception.message,
            "details": exception.details
        }
    )

def create_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create standardized error response
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code.value,
            "message": message,
            "details": details or {}
        }
    )

# Common error responses for quick use
def unauthorized_error(message: str = "Authentication required") -> HTTPException:
    return create_error_response(
        ErrorCode.AUTH_TOKEN_INVALID,
        message,
        status.HTTP_401_UNAUTHORIZED
    )

def forbidden_error(message: str = "Access denied") -> HTTPException:
    return create_error_response(
        ErrorCode.AUTH_PERMISSION_DENIED,
        message,
        status.HTTP_403_FORBIDDEN
    )

def not_found_error(message: str = "Resource not found") -> HTTPException:
    return create_error_response(
        ErrorCode.NOT_FOUND,
        message,
        status.HTTP_404_NOT_FOUND
    )

def validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    return create_error_response(
        ErrorCode.VALIDATION_ERROR,
        message,
        status.HTTP_400_BAD_REQUEST,
        details
    )

def conflict_error(message: str = "Resource already exists") -> HTTPException:
    return create_error_response(
        ErrorCode.USER_ALREADY_EXISTS,
        message,
        status.HTTP_409_CONFLICT
    )

def internal_server_error(message: str = "Internal server error") -> HTTPException:
    return create_error_response(
        ErrorCode.INTERNAL_SERVER_ERROR,
        message,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )