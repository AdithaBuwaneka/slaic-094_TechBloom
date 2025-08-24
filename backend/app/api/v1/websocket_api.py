from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse
from app.services.websocket_manager import websocket_manager
from app.services.realtime_streamer import realtime_streamer
from app.models.websocket import (
    SubscriptionRequest, SubscriptionType, NotificationData,
    WebSocketConfig, StreamingQuery
)
from app.models.transport_data import Location
from typing import Optional, Dict, Any
import json
from datetime import datetime

router = APIRouter()


@router.websocket("/live")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None),
    client_type: Optional[str] = Query("web"),
    app_version: Optional[str] = Query("1.0.0")
):
    """
    Main WebSocket endpoint for real-time transit updates
    
    Supports:
    - Route monitoring
    - Disruption alerts  
    - Schedule updates
    - Location tracking
    - System notifications
    """
    connection_id = None
    
    try:
        # Prepare connection metadata
        metadata = {
            "user_agent": websocket.headers.get("user-agent", "unknown"),
            "platform": client_type,
            "app_version": app_version,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        # Connect client
        connection_id = await websocket_manager.connect(
            websocket=websocket,
            user_id=user_id,
            metadata=metadata
        )
        
        # Start streaming services if not already running
        if not realtime_streamer.is_streaming:
            await realtime_streamer.start_streaming()
        
        # Keep connection alive and handle disconnection
        try:
            while True:
                # This will block until the client disconnects
                await websocket.receive_text()
                
        except WebSocketDisconnect:
            pass  # Normal disconnection
            
    except WebSocketDisconnect:
        pass  # Connection closed by client
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up connection
        if connection_id:
            await websocket_manager.disconnect(connection_id, "websocket_closed")


@router.websocket("/route-monitoring/{route_id}")
async def route_monitoring_websocket(
    websocket: WebSocket,
    route_id: str,
    user_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint specifically for monitoring a single route
    """
    connection_id = None
    
    try:
        # Connect client
        connection_id = await websocket_manager.connect(websocket, user_id=user_id)
        
        # Auto-subscribe to route monitoring for this specific route
        subscription = SubscriptionRequest(
            subscription_type=SubscriptionType.ROUTE_MONITORING,
            filters={"route_id": route_id},
            route_ids=[route_id],
            update_interval_seconds=15  # More frequent updates for route monitoring
        )
        
        await websocket_manager.subscribe(connection_id, subscription)
        
        # Also subscribe to disruption alerts for this route
        disruption_subscription = SubscriptionRequest(
            subscription_type=SubscriptionType.DISRUPTION_ALERTS,
            filters={"route_id": route_id}
        )
        
        await websocket_manager.subscribe(connection_id, disruption_subscription)
        
        # Keep connection alive
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
            
    except Exception as e:
        print(f"Route monitoring WebSocket error: {e}")
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id, "route_monitoring_closed")


@router.websocket("/location-tracking")
async def location_tracking_websocket(
    websocket: WebSocket,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, le=50),
    user_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for location-based tracking
    """
    connection_id = None
    
    try:
        # Connect client
        connection_id = await websocket_manager.connect(websocket, user_id=user_id)
        
        # Create location-based subscription
        location = Location(latitude=lat, longitude=lon)
        subscription = SubscriptionRequest(
            subscription_type=SubscriptionType.LOCATION_TRACKING,
            location=location,
            radius_km=radius_km,
            update_interval_seconds=20
        )
        
        await websocket_manager.subscribe(connection_id, subscription)
        
        # Also subscribe to disruption alerts in the area
        disruption_subscription = SubscriptionRequest(
            subscription_type=SubscriptionType.DISRUPTION_ALERTS,
            location=location,
            radius_km=radius_km
        )
        
        await websocket_manager.subscribe(connection_id, disruption_subscription)
        
        # Keep connection alive
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
            
    except Exception as e:
        print(f"Location tracking WebSocket error: {e}")
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id, "location_tracking_closed")


@router.get("/connections/status")
async def get_connection_status():
    """Get current WebSocket connection statistics"""
    try:
        stats = websocket_manager.get_connection_stats()
        streaming_status = realtime_streamer.get_streaming_status()
        
        return {
            "status": "success",
            "message": "Connection status retrieved",
            "websocket_stats": stats,
            "streaming_status": streaming_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connection status: {str(e)}")


@router.post("/broadcast-notification")
async def broadcast_notification(notification: NotificationData):
    """Broadcast a notification to all relevant subscribers"""
    try:
        await websocket_manager.send_notification(notification)
        
        return {
            "status": "success",
            "message": "Notification broadcast successfully",
            "notification_id": notification.notification_id,
            "target_subscriptions": [sub.value for sub in notification.target_subscriptions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to broadcast notification: {str(e)}")


@router.post("/trigger-test-update/{update_type}")
async def trigger_test_update(update_type: str):
    """Trigger a test update for demonstration purposes"""
    try:
        from app.models.websocket import LiveUpdate
        
        # Generate test data based on update type
        if update_type == "disruption":
            test_data = {
                "id": "TEST_DISRUPTION",
                "title": "Test Service Disruption",
                "description": "This is a test disruption alert for demonstration purposes",
                "severity": "medium",
                "affected_routes": ["ROUTE_100", "ROUTE_101"],
                "estimated_resolution": (datetime.utcnow()).isoformat()
            }
            subscription_types = [SubscriptionType.DISRUPTION_ALERTS]
            
        elif update_type == "schedule":
            test_data = {
                "route_id": "ROUTE_TEST",
                "change_type": "delay",
                "original_time": datetime.utcnow().isoformat(),
                "new_time": (datetime.utcnow()).isoformat(),
                "delay_minutes": 10,
                "reason": "Test delay notification"
            }
            subscription_types = [SubscriptionType.SCHEDULE_UPDATES]
            
        elif update_type == "location":
            test_data = {
                "vehicle_id": "TEST_VEHICLE",
                "route_id": "ROUTE_TEST",
                "current_location": {
                    "latitude": 6.9271,
                    "longitude": 79.8612,
                    "address": "Test Location"
                },
                "next_stop": "Test Stop",
                "eta_minutes": 5
            }
            subscription_types = [SubscriptionType.LOCATION_TRACKING]
            
        else:
            test_data = {
                "message": f"Test update of type: {update_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
            subscription_types = [SubscriptionType.ALL_UPDATES]
        
        # Create and broadcast live update
        live_update = LiveUpdate(
            update_type=f"test_{update_type}",
            data=test_data,
            subscription_types=subscription_types,
            source="test_trigger",
            confidence_level=1.0
        )
        
        await websocket_manager.broadcast_update(live_update)
        
        # Also send as notification
        notification = NotificationData(
            title=f"Test {update_type.title()} Update",
            message=f"This is a test {update_type} notification",
            notification_type="info",
            target_subscriptions=subscription_types
        )
        
        await websocket_manager.send_notification(notification)
        
        return {
            "status": "success",
            "message": f"Test {update_type} update triggered successfully",
            "update_id": live_update.update_id,
            "data": test_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger test update: {str(e)}")


@router.post("/streaming/start")
async def start_streaming():
    """Start real-time streaming services"""
    try:
        if not realtime_streamer.is_streaming:
            await realtime_streamer.start_streaming()
            message = "Real-time streaming services started"
        else:
            message = "Real-time streaming services already running"
        
        return {
            "status": "success",
            "message": message,
            "streaming_status": realtime_streamer.get_streaming_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming: {str(e)}")


@router.post("/streaming/stop")
async def stop_streaming():
    """Stop real-time streaming services"""
    try:
        if realtime_streamer.is_streaming:
            await realtime_streamer.stop_streaming()
            message = "Real-time streaming services stopped"
        else:
            message = "Real-time streaming services already stopped"
        
        return {
            "status": "success",
            "message": message,
            "streaming_status": realtime_streamer.get_streaming_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop streaming: {str(e)}")


@router.post("/streaming/configure")
async def configure_streaming(config: Dict[str, Any]):
    """Configure real-time streaming parameters"""
    try:
        realtime_streamer.configure_streaming(config)
        
        return {
            "status": "success",
            "message": "Streaming configuration updated",
            "new_config": config,
            "streaming_status": realtime_streamer.get_streaming_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure streaming: {str(e)}")


@router.get("/subscriptions/types")
async def get_subscription_types():
    """Get available subscription types and their descriptions"""
    subscription_info = {
        SubscriptionType.ROUTE_MONITORING: {
            "name": "Route Monitoring",
            "description": "Real-time updates for specific routes including delays, arrivals, and service changes",
            "filters": ["route_id", "transport_mode"],
            "update_frequency": "15-30 seconds"
        },
        SubscriptionType.DISRUPTION_ALERTS: {
            "name": "Disruption Alerts", 
            "description": "Service disruptions, delays, cancellations, and emergency notifications",
            "filters": ["severity", "location", "transport_mode"],
            "update_frequency": "Real-time"
        },
        SubscriptionType.SCHEDULE_UPDATES: {
            "name": "Schedule Updates",
            "description": "Changes to published schedules, timetable modifications, and service adjustments", 
            "filters": ["route_id", "time_range"],
            "update_frequency": "As changes occur"
        },
        SubscriptionType.LOCATION_TRACKING: {
            "name": "Location Tracking",
            "description": "Real-time vehicle positions, arrival predictions, and location-based services",
            "filters": ["location", "radius_km", "vehicle_id"],
            "update_frequency": "15-20 seconds"
        },
        SubscriptionType.FARE_CHANGES: {
            "name": "Fare Changes",
            "description": "Fare updates, pricing changes, and discount notifications",
            "filters": ["route_id", "fare_type"],
            "update_frequency": "As changes occur"
        },
        SubscriptionType.SYSTEM_NOTIFICATIONS: {
            "name": "System Notifications",
            "description": "General system alerts, maintenance notifications, and service advisories",
            "filters": ["priority", "category"],
            "update_frequency": "As needed"
        }
    }
    
    return {
        "status": "success",
        "message": "Subscription types retrieved",
        "subscription_types": {
            sub_type.value: info for sub_type, info in subscription_info.items()
        },
        "total_types": len(subscription_info)
    }


@router.get("/demo-client")
async def get_demo_client():
    """Return a simple HTML demo client for testing WebSocket connections"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Transit Companion WebSocket Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        #messages { height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; background: #f9f9f9; }
        .message { margin: 5px 0; padding: 5px; background: white; border-radius: 3px; }
        .message.error { background: #ffe6e6; }
        .message.update { background: #e6f3ff; }
        button { margin: 5px; padding: 8px 16px; }
        input, select { margin: 5px; padding: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Transit Companion WebSocket Demo</h1>
        
        <div class="section">
            <h3>Connection</h3>
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
            <span id="status">Disconnected</span>
        </div>
        
        <div class="section">
            <h3>Subscriptions</h3>
            <select id="subscriptionType">
                <option value="route_monitoring">Route Monitoring</option>
                <option value="disruption_alerts">Disruption Alerts</option>
                <option value="schedule_updates">Schedule Updates</option>
                <option value="location_tracking">Location Tracking</option>
                <option value="system_notifications">System Notifications</option>
            </select>
            <button onclick="subscribe()">Subscribe</button>
            <button onclick="unsubscribe()">Unsubscribe</button>
        </div>
        
        <div class="section">
            <h3>Test Updates</h3>
            <button onclick="triggerTest('disruption')">Test Disruption</button>
            <button onclick="triggerTest('schedule')">Test Schedule</button>
            <button onclick="triggerTest('location')">Test Location</button>
        </div>
        
        <div class="section">
            <h3>Messages</h3>
            <div id="messages"></div>
            <button onclick="clearMessages()">Clear Messages</button>
        </div>
    </div>

    <script>
        let ws = null;
        const messagesDiv = document.getElementById('messages');
        const statusSpan = document.getElementById('status');
        
        function addMessage(message, type = 'info') {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong>: ${JSON.stringify(message, null, 2)}`;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function connect() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                addMessage('Already connected', 'error');
                return;
            }
            
            const wsUrl = `ws://localhost:8005/api/v1/websocket/live?user_id=demo_user&client_type=web`;
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                statusSpan.textContent = 'Connected';
                statusSpan.style.color = 'green';
                addMessage('Connected to WebSocket');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data, data.type === 'error' ? 'error' : 'update');
            };
            
            ws.onclose = function(event) {
                statusSpan.textContent = 'Disconnected';
                statusSpan.style.color = 'red';
                addMessage('Disconnected from WebSocket');
            };
            
            ws.onerror = function(error) {
                addMessage('WebSocket error: ' + error, 'error');
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
            }
        }
        
        function subscribe() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                addMessage('Not connected', 'error');
                return;
            }
            
            const subscriptionType = document.getElementById('subscriptionType').value;
            const message = {
                type: 'subscribe',
                payload: {
                    subscription_type: subscriptionType,
                    update_interval_seconds: 30
                }
            };
            
            ws.send(JSON.stringify(message));
            addMessage(`Subscribing to ${subscriptionType}`);
        }
        
        function unsubscribe() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                addMessage('Not connected', 'error');
                return;
            }
            
            const subscriptionType = document.getElementById('subscriptionType').value;
            const message = {
                type: 'unsubscribe',
                payload: {
                    subscription_type: subscriptionType
                }
            };
            
            ws.send(JSON.stringify(message));
            addMessage(`Unsubscribing from ${subscriptionType}`);
        }
        
        function triggerTest(updateType) {
            fetch(`/api/v1/websocket/trigger-test-update/${updateType}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                addMessage(`Triggered test ${updateType} update`);
            })
            .catch(error => {
                addMessage(`Error triggering test: ${error}`, 'error');
            });
        }
        
        function clearMessages() {
            messagesDiv.innerHTML = '';
        }
        
        // Auto-connect on page load
        // connect();
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)