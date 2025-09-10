# WebSocket Routes for Real-Time Features
# Real-time disruption alerts, location tracking, and live updates

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Set, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.auth_middleware import get_current_user
from app.core.database import db
from app.services.push_notification_service import push_notification_service
import jwt
from app.core.config import settings

router = APIRouter()

class ConnectionManager:
    """
    Manages WebSocket connections for real-time features
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.location_subscribers: Set[str] = set()  # connection_ids subscribed to location updates
        self.disruption_subscribers: Set[str] = set()  # connection_ids subscribed to disruptions
        
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str):
        """Accept WebSocket connection and register user"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        print(f"WebSocket connected: {connection_id} for user {user_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to Transit Companion real-time service",
            "timestamp": datetime.utcnow().isoformat(),
            "connection_id": connection_id
        }, connection_id)
    
    def disconnect(self, connection_id: str, user_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        self.location_subscribers.discard(connection_id)
        self.disruption_subscribers.discard(connection_id)
        
        print(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except:
                # Connection might be broken, remove it
                self.remove_broken_connection(connection_id)
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            broken_connections = []
            for connection_id in self.user_connections[user_id].copy():
                try:
                    await self.send_personal_message(message, connection_id)
                except:
                    broken_connections.append(connection_id)
            
            # Remove broken connections
            for conn_id in broken_connections:
                self.remove_broken_connection(conn_id)
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], subscriber_set: Set[str]):
        """Broadcast message to specific subscribers"""
        broken_connections = []
        for connection_id in subscriber_set.copy():
            try:
                await self.send_personal_message(message, connection_id)
            except:
                broken_connections.append(connection_id)
        
        # Remove broken connections
        for conn_id in broken_connections:
            self.remove_broken_connection(conn_id)
            subscriber_set.discard(conn_id)
    
    def remove_broken_connection(self, connection_id: str):
        """Remove broken connection from all tracking"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Find and remove from user connections
        for user_id, connections in self.user_connections.items():
            if connection_id in connections:
                connections.discard(connection_id)
                if not connections:
                    del self.user_connections[user_id]
                break
        
        self.location_subscribers.discard(connection_id)
        self.disruption_subscribers.discard(connection_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_user_count(self) -> int:
        """Get number of unique connected users"""
        return len(self.user_connections)

# Global connection manager
manager = ConnectionManager()

def verify_websocket_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token for WebSocket authentication
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Main WebSocket endpoint for real-time features
    """
    connection_id = f"ws_{datetime.utcnow().timestamp()}"
    user_id = None
    
    try:
        # Verify authentication token
        payload = verify_websocket_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        # Connect user
        await manager.connect(websocket, connection_id, user_id)
        
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            await handle_websocket_message(websocket, connection_id, user_id, message)
    
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(connection_id, user_id)
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Invalid JSON format",
            "timestamp": datetime.utcnow().isoformat()
        }))
    except Exception as e:
        print(f"WebSocket error: {e}")
        if user_id:
            manager.disconnect(connection_id, user_id)

async def handle_websocket_message(websocket: WebSocket, connection_id: str, user_id: str, message: Dict[str, Any]):
    """
    Handle incoming WebSocket messages from clients
    """
    message_type = message.get("type", "")
    
    if message_type == "subscribe_disruptions":
        # Subscribe to disruption alerts
        manager.disruption_subscribers.add(connection_id)
        await manager.send_personal_message({
            "type": "subscription_confirmed",
            "subscription": "disruptions",
            "message": "Subscribed to real-time disruption alerts",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
    
    elif message_type == "subscribe_location":
        # Subscribe to location-based updates
        manager.location_subscribers.add(connection_id)
        await manager.send_personal_message({
            "type": "subscription_confirmed",
            "subscription": "location",
            "message": "Subscribed to location-based updates",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
    
    elif message_type == "location_update":
        # Handle location update from mobile app
        await handle_location_update(user_id, message.get("data", {}))
    
    elif message_type == "route_start":
        # User started following a route
        await handle_route_start(user_id, message.get("data", {}))
    
    elif message_type == "route_feedback":
        # User provided route feedback
        await handle_route_feedback(user_id, message.get("data", {}))
    
    elif message_type == "ping":
        # Keepalive ping
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)

async def handle_location_update(user_id: str, location_data: Dict[str, Any]):
    """
    Handle real-time location updates from mobile apps
    """
    try:
        # Update user location in database
        location_update = {
            "user_id": user_id,
            "latitude": location_data.get("latitude"),
            "longitude": location_data.get("longitude"),
            "accuracy": location_data.get("accuracy"),
            "timestamp": datetime.utcnow(),
            "speed": location_data.get("speed"),
            "heading": location_data.get("heading")
        }
        
        await db.database.user_locations.update_one(
            {"user_id": user_id},
            {"$set": location_update},
            upsert=True
        )
        
        # Check for nearby disruptions
        await check_nearby_disruptions(user_id, location_data)
        
    except Exception as e:
        print(f"Error handling location update: {e}")

async def handle_route_start(user_id: str, route_data: Dict[str, Any]):
    """
    Handle when user starts following a route
    """
    try:
        # Store active route
        active_route = {
            "user_id": user_id,
            "route_id": route_data.get("route_id"),
            "source": route_data.get("source"),
            "destination": route_data.get("destination"),
            "mode": route_data.get("mode"),
            "started_at": datetime.utcnow(),
            "status": "active"
        }
        
        await db.database.active_routes.update_one(
            {"user_id": user_id},
            {"$set": active_route},
            upsert=True
        )
        
        # Send confirmation
        await manager.send_to_user({
            "type": "route_tracking_started",
            "message": "Route tracking activated",
            "route_id": route_data.get("route_id"),
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)
        
    except Exception as e:
        print(f"Error handling route start: {e}")

async def handle_route_feedback(user_id: str, feedback_data: Dict[str, Any]):
    """
    Handle real-time route feedback from users
    """
    try:
        # Store feedback
        feedback = {
            "user_id": user_id,
            "route_id": feedback_data.get("route_id"),
            "feedback_type": feedback_data.get("type"),  # delay, disruption, quality
            "rating": feedback_data.get("rating"),
            "comment": feedback_data.get("comment"),
            "location": feedback_data.get("location"),
            "timestamp": datetime.utcnow()
        }
        
        await db.database.route_feedback.insert_one(feedback)
        
        # If it's a disruption report, notify other users
        if feedback_data.get("type") == "disruption":
            await broadcast_disruption_alert(feedback_data)
        
    except Exception as e:
        print(f"Error handling route feedback: {e}")

async def check_nearby_disruptions(user_id: str, location_data: Dict[str, Any]):
    """
    Check for disruptions near user's current location
    """
    try:
        # Get active disruptions (simplified - in real app, use geospatial queries)
        disruptions = await db.database.transit_disruptions.find({
            "status": "active"
        }).to_list(length=None)
        
        # Send relevant disruptions to user
        relevant_disruptions = []
        for disruption in disruptions:
            # Simplified proximity check - in real app, use proper geospatial calculations
            relevant_disruptions.append(disruption)
        
        if relevant_disruptions:
            await manager.send_to_user({
                "type": "nearby_disruptions",
                "disruptions": relevant_disruptions,
                "timestamp": datetime.utcnow().isoformat()
            }, user_id)
        
    except Exception as e:
        print(f"Error checking nearby disruptions: {e}")

async def broadcast_disruption_alert(disruption_data: Dict[str, Any]):
    """
    Broadcast disruption alert to all subscribed users
    """
    try:
        alert_message = {
            "type": "disruption_alert",
            "disruption": {
                "location": disruption_data.get("location"),
                "type": disruption_data.get("disruption_type", "unknown"),
                "severity": disruption_data.get("severity", "medium"),
                "description": disruption_data.get("comment", ""),
                "reported_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.broadcast_to_subscribers(alert_message, manager.disruption_subscribers)
        
    except Exception as e:
        print(f"Error broadcasting disruption alert: {e}")

@router.get("/realtime/stats")
async def get_realtime_stats():
    """
    Get real-time WebSocket connection statistics
    """
    return {
        "active_connections": manager.get_connection_count(),
        "connected_users": manager.get_user_count(),
        "disruption_subscribers": len(manager.disruption_subscribers),
        "location_subscribers": len(manager.location_subscribers),
        "timestamp": datetime.utcnow().isoformat()
    }

# Background task to send periodic updates
async def send_periodic_updates():
    """
    Send periodic updates to connected clients
    """
    while True:
        try:
            # Send system status to all connections
            if manager.active_connections:
                status_message = {
                    "type": "system_status",
                    "status": "operational",
                    "connected_users": manager.get_user_count(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                for connection_id in list(manager.active_connections.keys()):
                    await manager.send_personal_message(status_message, connection_id)
            
            # Wait 5 minutes before next update
            await asyncio.sleep(300)
            
        except Exception as e:
            print(f"Error in periodic updates: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# Start background task (this would be called in main.py)
# asyncio.create_task(send_periodic_updates())