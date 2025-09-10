# Community Data Reporting API Routes for SLAIC 2025
# Allows users to contribute transit data and report issues

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.services.community_service import community_service
from app.services.multilingual_service import multilingual_service

router = APIRouter()

# Request/Response Models
class TrafficReportRequest(BaseModel):
    location: str = Field(..., description="Location of traffic issue")
    severity: str = Field(..., description="Traffic severity: light, moderate, heavy")
    description: Optional[str] = Field(None, description="Additional details")
    coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")

class DelayReportRequest(BaseModel):
    route: str = Field(..., description="Route name or number")
    mode: str = Field(..., description="Transportation mode: bus, train, tuk-tuk")
    delay_minutes: int = Field(..., description="Delay in minutes")
    location: str = Field(..., description="Current location")
    description: Optional[str] = Field(None, description="Reason for delay")

class FareUpdateRequest(BaseModel):
    route: str = Field(..., description="Route name")
    mode: str = Field(..., description="Transportation mode")
    fare_amount: float = Field(..., description="Current fare amount in LKR")
    effective_date: Optional[str] = Field(None, description="When fare change took effect")
    source: Optional[str] = Field("community", description="Source of information")

class AccessibilityReportRequest(BaseModel):
    location: str = Field(..., description="Location or stop name")
    facility_type: str = Field(..., description="Type: wheelchair_access, audio_assistance, etc.")
    status: str = Field(..., description="Status: available, unavailable, needs_repair")
    description: Optional[str] = Field(None, description="Additional details")

@router.get("/")
async def community_data_root():
    """Community Data Reporting API root endpoint"""
    return {
        "message": "Community Data Reporting API for SLAIC 2025",
        "description": "Crowdsourced transit data from Sri Lankan commuters",
        "available_endpoints": {
            "report_traffic": "POST /traffic - Report traffic conditions",
            "report_delay": "POST /delays - Report transit delays",
            "update_fare": "POST /fares - Report fare changes",
            "report_accessibility": "POST /accessibility - Report accessibility issues",
            "get_reports": "GET /reports - View recent reports"
        },
        "features": [
            "Real-time traffic reporting",
            "Transit delay notifications",
            "Community fare updates",
            "Accessibility status reporting",
            "Multilingual support (en, si, ta)"
        ]
    }

@router.post("/traffic")
async def report_traffic(
    report: TrafficReportRequest,
    lang: Optional[str] = "en"
):
    """
    Report traffic conditions at specific locations
    Community-contributed real-time traffic data
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = await community_service.submit_traffic_report(
            location=report.location,
            severity=report.severity,
            description=report.description,
            coordinates=report.coordinates
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delays")
async def report_delay(
    report: DelayReportRequest,
    lang: Optional[str] = "en"
):
    """
    Report transit delays (bus, train, tuk-tuk)
    Community-contributed delay information
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = await community_service.submit_delay_report(
            route=report.route,
            mode=report.mode,
            delay_minutes=report.delay_minutes,
            location=report.location,
            description=report.description
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fares")
async def update_fare(
    update: FareUpdateRequest,
    lang: Optional[str] = "en"
):
    """
    Report fare changes for different routes and modes
    Community-contributed fare information
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = await community_service.submit_fare_update(
            route=update.route,
            mode=update.mode,
            fare_amount=update.fare_amount,
            effective_date=update.effective_date,
            source=update.source
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accessibility")
async def report_accessibility(
    report: AccessibilityReportRequest,
    lang: Optional[str] = "en"
):
    """
    Report accessibility status of transit facilities
    Community-contributed accessibility information
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = await community_service.submit_accessibility_report(
            location=report.location,
            facility_type=report.facility_type,
            status=report.status,
            description=report.description
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_community_reports(
    report_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50,
    lang: Optional[str] = "en"
):
    """
    Get recent community reports
    Filter by type (traffic, delays, fares, accessibility) or location
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = await community_service.get_recent_reports(
            report_type=report_type,
            location=location,
            limit=limit
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_community_stats(lang: Optional[str] = "en"):
    """Get community contribution statistics"""
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = await community_service.get_community_stats()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation  
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def community_service_health():
    """Health check for community data service"""
    return {
        "status": "healthy",
        "service": "Community Data Reporting API",
        "available": community_service.available,
        "multilingual_support": True,
        "supported_languages": list(multilingual_service.get_supported_languages().keys()),
        "report_types": ["traffic", "delays", "fares", "accessibility"],
        "features": [
            "Real-time crowdsourced data",
            "Multi-modal transit reporting", 
            "Accessibility information",
            "Community statistics"
        ]
    }