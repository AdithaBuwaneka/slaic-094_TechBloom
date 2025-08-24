from typing import Dict, List, Optional, Any, Callable
from app.services.websocket_manager import websocket_manager
from app.agents.agent_manager import agent_manager
from app.models.websocket import (
    LiveUpdate, SubscriptionType, RouteUpdateData, DisruptionAlertData,
    ScheduleChangeData, LocationUpdateData, NotificationData
)
from app.models.transport_data import Location, TransportMode
from app.models.disruption_management import DisruptionAlert
import asyncio
import json
from datetime import datetime, timedelta
import logging
import random


class RealTimeDataStreamer:
    """
    Real-Time Data Streaming Service
    
    Coordinates with agents to provide live updates for schedules, disruptions,
    locations, and other transit information to connected WebSocket clients.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_streaming = False
        self.streaming_tasks: List[asyncio.Task] = []
        
        # Data sources and update intervals
        self.update_intervals = {
            "route_updates": 30,      # Route/vehicle updates every 30 seconds
            "schedule_updates": 60,   # Schedule changes every minute
            "disruption_alerts": 10,  # Disruption monitoring every 10 seconds
            "location_updates": 15,   # Vehicle location updates every 15 seconds
            "system_status": 300,     # System status every 5 minutes
        }
        
        # Last update timestamps for each data type
        self.last_updates: Dict[str, datetime] = {}
        
        # Cached data for comparison
        self.cached_data: Dict[str, Any] = {}
        
        # Streaming configurations
        self.streaming_configs = {
            "enable_route_updates": True,
            "enable_schedule_updates": True,
            "enable_disruption_monitoring": True,
            "enable_location_tracking": True,
            "enable_system_notifications": True,
            "batch_updates": True,
            "max_batch_size": 10
        }
    
    async def start_streaming(self):
        """Start all real-time streaming services"""
        if not self.is_streaming:
            self.is_streaming = True
            
            # Start WebSocket manager if not already running
            await websocket_manager.start()
            
            # Start streaming tasks
            if self.streaming_configs["enable_route_updates"]:
                task = asyncio.create_task(self._stream_route_updates())
                self.streaming_tasks.append(task)
            
            if self.streaming_configs["enable_schedule_updates"]:
                task = asyncio.create_task(self._stream_schedule_updates())
                self.streaming_tasks.append(task)
            
            if self.streaming_configs["enable_disruption_monitoring"]:
                task = asyncio.create_task(self._stream_disruption_alerts())
                self.streaming_tasks.append(task)
            
            if self.streaming_configs["enable_location_tracking"]:
                task = asyncio.create_task(self._stream_location_updates())
                self.streaming_tasks.append(task)
            
            if self.streaming_configs["enable_system_notifications"]:
                task = asyncio.create_task(self._stream_system_notifications())
                self.streaming_tasks.append(task)
            
            # Start data change detection
            detection_task = asyncio.create_task(self._detect_data_changes())
            self.streaming_tasks.append(detection_task)
            
            self.logger.info("Real-time streaming services started")
    
    async def stop_streaming(self):
        """Stop all streaming services"""
        if self.is_streaming:
            self.is_streaming = False
            
            # Cancel all streaming tasks
            for task in self.streaming_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.streaming_tasks:
                await asyncio.gather(*self.streaming_tasks, return_exceptions=True)
            self.streaming_tasks.clear()
            
            self.logger.info("Real-time streaming services stopped")
    
    async def _stream_route_updates(self):
        """Stream live route and vehicle updates"""
        while self.is_streaming:
            try:
                # Generate or fetch route updates
                route_updates = await self._generate_route_updates()
                
                for update in route_updates:
                    # Create live update
                    live_update = LiveUpdate(
                        update_type="route_update",
                        data=update.model_dump(),
                        subscription_types=[SubscriptionType.ROUTE_MONITORING],
                        target_locations=[update.current_location] if update.current_location else [],
                        source="route_tracking_system"
                    )
                    
                    # Broadcast update
                    await websocket_manager.broadcast_update(live_update)
                
                # Wait for next update cycle
                await asyncio.sleep(self.update_intervals["route_updates"])
                
            except Exception as e:
                self.logger.error(f"Error in route updates streaming: {e}")
                await asyncio.sleep(5)
    
    async def _stream_schedule_updates(self):
        """Stream schedule changes and updates"""
        while self.is_streaming:
            try:
                # Check for schedule changes
                schedule_changes = await self._detect_schedule_changes()
                
                for change in schedule_changes:
                    # Create live update
                    live_update = LiveUpdate(
                        update_type="schedule_change",
                        data=change.model_dump(),
                        subscription_types=[SubscriptionType.SCHEDULE_UPDATES],
                        target_routes=[change.route_id],
                        source="schedule_management_system",
                        confidence_level=0.95
                    )
                    
                    # Broadcast update
                    await websocket_manager.broadcast_update(live_update)
                    
                    # Send targeted notification for significant changes
                    if change.change_type in ["cancellation", "major_delay"]:
                        notification = NotificationData(
                            title=f"Schedule Alert - {change.route_id}",
                            message=f"{change.change_type.title()}: {change.reason}",
                            notification_type="alert",
                            target_subscriptions=[SubscriptionType.SCHEDULE_UPDATES]
                        )
                        await websocket_manager.send_notification(notification)
                
                await asyncio.sleep(self.update_intervals["schedule_updates"])
                
            except Exception as e:
                self.logger.error(f"Error in schedule updates streaming: {e}")
                await asyncio.sleep(10)
    
    async def _stream_disruption_alerts(self):
        """Stream disruption alerts and updates"""
        while self.is_streaming:
            try:
                # Check for new or updated disruptions
                disruption_updates = await self._get_disruption_updates()
                
                for disruption_data in disruption_updates:
                    # Determine update type based on disruption status
                    if disruption_data["status"] == "new":
                        update_type = "disruption_alert"
                        message_type = "alert"
                    elif disruption_data["status"] == "updated":
                        update_type = "disruption_update" 
                        message_type = "warning"
                    else:  # resolved
                        update_type = "disruption_resolved"
                        message_type = "info"
                    
                    # Create live update
                    live_update = LiveUpdate(
                        update_type=update_type,
                        data=disruption_data,
                        subscription_types=[SubscriptionType.DISRUPTION_ALERTS],
                        target_locations=[area["location"] for area in disruption_data.get("affected_areas", [])],
                        source="disruption_management_agent",
                        confidence_level=disruption_data.get("confidence_score", 0.8)
                    )
                    
                    # Broadcast update
                    await websocket_manager.broadcast_update(live_update)
                    
                    # Send high-priority notification for critical disruptions
                    if disruption_data.get("severity") in ["high", "critical"]:
                        notification = NotificationData(
                            title=f"Service Alert - {disruption_data.get('title', 'Disruption')}",
                            message=disruption_data.get("description", "Service disruption detected"),
                            notification_type=message_type,
                            target_subscriptions=[SubscriptionType.DISRUPTION_ALERTS],
                            actions=[
                                {"label": "View Details", "action": "view_disruption"},
                                {"label": "Find Alternative", "action": "find_alternative_route"}
                            ]
                        )
                        await websocket_manager.send_notification(notification)
                
                await asyncio.sleep(self.update_intervals["disruption_alerts"])
                
            except Exception as e:
                self.logger.error(f"Error in disruption alerts streaming: {e}")
                await asyncio.sleep(5)
    
    async def _stream_location_updates(self):
        """Stream real-time vehicle location updates"""
        while self.is_streaming:
            try:
                # Generate location updates for active vehicles
                location_updates = await self._generate_location_updates()
                
                for location_update in location_updates:
                    # Create live update
                    live_update = LiveUpdate(
                        update_type="location_update",
                        data=location_update.model_dump(),
                        subscription_types=[SubscriptionType.LOCATION_TRACKING],
                        target_locations=[location_update.current_location],
                        source="vehicle_tracking_system"
                    )
                    
                    # Broadcast update
                    await websocket_manager.broadcast_update(live_update)
                    
                    # Send arrival notifications if approaching stops
                    if location_update.next_stop_eta:
                        time_to_arrival = (location_update.next_stop_eta - datetime.utcnow()).total_seconds() / 60
                        if 2 <= time_to_arrival <= 5:  # 2-5 minutes before arrival
                            notification = NotificationData(
                                title=f"Arrival Alert - {location_update.route_id}",
                                message=f"Arriving at {location_update.next_stop_id} in {int(time_to_arrival)} minutes",
                                notification_type="info",
                                target_subscriptions=[SubscriptionType.LOCATION_TRACKING]
                            )
                            await websocket_manager.send_notification(notification)
                
                await asyncio.sleep(self.update_intervals["location_updates"])
                
            except Exception as e:
                self.logger.error(f"Error in location updates streaming: {e}")
                await asyncio.sleep(5)
    
    async def _stream_system_notifications(self):
        """Stream system-wide notifications and alerts"""
        while self.is_streaming:
            try:
                # Check system status and generate notifications
                system_alerts = await self._check_system_status()
                
                for alert in system_alerts:
                    notification = NotificationData(
                        title=alert["title"],
                        message=alert["message"],
                        notification_type=alert["type"],
                        target_subscriptions=[SubscriptionType.SYSTEM_NOTIFICATIONS]
                    )
                    await websocket_manager.send_notification(notification)
                
                await asyncio.sleep(self.update_intervals["system_status"])
                
            except Exception as e:
                self.logger.error(f"Error in system notifications streaming: {e}")
                await asyncio.sleep(30)
    
    async def _detect_data_changes(self):
        """Detect significant changes in transit data and trigger updates"""
        while self.is_streaming:
            try:
                # Check for significant data changes
                changes = await self._analyze_data_changes()
                
                for change in changes:
                    # Create appropriate live update based on change type
                    live_update = LiveUpdate(
                        update_type=change["type"],
                        data=change["data"],
                        subscription_types=change["subscription_types"],
                        source="data_change_detector",
                        confidence_level=change.get("confidence", 0.7)
                    )
                    
                    await websocket_manager.broadcast_update(live_update)
                
                # Run change detection every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in data change detection: {e}")
                await asyncio.sleep(10)
    
    async def _generate_route_updates(self) -> List[RouteUpdateData]:
        """Generate sample route updates (in production, this would fetch from real systems)"""
        updates = []
        
        # Sample routes for demonstration
        sample_routes = [
            {
                "route_id": "BUS_100", 
                "transport_mode": TransportMode.BUS,
                "locations": [
                    Location(latitude=6.9271, longitude=79.8612, address="Colombo Fort"),
                    Location(latitude=6.8649, longitude=79.8997, address="Mount Lavinia")
                ]
            },
            {
                "route_id": "TRAIN_6007",
                "transport_mode": TransportMode.TRAIN,
                "locations": [
                    Location(latitude=6.9271, longitude=79.8612, address="Colombo Fort"),
                    Location(latitude=7.2906, longitude=80.6337, address="Kandy")
                ]
            }
        ]
        
        for route in sample_routes:
            # Simulate vehicle movement
            current_location = route["locations"][0] if route["locations"] else Location(latitude=6.9271, longitude=79.8612)
            
            # Add some randomness to location
            current_location.latitude += random.uniform(-0.01, 0.01)
            current_location.longitude += random.uniform(-0.01, 0.01)
            
            update = RouteUpdateData(
                route_id=route["route_id"],
                transport_mode=route["transport_mode"],
                current_location=current_location,
                next_stop="Next Stop Station",
                estimated_arrival=datetime.utcnow() + timedelta(minutes=random.randint(5, 30)),
                delay_minutes=random.randint(-2, 15),
                occupancy_level=random.choice(["empty", "moderate", "full"]),
                service_alerts=["On time"] if random.random() > 0.3 else ["Slight delay expected"]
            )
            
            updates.append(update)
        
        return updates
    
    async def _detect_schedule_changes(self) -> List[ScheduleChangeData]:
        """Detect schedule changes (simulated for demonstration)"""
        changes = []
        
        # Simulate occasional schedule changes
        if random.random() < 0.1:  # 10% chance of schedule change
            change = ScheduleChangeData(
                route_id=f"ROUTE_{random.randint(100, 200)}",
                transport_mode=random.choice(list(TransportMode)),
                change_type=random.choice(["delay", "early_departure", "route_change"]),
                original_time=datetime.utcnow() + timedelta(minutes=30),
                new_time=datetime.utcnow() + timedelta(minutes=45),
                reason=random.choice([
                    "Traffic congestion", 
                    "Signal maintenance", 
                    "Weather conditions",
                    "Operational adjustment"
                ]),
                affected_stops=["Stop A", "Stop B", "Stop C"]
            )
            changes.append(change)
        
        return changes
    
    async def _get_disruption_updates(self) -> List[Dict[str, Any]]:
        """Get disruption updates from the disruption management agent"""
        try:
            # Try to get disruptions from the agent
            if "disruption_management_agent" in agent_manager.agents:
                disruption_agent = agent_manager.agents["disruption_management_agent"]
                
                # Get current active disruptions
                result = await disruption_agent.process_request({
                    "request_type": "get_disruptions",
                    "data": {"active_only": True}
                })
                
                if result.get("success") and result.get("data", {}).get("disruptions"):
                    disruptions = result["data"]["disruptions"]
                    
                    # Check for changes since last update
                    last_check = self.last_updates.get("disruptions", datetime.utcnow() - timedelta(minutes=1))
                    updates = []
                    
                    for disruption in disruptions:
                        updated_at = datetime.fromisoformat(disruption["updated_at"])
                        if updated_at > last_check:
                            disruption_data = disruption.copy()
                            disruption_data["status"] = "new" if disruption["created_at"] == disruption["updated_at"] else "updated"
                            updates.append(disruption_data)
                    
                    self.last_updates["disruptions"] = datetime.utcnow()
                    return updates
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting disruption updates: {e}")
            return []
    
    async def _generate_location_updates(self) -> List[LocationUpdateData]:
        """Generate vehicle location updates"""
        updates = []
        
        # Sample vehicles
        vehicles = [
            {"vehicle_id": "BUS_001", "route_id": "ROUTE_100", "mode": TransportMode.BUS},
            {"vehicle_id": "TRAIN_001", "route_id": "TRAIN_6007", "mode": TransportMode.TRAIN}
        ]
        
        for vehicle in vehicles:
            # Simulate movement
            base_lat, base_lon = 6.9271, 79.8612
            current_location = Location(
                latitude=base_lat + random.uniform(-0.05, 0.05),
                longitude=base_lon + random.uniform(-0.05, 0.05),
                address=f"Location for {vehicle['vehicle_id']}"
            )
            
            update = LocationUpdateData(
                vehicle_id=vehicle["vehicle_id"],
                route_id=vehicle["route_id"],
                transport_mode=vehicle["mode"],
                current_location=current_location,
                heading=random.uniform(0, 360),
                speed_kmh=random.uniform(20, 60),
                next_stop_id="NEXT_STOP",
                next_stop_eta=datetime.utcnow() + timedelta(minutes=random.randint(3, 15)),
                passenger_count=random.randint(10, 80)
            )
            
            updates.append(update)
        
        return updates
    
    async def _check_system_status(self) -> List[Dict[str, Any]]:
        """Check system status and generate alerts if needed"""
        alerts = []
        
        # Simulate occasional system alerts
        if random.random() < 0.05:  # 5% chance of system alert
            alert = {
                "title": "System Maintenance",
                "message": "Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM",
                "type": "info"
            }
            alerts.append(alert)
        
        if random.random() < 0.02:  # 2% chance of service alert
            alert = {
                "title": "Service Advisory",
                "message": "Heavy rainfall may cause delays on some bus routes",
                "type": "warning"
            }
            alerts.append(alert)
        
        return alerts
    
    async def _analyze_data_changes(self) -> List[Dict[str, Any]]:
        """Analyze data for significant changes that warrant updates"""
        changes = []
        
        # This would analyze various data sources for changes
        # For demonstration, simulate occasional significant changes
        if random.random() < 0.1:  # 10% chance of significant change
            change = {
                "type": "fare_change",
                "data": {
                    "route_id": "ROUTE_100",
                    "old_fare": 25.0,
                    "new_fare": 30.0,
                    "effective_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    "reason": "Service enhancement and inflation adjustment"
                },
                "subscription_types": [SubscriptionType.FARE_CHANGES],
                "confidence": 1.0
            }
            changes.append(change)
        
        return changes
    
    def configure_streaming(self, config: Dict[str, Any]):
        """Configure streaming parameters"""
        self.streaming_configs.update(config)
        self.logger.info(f"Streaming configuration updated: {config}")
    
    def get_streaming_status(self) -> Dict[str, Any]:
        """Get current streaming status"""
        return {
            "is_streaming": self.is_streaming,
            "active_tasks": len(self.streaming_tasks),
            "update_intervals": self.update_intervals,
            "last_updates": {k: v.isoformat() for k, v in self.last_updates.items()},
            "streaming_configs": self.streaming_configs,
            "websocket_stats": websocket_manager.get_connection_stats()
        }


# Global real-time streamer instance
realtime_streamer = RealTimeDataStreamer()