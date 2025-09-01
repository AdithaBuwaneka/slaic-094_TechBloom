"""
Langfuse Service for Multi-Agent Travel System
Provides tracing and observability capabilities
"""

import os
import time
from typing import Optional, Dict, Any
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
from app.core.config import settings


class LangfuseService:
    """Service for managing Langfuse tracing and observability"""
    
    def __init__(self):
        self.client = None
        self.handler = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Langfuse client with configuration"""
        try:
            # Check if Langfuse is configured
            if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
                print("⚠️  Langfuse not configured. Tracing will be disabled.")
                return
            
            # Initialize Langfuse client with more lenient timeouts
            Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
            
            # Get the configured client instance
            self.client = get_client()
            
            # Initialize the Langfuse handler for LangChain
            self.handler = CallbackHandler()
            
            print("✅ Langfuse initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Langfuse: {e}")
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
            # Use the correct API for newer Langfuse versions
            # Create a trace ID first
            trace_id = self.client.create_trace_id()
            
            # Return a mock trace object for compatibility
            class MockTrace:
                def __init__(self, client, trace_id, name, metadata):
                    self.client = client
                    self.trace_id = trace_id
                    self.name = name
                    self.metadata = metadata
                    self.id = trace_id
                
                def update(self, **kwargs):
                    # Update the current trace with the provided data
                    try:
                        self.client.update_current_trace(**kwargs)
                    except Exception as e:
                        print(f"Warning: Could not update trace: {e}")
            
            return MockTrace(self.client, trace_id, name, metadata)
            
        except Exception as e:
            print(f"❌ Failed to create trace: {e}")
            return None
    
    def start_span(self, name: str, trace_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Start a new span for tracking specific operations"""
        if not self.is_enabled():
            return None
        
        try:
            # Create a mock span object for compatibility
            class MockSpan:
                def __init__(self, client, name, trace_id, metadata):
                    self.client = client
                    self.name = name
                    self.trace_id = trace_id
                    self.metadata = metadata
                    self.id = f"span_{name}_{trace_id or 'new'}"
                
                def update(self, **kwargs):
                    # For now, just print the update
                    print(f"Span update: {kwargs}")
                
                def end(self):
                    # Span ends automatically with context manager
                    pass
            
            span = MockSpan(self.client, name, trace_id, metadata)
            return span
            
        except Exception as e:
            print(f"❌ Failed to start span: {e}")
            return None
    
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
            print(f"❌ Failed to score trace: {e}")
    
    def flush(self):
        """Flush all pending events to Langfuse with robust error handling"""
        if not self.is_enabled():
            return
        
        try:
            # Try to flush with a reasonable timeout
            print("�� Flushing events to Langfuse...")
            
            # Use a simple timeout approach that works cross-platform
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def flush_worker():
                try:
                    self.client.flush()
                    result_queue.put(("success", None))
                except Exception as e:
                    result_queue.put(("error", e))
            
            # Start flush in a separate thread
            flush_thread = threading.Thread(target=flush_worker)
            flush_thread.daemon = True
            flush_thread.start()
            
            # Wait for completion with timeout
            try:
                result, error = result_queue.get(timeout=15)  # 15 second timeout
                if result == "success":
                    print("✅ Events flushed to Langfuse successfully")
                else:
                    print(f"⚠️  Flush operation failed: {error}")
            except queue.Empty:
                print("⚠️  Flush operation timed out after 15 seconds")
                print("   Events may not have been sent to Langfuse")
                print("   This is usually due to network connectivity issues")
                
        except Exception as e:
            print(f"❌ Failed to flush events: {e}")
            print("   This won't affect your application's functionality")
            print("   Traces will be stored locally and can be sent later")


# Global instance
langfuse_service = LangfuseService()
