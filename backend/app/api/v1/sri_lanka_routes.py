# Sri Lankan Transit Data API Routes for SLAIC 2025
# Implements the data sources specified in the challenge requirements

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.sri_lanka_transit_service import sri_lanka_transit_service
from app.services.multilingual_service import multilingual_service

router = APIRouter()

# Request/Response Models
class GTFSRequest(BaseModel):
    agency: Optional[str] = Field(None, description="Agency ID (SLTB, SLR)")

class RouteMapRequest(BaseModel):
    route_id: Optional[str] = Field(None, description="Specific route ID to get map for")

class FareRequest(BaseModel):
    route: Optional[str] = Field(None, description="Route name")
    bus_type: Optional[str] = Field(None, description="Bus type (normal, semi_luxury, air_conditioned)")

@router.get("/")
async def sri_lanka_transit_root():
    """Sri Lankan Transit Data API root endpoint"""
    return {
        "message": "Sri Lankan Transit Data API for SLAIC 2025",
        "available_endpoints": {
            "railways": "/railways/realtime",
            "bus_timetables": "/bus/timetables", 
            "bus_routes": "/bus/route-maps",
            "bus_fares": "/bus/fares",
            "gtfs": "/gtfs",
            "disruptions": "/disruptions"
        },
        "data_sources": [
            "Sri Lanka Railways Location API",
            "NTC Inter-Provincial Bus Timetables",
            "NTC Inter-Provincial Bus Route Maps", 
            "NTC Inter-Provincial Bus Fares",
            "GTFS Standard"
        ]
    }

@router.get("/railways/realtime")
async def get_realtime_train_data(
    route: Optional[str] = Query(None, description="Filter by route"),
    lang: Optional[str] = Query("en", description="Language code (en, si, ta)")
):
    """
    Sri Lanka Railways Location API - Real-time train GPS data
    As specified in SLAIC 2025 requirements
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = sri_lanka_transit_service.get_railway_realtime_data(route)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bus/timetables")
async def get_bus_timetables(
    route: Optional[str] = Query(None, description="Filter by route"),
    lang: Optional[str] = Query("en", description="Language code (en, si, ta)")
):
    """
    NTC Inter-Provincial Bus Timetables
    As specified in SLAIC 2025 requirements
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = sri_lanka_transit_service.get_bus_timetables(route)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bus/route-maps")
async def get_bus_route_maps(
    route_id: Optional[str] = Query(None, description="Specific route ID"),
    lang: Optional[str] = Query("en", description="Language code (en, si, ta)")
):
    """
    NTC Inter-Provincial Bus Route Maps
    As specified in SLAIC 2025 requirements
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = sri_lanka_transit_service.get_bus_route_maps(route_id)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bus/fares")
async def get_bus_fares(
    route: Optional[str] = Query(None, description="Route name"),
    bus_type: Optional[str] = Query(None, description="Bus type"),
    lang: Optional[str] = Query("en", description="Language code (en, si, ta)")
):
    """
    NTC Inter-Provincial Bus Fares
    As specified in SLAIC 2025 requirements
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = sri_lanka_transit_service.get_bus_fares(route, bus_type)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gtfs")
async def get_gtfs_data(
    agency: Optional[str] = Query(None, description="Agency ID"),
    lang: Optional[str] = Query("en", description="Language code (en, si, ta)")
):
    """
    GTFS Standard data for structuring transport schedules
    As specified in SLAIC 2025 requirements
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = sri_lanka_transit_service.get_gtfs_data(agency)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disruptions")
async def get_live_disruptions(
    lang: Optional[str] = Query("en", description="Language code (en, si, ta)")
):
    """
    Live disruption data for Sri Lankan transit
    """
    try:
        if not multilingual_service.validate_language(lang):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
            
        result = sri_lanka_transit_service.get_live_disruptions()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Apply multilingual translation
        translated_result = multilingual_service.translate_response(result, lang)
        return translated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Get supported languages for multilingual support"""
    return {
        "supported_languages": multilingual_service.get_supported_languages(),
        "default_language": "en",
        "usage": "Add ?lang=si or ?lang=ta to any endpoint for Sinhala or Tamil translations"
    }

@router.get("/health")
async def sri_lanka_transit_health():
    """Health check for Sri Lankan transit data service"""
    return {
        "status": "healthy",
        "service": "Sri Lankan Transit Data API",
        "available": sri_lanka_transit_service.available,
        "multilingual_support": True,
        "supported_languages": list(multilingual_service.get_supported_languages().keys()),
        "data_sources_implemented": [
            "Sri Lanka Railways Location API",
            "NTC Inter-Provincial Bus Timetables", 
            "NTC Inter-Provincial Bus Route Maps",
            "NTC Inter-Provincial Bus Fares",
            "GTFS Standard"
        ]
    }