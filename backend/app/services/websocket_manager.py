from typing import Dict, List, Optional, Set, Callable, Any
from fastapi import WebSocket, WebSocketDisconnect
from app.models.websocket import (
    WebSocketMessage, MessageType, SubscriptionType, SubscriptionRequest,
    ClientConnection, ConnectionStatus, LiveUpdate, WebSocketConfig,
    ConnectionMetrics, WebSocketError, NotificationData
)
from app.models.transport_data import Location
import asyncio
import json
import uuid
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import weakref


class WebSocketConnectionManager:
    """
    Advanced WebSocket Connection Manager for Real-time Transit Updates
    
    Manages WebSocket connections, subscriptions, message routing, and real-time
    data streaming for the transit companion application.
    """
    
    def __init__(self, config: WebSocketConfig = None):
        self.config = config or WebSocketConfig()
        
        # Connection management
        self.connections: Dict[str, WebSocket] = {}
        self.client_connections: Dict[str, ClientConnection] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Subscription management
        self.subscriptions: Dict[SubscriptionType, Set[str]] = defaultdict(set)
        self.client_subscriptions: Dict[str, List[SubscriptionRequest]] = defaultdict(list)
        self.location_subscriptions: Dict[str, List[tuple]] = defaultdict(list)  # location_key -> [(connection_id, radius)]
        
        # Message handling
        self.message_queue: Dict[str, asyncio.Queue] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.broadcast_queue: asyncio.Queue = asyncio.Queue()
        
        # Monitoring and metrics
        self.metrics = ConnectionMetrics()
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        
        # Setup default message handlers
        self._setup_message_handlers()
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def _setup_message_handlers(self):
        """Set up default message handlers"""
        self.message_handlers.update({
            MessageType.PING: self._handle_ping,
            MessageType.SUBSCRIBE: self._handle_subscribe,
            MessageType.UNSUBSCRIBE: self._handle_unsubscribe,
            MessageType.CONNECT: self._handle_connect,
            MessageType.DISCONNECT: self._handle_disconnect,
        })
    
    async def start(self):
        """Start the WebSocket manager and background tasks"""
        if not self.is_monitoring:
            self.is_monitoring = True
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            # Start broadcast processor
            broadcast_task = asyncio.create_task(self._process_broadcasts())
            self.background_tasks.append(broadcast_task)
            
            self.logger.info("WebSocket Manager started")
    
    async def stop(self):
        """Stop the WebSocket manager and cleanup"""
        if self.is_monitoring:
            self.is_monitoring = False
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            self.background_tasks.clear()
            
            # Close all connections
            await self._close_all_connections()
            
            self.logger.info("WebSocket Manager stopped")
    
    async def connect(self, websocket: WebSocket, connection_id: str = None, 
                     user_id: str = None, metadata: Dict[str, Any] = None) -> str:
        """Connect a new WebSocket client"""
        
        if connection_id is None:
            connection_id = f"conn_{uuid.uuid4().hex[:8]}"
        
        try:
            await websocket.accept()
            
            # Store connection
            self.connections[connection_id] = websocket
            self.connection_metadata[connection_id] = metadata or {}
            
            # Create client connection record
            client_connection = ClientConnection(
                connection_id=connection_id,
                user_id=user_id,
                status=ConnectionStatus.CONNECTED,
                user_agent=metadata.get("user_agent") if metadata else None,
                ip_address=metadata.get("ip_address") if metadata else None,
                platform=metadata.get("platform") if metadata else None
            )
            self.client_connections[connection_id] = client_connection
            
            # Initialize message queue
            self.message_queue[connection_id] = asyncio.Queue(maxsize=self.config.message_queue_size)
            
            # Update metrics
            self.metrics.total_connections += 1
            self.metrics.active_connections += 1
            
            # Send connection confirmation
            await self._send_message(connection_id, WebSocketMessage(
                type=MessageType.CONNECT,
                payload={
                    "connection_id": connection_id,
                    "status": "connected",
                    "server_time": datetime.utcnow().isoformat(),
                    "config": {
                        "ping_interval": self.config.ping_interval_seconds,
                        "max_subscriptions": self.config.max_subscriptions_per_client
                    }
                }
            ))
            
            # Start message processor for this connection
            processor_task = asyncio.create_task(self._process_connection_messages(connection_id))
            self.background_tasks.append(processor_task)
            
            self.logger.info(f"Client connected: {connection_id}")
            return connection_id
            
        except Exception as e:
            self.logger.error(f"Failed to connect client {connection_id}: {e}")
            if connection_id in self.connections:
                del self.connections[connection_id]
            raise
    
    async def disconnect(self, connection_id: str, reason: str = "client_disconnect"):
        """Disconnect a WebSocket client"""
        try:
            if connection_id in self.connections:
                # Update client status
                if connection_id in self.client_connections:
                    self.client_connections[connection_id].status = ConnectionStatus.DISCONNECTING
                
                # Remove subscriptions
                await self._remove_all_subscriptions(connection_id)
                
                # Close WebSocket
                websocket = self.connections[connection_id]
                try:
                    await websocket.close()
                except:
                    pass  # Connection might already be closed
                
                # Cleanup
                del self.connections[connection_id]
                if connection_id in self.client_connections:
                    del self.client_connections[connection_id]
                if connection_id in self.connection_metadata:
                    del self.connection_metadata[connection_id]
                if connection_id in self.message_queue:
                    del self.message_queue[connection_id]
                
                # Update metrics
                self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
                
                self.logger.info(f"Client disconnected: {connection_id}, reason: {reason}")
                
        except Exception as e:
            self.logger.error(f"Error disconnecting client {connection_id}: {e}")
    
    async def subscribe(self, connection_id: str, subscription: SubscriptionRequest) -> bool:
        """Subscribe a client to updates"""
        try:
            if connection_id not in self.client_connections:
                return False
            
            client = self.client_connections[connection_id]
            
            # Check subscription limits
            if len(client.active_subscriptions) >= client.max_subscriptions:
                await self._send_error(connection_id, "subscription_limit_exceeded", 
                                     f"Maximum {client.max_subscriptions} subscriptions allowed")
                return False
            
            # Add subscription
            client.active_subscriptions.append(subscription)
            client.subscription_count += 1
            
            # Add to subscription index
            self.subscriptions[subscription.subscription_type].add(connection_id)
            self.client_subscriptions[connection_id].append(subscription)
            
            # Handle location-based subscriptions
            if subscription.location:
                location_key = f"{subscription.location.latitude:.4f},{subscription.location.longitude:.4f}"
                self.location_subscriptions[location_key].append((connection_id, subscription.radius_km))
            
            # Update metrics
            self.metrics.subscriptions_count += 1
            
            # Send confirmation
            await self._send_message(connection_id, WebSocketMessage(
                type=MessageType.SUBSCRIPTION_CONFIRMED,
                payload={
                    "subscription_type": subscription.subscription_type,
                    "filters": subscription.filters,
                    "status": "subscribed"
                }
            ))
            
            self.logger.info(f"Client {connection_id} subscribed to {subscription.subscription_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe client {connection_id}: {e}")
            await self._send_error(connection_id, "subscription_failed", str(e))
            return False
    
    async def unsubscribe(self, connection_id: str, subscription_type: SubscriptionType) -> bool:
        """Unsubscribe a client from updates"""
        try:
            if connection_id not in self.client_connections:
                return False
            
            client = self.client_connections[connection_id]
            
            # Remove from client subscriptions
            client.active_subscriptions = [
                sub for sub in client.active_subscriptions 
                if sub.subscription_type != subscription_type
            ]
            client.subscription_count = len(client.active_subscriptions)
            
            # Remove from subscription index
            if connection_id in self.subscriptions[subscription_type]:
                self.subscriptions[subscription_type].remove(connection_id)
            
            # Remove from client subscription list
            self.client_subscriptions[connection_id] = [
                sub for sub in self.client_subscriptions[connection_id]
                if sub.subscription_type != subscription_type
            ]
            
            # Update metrics
            self.metrics.subscriptions_count = max(0, self.metrics.subscriptions_count - 1)
            
            self.logger.info(f"Client {connection_id} unsubscribed from {subscription_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe client {connection_id}: {e}")
            return False
    
    async def broadcast_update(self, update: LiveUpdate):
        """Broadcast an update to all relevant subscribers"""
        await self.broadcast_queue.put(update)
    
    async def send_notification(self, notification: NotificationData, 
                              target_connections: List[str] = None):
        """Send notification to specific connections or broadcast"""
        
        message = WebSocketMessage(
            type=MessageType.SYSTEM_ALERT,
            payload=notification.model_dump(),
            priority=2  # High priority for notifications
        )
        
        if target_connections:
            # Send to specific connections
            for connection_id in target_connections:
                if connection_id in self.connections:
                    await self._send_message(connection_id, message)
        else:
            # Broadcast to all subscribed connections
            for subscription_type in notification.target_subscriptions:
                for connection_id in self.subscriptions[subscription_type]:
                    if connection_id in self.connections:
                        await self._send_message(connection_id, message)
    
    async def _send_message(self, connection_id: str, message: WebSocketMessage):
        """Send a message to a specific connection"""
        if connection_id not in self.connections:
            return False
        
        try:
            # Check rate limiting
            if not self._check_rate_limit(connection_id):
                await self._send_error(connection_id, "rate_limit_exceeded", 
                                     "Too many messages sent")
                return False
            
            # Send message
            websocket = self.connections[connection_id]
            message_data = message.model_dump()
            await websocket.send_text(json.dumps(message_data))
            
            # Update client metrics
            if connection_id in self.client_connections:
                client = self.client_connections[connection_id]
                client.messages_sent += 1
                client.last_activity = datetime.utcnow()
            
            return True
            
        except WebSocketDisconnect:
            await self.disconnect(connection_id, "websocket_disconnect")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send message to {connection_id}: {e}")
            return False
    
    async def _send_error(self, connection_id: str, error_code: str, error_message: str):
        """Send an error message to a connection"""
        error_msg = WebSocketMessage(
            type=MessageType.ERROR,
            payload={
                "error_code": error_code,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=1  # Highest priority for errors
        )
        await self._send_message(connection_id, error_msg)
    
    def _check_rate_limit(self, connection_id: str) -> bool:
        """Check if connection is within rate limits"""
        if not self.config.enable_rate_limiting:
            return True
        
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old timestamps
        self.rate_limits[connection_id] = [
            ts for ts in self.rate_limits[connection_id] if ts > minute_ago
        ]
        
        # Check limit
        if len(self.rate_limits[connection_id]) >= self.config.max_messages_per_minute:
            return False
        
        # Add current timestamp
        self.rate_limits[connection_id].append(now)
        return True
    
    async def _process_connection_messages(self, connection_id: str):
        """Process incoming messages from a specific connection"""
        try:
            websocket = self.connections.get(connection_id)
            if not websocket:
                return
            
            while connection_id in self.connections and self.is_monitoring:
                try:
                    # Receive message with timeout
                    message_text = await asyncio.wait_for(
                        websocket.receive_text(), 
                        timeout=self.config.connection_timeout_seconds
                    )
                    
                    # Parse message
                    try:
                        message_data = json.loads(message_text)
                        message = WebSocketMessage(**message_data)
                    except (json.JSONDecodeError, ValueError) as e:
                        await self._send_error(connection_id, "invalid_message", 
                                             f"Failed to parse message: {str(e)}")
                        continue
                    
                    # Handle message
                    await self._handle_message(connection_id, message)
                    
                    # Update client metrics
                    if connection_id in self.client_connections:
                        client = self.client_connections[connection_id]
                        client.messages_received += 1
                        client.last_activity = datetime.utcnow()
                    
                except asyncio.TimeoutError:
                    # Send ping to check if connection is still alive
                    await self._send_ping(connection_id)
                    
                except WebSocketDisconnect:
                    await self.disconnect(connection_id, "websocket_disconnect")
                    break
                    
                except Exception as e:
                    self.logger.error(f"Error processing message from {connection_id}: {e}")
                    await self._send_error(connection_id, "message_processing_error", str(e))
                
        except Exception as e:
            self.logger.error(f"Error in message processor for {connection_id}: {e}")
            await self.disconnect(connection_id, "processor_error")
    
    async def _handle_message(self, connection_id: str, message: WebSocketMessage):
        """Handle incoming message from client"""
        handler = self.message_handlers.get(message.type)
        
        if handler:
            await handler(connection_id, message)
        else:
            await self._send_error(connection_id, "unknown_message_type", 
                                 f"Unknown message type: {message.type}")
    
    async def _handle_ping(self, connection_id: str, message: WebSocketMessage):
        """Handle ping message"""
        pong_message = WebSocketMessage(
            type=MessageType.PONG,
            payload={"timestamp": datetime.utcnow().isoformat()},
            correlation_id=message.id
        )
        await self._send_message(connection_id, pong_message)
        
        # Update last ping time
        if connection_id in self.client_connections:
            self.client_connections[connection_id].last_ping = datetime.utcnow()
    
    async def _handle_subscribe(self, connection_id: str, message: WebSocketMessage):
        """Handle subscription request"""
        try:
            subscription = SubscriptionRequest(**message.payload)
            await self.subscribe(connection_id, subscription)
        except Exception as e:
            await self._send_error(connection_id, "invalid_subscription", str(e))
    
    async def _handle_unsubscribe(self, connection_id: str, message: WebSocketMessage):
        """Handle unsubscribe request"""
        try:
            subscription_type = SubscriptionType(message.payload.get("subscription_type"))
            await self.unsubscribe(connection_id, subscription_type)
        except Exception as e:
            await self._send_error(connection_id, "invalid_unsubscribe", str(e))
    
    async def _handle_connect(self, connection_id: str, message: WebSocketMessage):
        """Handle connect message (additional connection setup)"""
        # Additional connection setup if needed
        pass
    
    async def _handle_disconnect(self, connection_id: str, message: WebSocketMessage):
        """Handle disconnect request from client"""
        await self.disconnect(connection_id, "client_requested")
    
    async def _send_ping(self, connection_id: str):
        """Send ping to connection"""
        ping_message = WebSocketMessage(
            type=MessageType.PING,
            payload={"timestamp": datetime.utcnow().isoformat()}
        )
        await self._send_message(connection_id, ping_message)
    
    async def _process_broadcasts(self):
        """Process broadcast queue and send updates to subscribers"""
        while self.is_monitoring:
            try:
                # Get update from queue
                update = await asyncio.wait_for(self.broadcast_queue.get(), timeout=1.0)
                
                # Determine target connections
                target_connections = set()
                
                # Add subscribers by subscription type
                for sub_type in update.subscription_types:
                    target_connections.update(self.subscriptions[sub_type])
                
                # Add location-based subscribers
                for location in update.target_locations:
                    location_key = f"{location.latitude:.4f},{location.longitude:.4f}"
                    for conn_id, radius in self.location_subscriptions.get(location_key, []):
                        if self._is_within_radius(location, conn_id, radius):
                            target_connections.add(conn_id)
                
                # Add specific user targets
                if update.target_users:
                    for conn_id, client in self.client_connections.items():
                        if client.user_id in update.target_users:
                            target_connections.add(conn_id)
                
                # Send update to target connections
                update_message = WebSocketMessage(
                    type=MessageType.LIVE_UPDATE,
                    payload=update.model_dump()
                )
                
                send_tasks = []
                for conn_id in target_connections:
                    if conn_id in self.connections:
                        task = asyncio.create_task(self._send_message(conn_id, update_message))
                        send_tasks.append(task)
                
                # Execute all sends concurrently
                if send_tasks:
                    await asyncio.gather(*send_tasks, return_exceptions=True)
                
                # Update metrics
                self.metrics.messages_per_minute += len(target_connections)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing broadcast: {e}")
    
    def _is_within_radius(self, location: Location, connection_id: str, radius_km: float) -> bool:
        """Check if location is within radius of connection's subscribed area"""
        # Simplified distance check - in production would use proper geospatial calculations
        if connection_id not in self.client_connections:
            return False
        
        client = self.client_connections[connection_id]
        for subscription in client.active_subscriptions:
            if subscription.location:
                lat_diff = abs(location.latitude - subscription.location.latitude)
                lon_diff = abs(location.longitude - subscription.location.longitude)
                distance_km = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                if distance_km <= radius_km:
                    return True
        
        return False
    
    async def _remove_all_subscriptions(self, connection_id: str):
        """Remove all subscriptions for a connection"""
        if connection_id in self.client_connections:
            client = self.client_connections[connection_id]
            for subscription in client.active_subscriptions:
                self.subscriptions[subscription.subscription_type].discard(connection_id)
            client.active_subscriptions.clear()
            client.subscription_count = 0
        
        # Remove from client subscriptions
        if connection_id in self.client_subscriptions:
            del self.client_subscriptions[connection_id]
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                await self._update_metrics()
                await self._health_check_connections()
                await asyncio.sleep(self.config.metrics_collection_interval_seconds)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_metrics(self):
        """Update system metrics"""
        self.metrics.timestamp = datetime.utcnow()
        self.metrics.active_connections = len(self.connections)
        self.metrics.subscriptions_count = sum(len(subs) for subs in self.subscriptions.values())
        
        # Calculate messages per minute (simplified)
        self.metrics.messages_per_minute = min(100.0, self.metrics.messages_per_minute * 0.9)
    
    async def _health_check_connections(self):
        """Check health of all connections and remove stale ones"""
        now = datetime.utcnow()
        stale_connections = []
        
        for connection_id, client in self.client_connections.items():
            # Check if connection is stale
            time_since_activity = (now - client.last_activity).total_seconds()
            if time_since_activity > self.config.connection_timeout_seconds * 2:
                stale_connections.append(connection_id)
        
        # Remove stale connections
        for connection_id in stale_connections:
            await self.disconnect(connection_id, "stale_connection")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of resources"""
        while self.is_monitoring:
            try:
                await self._cleanup_rate_limits()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_rate_limits(self):
        """Clean up old rate limit records"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        connections_to_clean = []
        
        for connection_id, timestamps in self.rate_limits.items():
            if connection_id not in self.connections:
                connections_to_clean.append(connection_id)
            else:
                # Clean old timestamps
                self.rate_limits[connection_id] = [
                    ts for ts in timestamps if ts > cutoff_time
                ]
        
        # Remove rate limits for disconnected connections
        for connection_id in connections_to_clean:
            del self.rate_limits[connection_id]
    
    async def _close_all_connections(self):
        """Close all active connections"""
        close_tasks = []
        for connection_id in list(self.connections.keys()):
            task = asyncio.create_task(self.disconnect(connection_id, "server_shutdown"))
            close_tasks.append(task)
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        return {
            "total_connections": self.metrics.total_connections,
            "active_connections": self.metrics.active_connections,
            "subscriptions_count": self.metrics.subscriptions_count,
            "subscription_types": {
                sub_type.value: len(connections) 
                for sub_type, connections in self.subscriptions.items()
            },
            "messages_per_minute": self.metrics.messages_per_minute,
            "manager_status": "running" if self.is_monitoring else "stopped"
        }
    
    def get_client_info(self, connection_id: str) -> Optional[ClientConnection]:
        """Get information about a specific client"""
        return self.client_connections.get(connection_id)


# Global WebSocket manager instance
websocket_manager = WebSocketConnectionManager()