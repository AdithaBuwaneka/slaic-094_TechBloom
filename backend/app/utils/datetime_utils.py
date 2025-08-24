"""
DateTime utilities to handle deprecated datetime.utcnow() usage
"""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Replace deprecated datetime.utcnow() with timezone-aware datetime.now(timezone.utc)
    
    Returns:
        datetime: Current UTC time as timezone-aware datetime object
    """
    return datetime.now(timezone.utc)


def ensure_timezone_aware(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-aware, assuming UTC if naive
    
    Args:
        dt: datetime object that may or may not be timezone-aware
        
    Returns:
        datetime: timezone-aware datetime object
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def safe_fromisoformat(date_string: str, default: datetime = None) -> datetime:
    """
    Safely parse ISO format datetime string with fallback
    
    Args:
        date_string: ISO format datetime string
        default: Default datetime to use if parsing fails
        
    Returns:
        datetime: Parsed datetime or default
    """
    if default is None:
        default = utc_now()
    
    try:
        if isinstance(date_string, str):
            return datetime.fromisoformat(date_string)
        elif isinstance(date_string, datetime):
            return ensure_timezone_aware(date_string)
        else:
            return default
    except (ValueError, TypeError):
        return default