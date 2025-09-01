from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
import asyncio

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(lambda: deque())
        
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        while self.clients[client_ip] and self.clients[client_ip][0] <= now - self.period:
            self.clients[client_ip].popleft()
            
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
            )
            
        # Add current request
        self.clients[client_ip].append(now)
        
        response = await call_next(request)
        return response

class AgentRateLimitMiddleware(BaseHTTPMiddleware):
    """Stricter rate limiting for AI agent endpoints"""
    def __init__(self, app, calls: int = 20, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(lambda: deque())
        
    async def dispatch(self, request: Request, call_next):
        # Apply stricter limits only to AI agent endpoints
        if any(agent_path in str(request.url.path) for agent_path in [
            '/plan-journey/agentic', '/search/comprehensive', '/disruptions/check',
            '/personalization/recommendations', '/fare/optimize', '/language/translate',
            '/local/insights'
        ]):
            client_ip = request.client.host
            now = time.time()
            
            # Clean old requests
            while self.clients[client_ip] and self.clients[client_ip][0] <= now - self.period:
                self.clients[client_ip].popleft()
                
            # Check agent rate limit (stricter)
            if len(self.clients[client_ip]) >= self.calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"AI Agent rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
                )
                
            # Add current request
            self.clients[client_ip].append(now)
        
        response = await call_next(request)
        return response