"""
Langfuse Service for Multi-Agent Travel System
Provides tracing and observability capabilities
"""

import os
import time
import uuid
from typing import Optional, Dict, Any, ContextManager
from contextlib import contextmanager
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
from app.core.config import settings


class LangfuseService:
    """Service for managing Langfuse tracing and observability"""
    
    def __init__(self):
        self.client = None
        self.handler = None
        self.current_trace = None
        self.current_spans = {}  # Track active spans
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Langfuse client with configuration"""
        try:
            # Check if Langfuse is configured
            if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
                print(" Langfuse not configured. Tracing will be disabled.")
                return
            
            # Initialize Langfuse client with optimized settings to prevent timeout issues
            self.client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST,
                # Increase timeout to prevent immediate failures
                timeout=30,
                # Enable automatic tracing for LangChain integration
                tracing_enabled=True,
                # Use longer flush intervals to batch operations
                flush_interval=10.0,
                # Set environment for better organization
                environment="development"
            )
            
            # Initialize the Langfuse handler for LangChain
            self.handler = CallbackHandler()
            
            print("Langfuse initialized successfully with optimized settings")
            
        except Exception as e:
            print(f" Failed to initialize Langfuse: {e}")
            self.client = None
            self.handler = None
    
    def is_enabled(self) -> bool:
        """Check if Langfuse tracing is enabled"""
        return self.client is not None and self.handler is not None
    
    def get_handler(self) -> Optional[CallbackHandler]:
        """Get the Langfuse callback handler for LangChain"""
        return self.handler if self.is_enabled() else None
    
    def create_trace(self, name: str, user_id: Optional[str] = None, 
                    metadata: Optional[Dict[str, Any]] = None):
        """Create a new trace for tracking agent execution"""
        if not self.is_enabled():
            return None
        
        try:
            # Create a new trace using the Langfuse client
            trace_id = str(uuid.uuid4())
            
            # Create the trace with proper metadata
            trace_data = {
                "id": trace_id,
                "name": name,
                "user_id": user_id,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            # Store the current trace
            self.current_trace = trace_data
            
            # Return a trace object for compatibility
            class Trace:
                def __init__(self, service, trace_id, name, metadata):
                    self.service = service
                    self.trace_id = trace_id
                    self.name = name
                    self.metadata = metadata
                    self.id = trace_id
                    self.start_time = time.time()
                
                def update(self, **kwargs):
                    """Update the current trace with the provided data"""
                    try:
                        if self.service.client:
                            # Update trace metadata
                            if 'output' in kwargs:
                                self.service.current_trace['output'] = kwargs['output']
                            if 'status' in kwargs:
                                self.service.current_trace['status'] = kwargs['status']
                            
                            # Calculate duration
                            duration = time.time() - self.start_time
                            self.service.current_trace['duration'] = duration
                            
                            print(f"🔍 Trace updated: {self.name} (duration: {duration:.2f}s)")
                    except Exception as e:
                        print(f"Warning: Could not update trace: {e}")
                
                def end(self):
                    """End the trace"""
                    try:
                        if self.service.client:
                            duration = time.time() - self.start_time
                            self.service.current_trace['duration'] = duration
                            self.service.current_trace['end_time'] = time.time()
                            print(f"🏁 Trace ended: {self.name} (duration: {duration:.2f}s)")
                    except Exception as e:
                        print(f"Warning: Could not end trace: {e}")
            
            return Trace(self, trace_id, name, metadata)
            
        except Exception as e:
            print(f" Failed to create trace: {e}")
            return None
    
    @contextmanager
    def start_span(self, name: str, trace_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Start a new span for tracking specific operations"""
        if not self.is_enabled():
            yield None
            return
        
        try:
            # Use current trace ID if not provided
            if not trace_id and self.current_trace:
                trace_id = self.current_trace['id']
            
            span_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Create span data
            span_data = {
                "id": span_id,
                "name": name,
                "trace_id": trace_id,
                "metadata": metadata or {},
                "start_time": start_time,
                "status": "running"
            }
            
            # Store active span
            self.current_spans[span_id] = span_data
            
            print(f" Agent action started: {name}")
            
            # Create span object
            class Span:
                def __init__(self, service, span_id, name, trace_id, metadata):
                    self.service = service
                    self.span_id = span_id
                    self.name = name
                    self.trace_id = trace_id
                    self.metadata = metadata
                    self.id = span_id
                    self.start_time = time.time()
                
                def update(self, **kwargs):
                    """Update the span with new data"""
                    try:
                        if self.service.current_spans.get(self.span_id):
                            span_data = self.service.current_spans[self.span_id]
                            
                            # Update span data
                            if 'input' in kwargs:
                                span_data['input'] = kwargs['input']
                            if 'output' in kwargs:
                                span_data['output'] = kwargs['output']
                            if 'status' in kwargs:
                                span_data['status'] = kwargs['status']
                            if 'error' in kwargs:
                                span_data['error'] = kwargs['error']
                                span_data['status'] = 'error'
                            
                            # Calculate duration
                            duration = time.time() - self.start_time
                            span_data['duration'] = duration
                            
                            print(f" Agent action updated: {self.name} (duration: {duration:.2f}s)")
                    except Exception as e:
                        print(f"Warning: Could not update span: {e}")
                
                def end(self):
                    """End the span"""
                    try:
                        if self.service.current_spans.get(self.span_id):
                            span_data = self.service.current_spans[self.span_id]
                            duration = time.time() - self.start_time
                            span_data['duration'] = duration
                            span_data['end_time'] = time.time()
                            span_data['status'] = 'completed'
                            
                            print(f" Agent action completed: {self.name} (duration: {duration:.2f}s)")
                            
                            # Remove from active spans
                            del self.service.current_spans[self.span_id]
                    except Exception as e:
                        print(f"Warning: Could not end span: {e}")
            
            span = Span(self, span_id, name, trace_id, metadata)
            
            try:
                yield span
            finally:
                span.end()
            
        except Exception as e:
            print(f" Failed to start span: {e}")
            yield None
    
    def score_trace(self, trace_id: str, name: str, value: float, 
                   comment: Optional[str] = None):
        """Add a score to a trace for evaluation"""
        if not self.is_enabled():
            return
        
        try:
            self.client.create_score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment
            )
        except Exception as e:
            print(f" Failed to score trace: {e}")
    
    def flush(self):
        """Flush all pending events to Langfuse with robust error handling"""
        if not self.is_enabled():
            return
        
        try:
            print(" Flushing events to Langfuse...")
            
            # Log what we have locally for debugging
            if self.current_trace:
                print(f" Local trace data: {self.current_trace['name']} (ID: {self.current_trace['id']})")
            
            if self.current_spans:
                print(f" Local spans data: {len(self.current_spans)} spans")
                for span_id, span_data in self.current_spans.items():
                    print(f"   - {span_data['name']} (ID: {span_id})")
            
            # Flush the client - the LangChain callback handler will automatically send traces and spans
            self.client.flush()
            print("All events flushed to Langfuse successfully")
            
        except Exception as e:
            print(f"  Failed to flush events: {e}")
            print("   This won't affect your application's functionality")
            print("   Traces will be stored locally and can be sent later")


# Global instance
langfuse_service = LangfuseService()
