"""
Cache management for API responses to reduce quota usage
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os

class SimpleCache:
    def __init__(self, cache_duration_minutes: int = 60):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def _get_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate cache key from request data"""
        cache_string = json.dumps(data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, key_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response if valid"""
        cache_key = self._get_cache_key(key_data)
        
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if datetime.now() < cached_item['expires_at']:
                print(f"Cache hit for key: {cache_key[:8]}...")
                return cached_item['data']
            else:
                # Remove expired item
                del self.cache[cache_key]
        
        return None
    
    def set(self, key_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Cache response data"""
        cache_key = self._get_cache_key(key_data)
        
        self.cache[cache_key] = {
            'data': response_data,
            'expires_at': datetime.now() + self.cache_duration,
            'created_at': datetime.now()
        }
        print(f"Cached response for key: {cache_key[:8]}...")
    
    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, value in self.cache.items() 
            if now >= value['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60,
            "oldest_entry": min([v['created_at'] for v in self.cache.values()]) if self.cache else None,
            "newest_entry": max([v['created_at'] for v in self.cache.values()]) if self.cache else None
        }

# Global cache instances
chatbot_cache = SimpleCache(cache_duration_minutes=30)  # 30 minute cache for chatbot responses
route_cache = SimpleCache(cache_duration_minutes=15)    # 15 minute cache for route data
search_cache = SimpleCache(cache_duration_minutes=60)   # 1 hour cache for search results