# Push Notification Service for Mobile Apps
# Supports Expo Push Notifications and FCM

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from exponent_server_sdk import PushClient, PushMessage, PushServerError, PushTicketError
from app.core.database import db
from app.core.config import settings
import uuid

class PushNotificationService:
    """
    Handles push notifications for mobile apps using Expo Push Notifications
    """
    
    def __init__(self):
        self.push_client = PushClient()
        
    async def register_device(self, user_id: str, device_token: str, platform: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a device for push notifications
        """
        try:
            # Check if device already exists
            existing_device = await db.database.device_tokens.find_one({
                "user_id": user_id,
                "device_token": device_token
            })
            
            if existing_device:
                # Update existing device
                update_result = await db.database.device_tokens.update_one(
                    {"_id": existing_device["_id"]},
                    {
                        "$set": {
                            "platform": platform,
                            "device_info": device_info or {},
                            "last_updated": datetime.utcnow(),
                            "is_active": True
                        }
                    }
                )
                return {
                    "status": "success",
                    "message": "Device updated successfully",
                    "device_id": str(existing_device["_id"])
                }
            else:
                # Create new device registration
                device_data = {
                    "device_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "device_token": device_token,
                    "platform": platform,  # "ios", "android"
                    "device_info": device_info or {},
                    "registered_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow(),
                    "is_active": True,
                    "notification_count": 0,
                    "last_notification_sent": None
                }
                
                result = await db.database.device_tokens.insert_one(device_data)
                
                return {
                    "status": "success",
                    "message": "Device registered successfully",
                    "device_id": device_data["device_id"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Device registration failed: {str(e)}"
            }
    
    async def unregister_device(self, user_id: str, device_token: str) -> Dict[str, Any]:
        """
        Unregister a device from push notifications
        """
        try:
            result = await db.database.device_tokens.update_one(
                {"user_id": user_id, "device_token": device_token},
                {"$set": {"is_active": False, "unregistered_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {
                    "status": "success",
                    "message": "Device unregistered successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Device not found"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Device unregistration failed: {str(e)}"
            }
    
    async def send_notification(self, user_id: str, title: str, body: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send push notification to a specific user
        """
        try:
            # Get active devices for user
            devices = await db.database.device_tokens.find({
                "user_id": user_id,
                "is_active": True
            }).to_list(length=None)
            
            if not devices:
                return {
                    "status": "error",
                    "message": "No active devices found for user"
                }
            
            # Send to all user devices
            messages = []
            for device in devices:
                message = PushMessage(
                    to=device["device_token"],
                    title=title,
                    body=body,
                    data=data or {},
                    sound="default",
                    badge=1
                )
                messages.append(message)
            
            # Send notifications
            tickets = self.push_client.publish_multiple(messages)
            
            # Store notification in database
            notification_data = {
                "notification_id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title,
                "body": body,
                "data": data or {},
                "sent_at": datetime.utcnow(),
                "device_count": len(devices),
                "tickets": [ticket.to_dict() if hasattr(ticket, 'to_dict') else str(ticket) for ticket in tickets],
                "status": "sent"
            }
            
            await db.database.notifications.insert_one(notification_data)
            
            # Update device notification counts
            for device in devices:
                await db.database.device_tokens.update_one(
                    {"_id": device["_id"]},
                    {
                        "$inc": {"notification_count": 1},
                        "$set": {"last_notification_sent": datetime.utcnow()}
                    }
                )
            
            return {
                "status": "success",
                "message": f"Notification sent to {len(devices)} devices",
                "notification_id": notification_data["notification_id"],
                "device_count": len(devices)
            }
            
        except PushServerError as e:
            return {
                "status": "error",
                "message": f"Push server error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Notification send failed: {str(e)}"
            }
    
    async def send_bulk_notification(self, user_ids: List[str], title: str, body: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send push notification to multiple users
        """
        try:
            # Get all active devices for users
            devices = await db.database.device_tokens.find({
                "user_id": {"$in": user_ids},
                "is_active": True
            }).to_list(length=None)
            
            if not devices:
                return {
                    "status": "error",
                    "message": "No active devices found for users"
                }
            
            # Create messages for all devices
            messages = []
            for device in devices:
                message = PushMessage(
                    to=device["device_token"],
                    title=title,
                    body=body,
                    data=data or {},
                    sound="default",
                    badge=1
                )
                messages.append(message)
            
            # Send notifications in batches (Expo limit is 100 per batch)
            batch_size = 100
            all_tickets = []
            
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                tickets = self.push_client.publish_multiple(batch)
                all_tickets.extend(tickets)
            
            # Store bulk notification record
            notification_data = {
                "notification_id": str(uuid.uuid4()),
                "type": "bulk",
                "user_ids": user_ids,
                "title": title,
                "body": body,
                "data": data or {},
                "sent_at": datetime.utcnow(),
                "device_count": len(devices),
                "user_count": len(user_ids),
                "status": "sent"
            }
            
            await db.database.notifications.insert_one(notification_data)
            
            return {
                "status": "success",
                "message": f"Bulk notification sent to {len(devices)} devices for {len(user_ids)} users",
                "notification_id": notification_data["notification_id"],
                "device_count": len(devices),
                "user_count": len(user_ids)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Bulk notification failed: {str(e)}"
            }
    
    async def send_route_disruption_alert(self, affected_user_ids: List[str], disruption_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send route disruption alerts to affected users
        """
        title = f"Route Disruption Alert"
        body = f"Disruption on {disruption_info.get('location', 'your route')}: {disruption_info.get('description', 'Check for updates')}"
        
        data = {
            "type": "route_disruption",
            "disruption_id": disruption_info.get("disruption_id"),
            "location": disruption_info.get("location"),
            "severity": disruption_info.get("severity"),
            "affected_routes": disruption_info.get("affected_routes", [])
        }
        
        return await self.send_bulk_notification(affected_user_ids, title, body, data)
    
    async def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get notification history for a user
        """
        try:
            notifications = await db.database.notifications.find({
                "$or": [
                    {"user_id": user_id},
                    {"user_ids": user_id}
                ]
            }).sort("sent_at", -1).limit(limit).to_list(length=None)
            
            # Clean up the response
            for notification in notifications:
                notification["_id"] = str(notification["_id"])
            
            return notifications
            
        except Exception as e:
            print(f"Error getting user notifications: {str(e)}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """
        Mark a notification as read
        """
        try:
            result = await db.database.notifications.update_one(
                {"notification_id": notification_id},
                {"$addToSet": {"read_by": user_id}}
            )
            
            if result.modified_count > 0:
                return {"status": "success", "message": "Notification marked as read"}
            else:
                return {"status": "error", "message": "Notification not found"}
                
        except Exception as e:
            return {"status": "error", "message": f"Failed to mark notification as read: {str(e)}"}

# Initialize global push notification service
push_notification_service = PushNotificationService()