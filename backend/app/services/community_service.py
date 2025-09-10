# Community Data Service for SLAIC 2025
# Handles crowdsourced transit data from Sri Lankan commuters

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import random
from app.core.database import db

class CommunityDataService:
    """
    Community Data Service for crowdsourced transit information
    Handles user-contributed data for traffic, delays, fares, and accessibility
    """
    
    def __init__(self):
        self.available = True
        print("Community Data Service initialized with database integration")
    
    async def submit_traffic_report(self, location: str, severity: str, description: str = None, coordinates: Dict = None, user_id: str = None) -> Dict[str, Any]:
        """Submit a traffic condition report to database"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "traffic",
                "location": location,
                "severity": severity,
                "description": description or f"{severity.title()} traffic reported at {location}",
                "coordinates": coordinates,
                "user_id": user_id,
                "reported_at": datetime.utcnow(),
                "status": "active",
                "votes": 1,  # Start with 1 vote (from reporter)
                "reliability_score": 0.8,
                "verified": False
            }
            
            # Save to database
            result = await db.database.community_reports.insert_one(report)
            report["_id"] = str(result.inserted_id)
            
            return {
                "status": "success",
                "message": "Traffic report submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def submit_delay_report(self, route: str, mode: str, delay_minutes: int, location: str, description: str = None, user_id: str = None) -> Dict[str, Any]:
        """Submit a transit delay report to database"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "delay",
                "route": route,
                "mode": mode,
                "delay_minutes": delay_minutes,
                "location": location,
                "description": description or f"{delay_minutes}-minute delay on {route} ({mode})",
                "user_id": user_id,
                "reported_at": datetime.utcnow(),
                "status": "active",
                "votes": 1,
                "reliability_score": 0.8,
                "verified": False,
                "estimated_clearance": (datetime.utcnow() + timedelta(minutes=delay_minutes * 2)).isoformat()
            }
            
            # Save to database
            result = await db.database.community_reports.insert_one(report)
            report["_id"] = str(result.inserted_id)
            
            return {
                "status": "success", 
                "message": "Delay report submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def submit_fare_update(self, route: str, mode: str, fare_amount: float, effective_date: str = None, source: str = "community", user_id: str = None) -> Dict[str, Any]:
        """Submit a fare update report to database"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "fare_update",
                "route": route,
                "mode": mode,
                "fare_amount": fare_amount,
                "currency": "LKR",
                "effective_date": effective_date or datetime.utcnow().date().isoformat(),
                "source": source,
                "user_id": user_id,
                "reported_at": datetime.utcnow(),
                "status": "pending_verification",
                "votes": 1,
                "reliability_score": 0.8,
                "verified": False,
                "previous_fare": None  # Can be updated later with actual data
            }
            
            # Save to database
            result = await db.database.community_reports.insert_one(report)
            report["_id"] = str(result.inserted_id)
            
            return {
                "status": "success",
                "message": "Fare update submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def submit_accessibility_report(self, location: str, facility_type: str, status: str, description: str = None, user_id: str = None) -> Dict[str, Any]:
        """Submit an accessibility status report to database"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "accessibility",
                "location": location,
                "facility_type": facility_type,
                "status": status,
                "description": description or f"{facility_type.replace('_', ' ').title()} is {status} at {location}",
                "user_id": user_id,
                "reported_at": datetime.utcnow(),
                "priority": "high" if status in ["unavailable", "needs_repair"] else "medium",
                "votes": 1,
                "reliability_score": 0.8,
                "verified": False,
                "impact_level": "medium"  # Default to medium, can be updated later
            }
            
            # Save to database
            result = await db.database.community_reports.insert_one(report)
            report["_id"] = str(result.inserted_id)
            
            return {
                "status": "success",
                "message": "Accessibility report submitted successfully", 
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def submit_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit any type of community report to database"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": report_data.get("type"),
                "title": report_data.get("title"),
                "description": report_data.get("description"),
                "location": report_data.get("location"),
                "severity": report_data.get("severity"),
                "user_id": report_data.get("user_id"),
                "reported_at": datetime.utcnow(),
                "status": "active",
                "votes": 1,  # Start with 1 vote (from reporter)
                "reliability_score": 0.8,
                "verified": False
            }
            
            # Save to database
            result = await db.database.community_reports.insert_one(report)
            report["_id"] = str(result.inserted_id)
            
            return {
                "status": "success",
                "message": "Report submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_recent_reports(self, report_type: str = None, location: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get recent community reports from database with optional filtering"""
        try:
            # Build filter query
            filter_query = {}
            if report_type:
                filter_query["type"] = report_type
            if location:
                filter_query["location"] = {"$regex": location, "$options": "i"}
            
            # Query database
            cursor = db.database.community_reports.find(filter_query).sort("reported_at", -1).limit(limit)
            reports = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for report in reports:
                if "_id" in report:
                    report["_id"] = str(report["_id"])
                # Convert datetime to ISO string for frontend
                if "reported_at" in report and isinstance(report["reported_at"], datetime):
                    report["reported_at"] = report["reported_at"].isoformat()
            
            total_count = await db.database.community_reports.count_documents(filter_query)
            
            return {
                "status": "success",
                "data": {
                    "reports": reports,
                    "total_count": total_count,
                    "returned_count": len(reports),
                    "filters_applied": {
                        "report_type": report_type,
                        "location": location,
                        "limit": limit
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_community_stats(self) -> Dict[str, Any]:
        """Get community contribution statistics from database"""
        try:
            # Get total reports from database
            total_reports = await db.database.community_reports.count_documents({})
            
            # Get reports by type
            pipeline = [
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]
            reports_by_type_cursor = db.database.community_reports.aggregate(pipeline)
            reports_by_type_data = await reports_by_type_cursor.to_list(length=None)
            
            reports_by_type = {}
            for item in reports_by_type_data:
                reports_by_type[item["_id"]] = item["count"]
            
            # Get reports today
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            reports_today = await db.database.community_reports.count_documents(
                {"reported_at": {"$gte": today}}
            )
            
            # Get reports this week
            week_ago = datetime.utcnow() - timedelta(days=7)
            reports_this_week = await db.database.community_reports.count_documents(
                {"reported_at": {"$gte": week_ago}}
            )
            
            # Get top locations
            location_pipeline = [
                {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 4}
            ]
            top_locations_cursor = db.database.community_reports.aggregate(location_pipeline)
            top_locations_data = await top_locations_cursor.to_list(length=4)
            
            top_locations = [
                {"location": item["_id"], "report_count": item["count"]}
                for item in top_locations_data
            ]
            
            stats = {
                "total_reports": total_reports,
                "reports_by_type": reports_by_type,
                "active_contributors": len(set()),  # Could be enhanced to track unique user_ids
                "reports_today": reports_today,
                "reports_this_week": reports_this_week,
                "top_locations": top_locations,
                "average_response_time": "5 minutes",  # Could be calculated from data
                "reliability_score": 0.90,  # Could be calculated from verified reports
                "community_engagement": "High" if reports_today > 10 else "Medium"
            }
            
            return {
                "status": "success",
                "data": stats,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "Community Data Analytics"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    

# Initialize global service instance
community_service = CommunityDataService()