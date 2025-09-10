# Community Data Service for SLAIC 2025
# Handles crowdsourced transit data from Sri Lankan commuters

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import random

class CommunityDataService:
    """
    Community Data Service for crowdsourced transit information
    Handles user-contributed data for traffic, delays, fares, and accessibility
    """
    
    def __init__(self):
        self.available = True
        self.reports_storage = {
            "traffic": [],
            "delays": [],
            "fares": [],
            "accessibility": []
        }
        self.stats = {
            "total_reports": 0,
            "active_contributors": 0,
            "reports_today": 0
        }
        print("Community Data Service initialized")
    
    def submit_traffic_report(self, location: str, severity: str, description: str = None, coordinates: Dict = None) -> Dict[str, Any]:
        """Submit a traffic condition report"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "traffic",
                "location": location,
                "severity": severity,
                "description": description or f"{severity.title()} traffic reported at {location}",
                "coordinates": coordinates,
                "timestamp": datetime.now().isoformat(),
                "status": "active",
                "votes": random.randint(1, 15),  # Mock community votes
                "reliability_score": random.uniform(0.7, 0.95)
            }
            
            self.reports_storage["traffic"].append(report)
            self._update_stats()
            
            return {
                "status": "success",
                "message": "Traffic report submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def submit_delay_report(self, route: str, mode: str, delay_minutes: int, location: str, description: str = None) -> Dict[str, Any]:
        """Submit a transit delay report"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "delay",
                "route": route,
                "mode": mode,
                "delay_minutes": delay_minutes,
                "location": location,
                "description": description or f"{delay_minutes}-minute delay on {route} ({mode})",
                "timestamp": datetime.now().isoformat(),
                "status": "active",
                "votes": random.randint(1, 20),
                "reliability_score": random.uniform(0.8, 0.98),
                "estimated_clearance": (datetime.now() + timedelta(minutes=delay_minutes * 2)).isoformat()
            }
            
            self.reports_storage["delays"].append(report)
            self._update_stats()
            
            return {
                "status": "success", 
                "message": "Delay report submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def submit_fare_update(self, route: str, mode: str, fare_amount: float, effective_date: str = None, source: str = "community") -> Dict[str, Any]:
        """Submit a fare update report"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "fare_update",
                "route": route,
                "mode": mode,
                "fare_amount": fare_amount,
                "currency": "LKR",
                "effective_date": effective_date or datetime.now().date().isoformat(),
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "status": "pending_verification",
                "votes": random.randint(1, 12),
                "reliability_score": random.uniform(0.75, 0.92),
                "previous_fare": fare_amount - random.uniform(10, 50)  # Mock previous fare
            }
            
            self.reports_storage["fares"].append(report)
            self._update_stats()
            
            return {
                "status": "success",
                "message": "Fare update submitted successfully",
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def submit_accessibility_report(self, location: str, facility_type: str, status: str, description: str = None) -> Dict[str, Any]:
        """Submit an accessibility status report"""
        try:
            report = {
                "report_id": str(uuid.uuid4())[:8],
                "type": "accessibility",
                "location": location,
                "facility_type": facility_type,
                "status": status,
                "description": description or f"{facility_type.replace('_', ' ').title()} is {status} at {location}",
                "timestamp": datetime.now().isoformat(),
                "priority": "high" if status in ["unavailable", "needs_repair"] else "medium",
                "votes": random.randint(1, 8),
                "reliability_score": random.uniform(0.85, 0.99),
                "impact_level": random.choice(["low", "medium", "high"])
            }
            
            self.reports_storage["accessibility"].append(report)
            self._update_stats()
            
            return {
                "status": "success",
                "message": "Accessibility report submitted successfully", 
                "report_id": report["report_id"],
                "data": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_recent_reports(self, report_type: str = None, location: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get recent community reports with optional filtering"""
        try:
            all_reports = []
            
            # Collect reports from all types or specific type
            if report_type:
                if report_type in self.reports_storage:
                    all_reports = self.reports_storage[report_type].copy()
                else:
                    return {
                        "status": "error",
                        "error": f"Invalid report type: {report_type}",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                # Combine all report types
                for reports_list in self.reports_storage.values():
                    all_reports.extend(reports_list)
            
            # Filter by location if specified
            if location:
                all_reports = [
                    report for report in all_reports 
                    if location.lower() in report.get("location", "").lower()
                ]
            
            # Sort by timestamp (most recent first) and limit
            all_reports.sort(key=lambda x: x["timestamp"], reverse=True)
            limited_reports = all_reports[:limit]
            
            return {
                "status": "success",
                "data": limited_reports,
                "total_count": len(all_reports),
                "returned_count": len(limited_reports),
                "filters_applied": {
                    "report_type": report_type,
                    "location": location,
                    "limit": limit
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_community_stats(self) -> Dict[str, Any]:
        """Get community contribution statistics"""
        try:
            # Calculate real-time stats
            total_reports = sum(len(reports) for reports in self.reports_storage.values())
            
            # Mock some additional stats
            stats = {
                "total_reports": total_reports,
                "reports_by_type": {
                    report_type: len(reports) 
                    for report_type, reports in self.reports_storage.items()
                },
                "active_contributors": random.randint(150, 500),
                "reports_today": random.randint(20, 80),
                "reports_this_week": random.randint(100, 400),
                "top_locations": [
                    {"location": "Colombo", "report_count": random.randint(50, 120)},
                    {"location": "Kandy", "report_count": random.randint(30, 80)},
                    {"location": "Galle", "report_count": random.randint(20, 60)},
                    {"location": "Anuradhapura", "report_count": random.randint(15, 45)}
                ],
                "average_response_time": f"{random.randint(2, 8)} minutes",
                "reliability_score": random.uniform(0.85, 0.95),
                "community_engagement": "High"
            }
            
            return {
                "status": "success",
                "data": stats,
                "timestamp": datetime.now().isoformat(),
                "source": "Community Data Analytics"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _update_stats(self):
        """Update internal statistics"""
        self.stats["total_reports"] = sum(len(reports) for reports in self.reports_storage.values())
        self.stats["reports_today"] += 1

# Initialize global service instance
community_service = CommunityDataService()